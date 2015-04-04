from flask import Flask
from flask import jsonify
import subprocess
import getpass
import os
import signal

app         = Flask(__name__)
usbip       = "usbip"
usbipd      = "usbipd"
modprobe    = "/sbin/modprobe"
reboot      = "/sbin/reboot"
pidfile     = "/var/run/usbipd.pid"
basedir     = os.path.dirname(os.path.realpath(__file__))

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
    print("loading...")
    load_module("usbip-core")
    load_module("usbip-host")    
    print("starting daemon..")
    process = subprocess.Popen([usbipd, "-D"])
    open(pidfile, 'w').write(str(process.pid))
    Settings.device_id = open(basedir + "/conf/device").read().strip()
    print(Settings.device_id)
    print("....done!")

def shutdown():
    print("shutting down...")
    pid = int(open(pidfile).read())
    os.kill(pid, signal.SIGKILL)
    print("...done!")   

@app.route("/")
def index():
    return """
<h1>3D Printer Server</h1>
<a href="/list">List connected USB devices</a><br/>
<a href="/attach">Attach default device</a><br/>
<a href="/detach">Detach default device</a><br/>
<a href="/status">Display status</a><br/>
<a href="/reboot">Reboot system</a><br/>
"""

@app.route("/list")
def list():
    return call([usbip, "list", "-l"])

@app.route("/attach")
def attach():
    return call([usbip, "bind", "-b", Settings.device_id])

@app.route("/detach")
def detach():
    return call([usbip, "unbind", "-b", Settings.device_id])

@app.route("/reboot")
def reboot():
    return call([reboot])

@app.route("/status")
def status():
    return call([usbip, "list", "--remote", "localhost"])

@app.route("/device")
def device():
    return "selected device: " + Settings.device_id

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
