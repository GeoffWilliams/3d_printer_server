from flask import Flask
from flask import jsonify
import subprocess

app         = Flask(__name__)
usbip       = "/usr/bin/usbip"
usbipd      = "/usr/bin/usbipd"
modprobe    = "/sbin/modprobe"
reboot      = "/sbin/reboot"
pidfile     = "/var/run/usbipd.pid"

def call(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)


@app.before_first_request
def setup():
    call([modprobe, "usbip-core"])
    call([modprobe, "usbip-host"])
    process = subprocess.Popen(usbipd + "-d")
    open(pidfile, 'w').write(str(process.pid)).close()


def shutdown():
    pid = int(open(pidfile).read())
    os.kill(pid, signal.SIGKILL)
   
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
    print(call([usbip, "list", " -l"]))

@app.route("/attach")
def attach():
    print(call([usbip, "bind", "-b", "$(cat conf/device)"]))

@app.route("/detach")
def detach():
    print(call([usbip, "unbind", "-b", "$(cat conf/device)"]))

@app.route("/reboot")
def reboot():
    print(call([reboot]))

@app.route("/status")
def status():
    print(call([usbip, "list", "--remote", "localhost"]))

@app.errorhandler(subprocess.CalledProcessError)
def handle_invalid_usage(error):
    response = jsonify(
        output=error.output,
        returncode=error.returncode)
    return response

@app.errorhandler(500)
def internal_error(error):
    return "error: " + str(error)

if __name__ == "__main__":
    app.run()
