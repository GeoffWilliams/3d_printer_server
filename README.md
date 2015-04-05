#3D Printer Server

## What's this?
It's a 3D printer server to allow a remote USB connection to 3D printers that
only work under windows, eg the the [UP! mini](http://www.pp3dp.com/index.php?page=shop.product_details&flypage=flypage.tpl&product_id=6&option=com_virtuemart&Itemid=37&vmcchk=1&Itemid=37).

I really like this little printer but dragging a laptop over to it and plugging
it in is a bit of a drag so I wrote this quick python program to connect it 
over the network using a Windows machine running in VirtualBox.

The server is designed to run on a [Rasberry PI](http://www.raspberrypi.org/) 
which is then plugged into the printer and connected to the LAN.

## Features
* Uses USBIP to make USB port accessible over network
* Webcam video streaming (so you can watch your print!)
* Webcam image capture 

## How stable is it?
Not stable at all :D

## How secure is it?
Note secure at all(!).  Daemons and client code run as `root` to gain access
to the `usbip` system -- at least for the moment.

## Isn't that really bad?
Kinda.  USBIP is for trusted environments only and so is the server software.
This may be fixed in the future, or it may not.

## OK how do I use this?

### Server
1. get a raspberry PI and install rasbian on it
2. make it accessible over the network
3. install usbip by obtaining the kernel source from git and compiling the
   usbip userspace driver.  DO NOT use the usbip package available via apt-get
   it needs to match the running kernel!
4. checkout this code onto your Rasberry PI somewhere
5. plug-in the 3D printer and webcam
6. install required libraries:
```
sudo apt-get install python-imaging python-pygame python-flask
```
7. add a line to /etc/rc.local that looks something like
```
python /path/to/code/3d_printer_server/app.py > /var/log/usbip.log 2>&1 &
```
8. edit ./conf/device to be the bus id of the printer device `usbip list -l`
   to lookup your devices
9. start the daemon
```
sudo /path/to/code/3d_printer_server/app.py
```
10. type the IP of your Rasberry PI into a browser and head to port 5000
11. if it doesn't work, look in the logfile above and also usbipd.log

### Client
The client code is configured to connect to the host listed in `./conf/host` 
on port 5000 and will also read the device name from the `./conf/device` file
To setup client:
1. checkout the code somewhere
2. install usbip - on ubuntu/debian its in the `linux-tools-generic` package.
   Remove the `usbip` package if it exists!
3. fix the path to usbip in client.pp (nasty hack for moment)
4. check correct hostname and device in `./conf/host` and `./conf/device`
5. try and connect
```
sudo ./client.py --plug
```
6. if this works, start virtual box and righ click the usb icon in the bottom
   right corner, then select your printer.  Windows should detect the printer
   and you can send it a test job
7. Check the progress of your print using the cool webcam feed feature :)

## Can I get help with this?
I'd love to buy my free time is very limited.  This is experimental software
at the moment and probably won't work out of the box.  Feel free to open github issues though

## Can I use it/contribue?
Sure!  This is GPL licenced code, if you'd like to collaborate please drop me
an email:  Geoff Williams <geoffREMOVE_NOSPAM@geoffwilliams.me.uk>
