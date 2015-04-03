#!/usr/bin/env python
import argparse
import subprocess
import urllib2
import getpass

modprobe = "modprobe"
device   = False
host     = False
base_url = False
usbip    = "/home/geoff/src/linux-3.13/drivers/staging/usbip/userspace/src/usbip"
port     = "5000"


def call(cmd):
    print cmd
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)

def setup():
    global device, host, base_url
    load_modules()
    device   = open("./conf/device").read().strip()
    host     = open("./conf/host").read().strip()
    base_url = "http://" + host + ":" + port

    print "using :" + base_url


def load_modules():
    call([modprobe, "vhci-hcd"])
    call([modprobe, "usbip-core"])
 
def plug():
    print usbip 
    setup()
    print "connecting remote device"
    print urllib2.urlopen(base_url + "/attach").read()
    print "connecting local device"
    print call([usbip, "attach",  "-r",  host, "-b", device])

def unplug():
    print "disconnecting local device"
    print call([usbip, "detach", "-r", host, "-b", device])
    print "disconnecting remote device"
    print urllib2.urlopen(base_url + "/detach").read()


parser = argparse.ArgumentParser(description="plug/unplug usbip device")
parser.add_argument("--plug", dest="plug", action="store_true", default=False,
                    help="connect to device")
parser.add_argument("--unplug", dest="unplug", action="store_true", default=False,
                    help="disconnect from device")
args = parser.parse_args()


if getpass.getuser() == "root":
    if args.unplug and args.plug:
        parser.print_help()
    elif args.unplug:
        print "unplugging device..."
        unplug()
    elif args.plug:
        print "plugging in device..."
        plug()
    else: 
        parser.print_help()
else:
    print("must be run as root for now!")
