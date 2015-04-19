#!/usr/bin/env python
import argparse
import subprocess
import urllib2
import getpass
import time
import sys

rmmod    = "rmmod"
modprobe = "modprobe"
device   = False
host     = False
base_url = False
usbip    = "/home/geoff/src/linux-3.19.3/tools/usb/usbip/src/usbip"
port     = "5000"


def call(cmd):
    print cmd
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)

def request(url):
    requested = False
    while not requested:
        try:
            data = urllib2.urlopen(url, None, 1)
            message = data.read()
            if data.getcode() == 200:
                requested = True
                print("*** succeeded! " + message + "***")
            else:
                print("error requesting: " + message)
        except:
            sys.stdout.write(".")
            sys.stdout.flush()
        
        if not requested:
            time.sleep(1)
    

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
    setup()
    print "connecting remote device"
    request(base_url + "/attach")
    print "connecting local device"
    print call([usbip, "attach",  "-r",  host, "-b", device])

def unplug():
    setup()
    print "disconnecting local device"
    print call([rmmod, "vhci_hcd"])
    print call([rmmod, "usbip-core"])
    print "disconnecting remote device"
    request(base_url + "/detach")

def main():
    parser = argparse.ArgumentParser(description="plug/unplug usbip device")
    parser.add_argument("--plug", dest="plug", action="store_true", 
                        default=False,
                        help="connect to device")
    parser.add_argument("--unplug", dest="unplug", action="store_true", 
                        default=False,
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


try:
    main()
except subprocess.CalledProcessError as error:
    print error.cmd
    print error.output
