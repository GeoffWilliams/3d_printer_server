from flask import Flask
from flask import jsonify
from flask import send_file
from flask import Response
from StringIO import StringIO
from PIL import Image
import subprocess
import getpass
import os
import signal
import sys
import pygame.camera
import pygame.image
from time import sleep

app         = Flask(__name__)
cam         = None
video_size  = (640,480)
usbip       = "usbip"
usbipd      = "usbipd"
modprobe    = "/sbin/modprobe"
reboot      = "/sbin/reboot"
pidfile     = "/var/run/usbipd.pid"
usbipd_log  = "/var/log/usbipd.log"
photo       = "/tmp/photo.bmp"
basedir     = os.path.dirname(os.path.realpath(__file__))
os.environ["PATH"] += os.pathsep + "/sbin/"
os.environ["PATH"] += os.pathsep + "/bin"
os.environ["PATH"] += os.pathsep + "/usr/bin"
os.environ["PATH"] += os.pathsep + "/usr/local/sbin"

class Settings(Flask):
    device_id   = False

def call(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)

def load_module(name):
    try:
        call([modprobe, name])
    except subprocess.CalledProcessError as error:
	print("error loading kernel module %(output)s" % error.output)
        

def setup():
    global cam
    print("loading...")
    load_module("usbip-core")

    load_module("usbip-host")    
    print("starting daemon..")
    os.system(usbipd + " --debug --pid " + pidfile + " > " + usbipd_log + " 2>&1 &")
    Settings.device_id = open(basedir + "/conf/device").read().strip()
    print(Settings.device_id)

    # setup webcam
    pygame.camera.init()
    cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
    cam.start()

    print("....done!")

def shutdown():
    print("shutting down...")
    try:
        # webcam off
        cam.stop()
        pygame.camera.quit()

        # usbipd kill
        pid = int(open(pidfile).read())
        os.kill(pid, signal.SIGKILL)
        os.remove(pidfile)

    except:
        print("no pid file or couldn't kill")
    print("...done!")   

@app.route("/")
def index():
    return """
<h1>3D Printer Server</h1>
<a href="/list">List connected USB devices</a><br/>
<a href="/attach">Attach default device</a><br/>
<a href="/detach">Detach default device</a><br/>
<a href="/status">Display status</a><br/>
<a href="/log">Display log</a><br/>
<a href="/camera">Webcam photo</a><br/>
<a href="/static/watch.html">Watch webcam</a></br>
<a href="/video">Webcam video</a><br/>
<hr/>
<a href="/reboot">Reboot system</a><br/>
"""

@app.route("/list")
def list():
    return call([usbip, "list", "-l"])

@app.route("/attach")
def attach():
    return call([usbip, "--debug", "bind", "-b", Settings.device_id])

@app.route("/detach")
def detach():
    return call([usbip, "--debug", "unbind", "-b", Settings.device_id])

@app.route("/reboot")
def reboot():
    os.system("reboot")
    #return call([reboot])

@app.route("/status")
def status():
    return call([usbip, "list", "--remote", "localhost"])

@app.route("/device")
def device():
    return "selected device: " + Settings.device_id

@app.route("/log")
def log():
    file = open(usbipd_log)
    return file.read()

@app.route("/camera")
def camera():
    img = cam.get_image()
    pygame.image.save(img, photo)
    return send_file(photo, "image/bmp")

@app.route("/video")
def video():
    def generate():
        surface = pygame.Surface(video_size)
        while True:
            if cam.query_image():
                cam.get_image(surface)
                data = pygame.image.tostring(surface, "RGBA")
                img = Image.fromstring("RGBA", video_size, data)
                zdata = StringIO()
                img.save(zdata, "JPEG")
                frame = zdata.getvalue()
                # must allow other processes to run
                sleep(0.1) 

                yield ( b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.errorhandler(subprocess.CalledProcessError)
def handle_invalid_usage(error):
    response = jsonify(
        output=error.output,
        cmd=error.cmd,
        returncode=error.returncode)
    return response

@app.errorhandler(500)
def internal_error(error):
    response = jsonify(
        returncode=500,
        message=str(error))
    return response

if __name__ == "__main__":
    if getpass.getuser() == "root":
        setup()
        app.run(host= '0.0.0.0')
        shutdown()
    else:
        print "Server must be run as root for now!"
