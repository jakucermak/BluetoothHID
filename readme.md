was an experiment to turn a Raspberry Pi into a Human Interface Device (HID).

I followed the instructions at the following location to get me started:
http://yetanotherpointlesstechblog.blogspot.com/2016/04/emulating-bluetooth-keyboard-with.html

I wanted to move to Python3 and tidy things up on the Bluetooth side to bring it in to line with current ways things are done in BlueZ.

## Configure Raspberry Pi.
These instructions assuming you have BlueZ 5.43 installed. You can check this with:
```
$ bluetoothctl -v
5.43
```

Ensure Raspberry Pi is at the latest version:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
```

Check that the packages required for this are installed
```
sudo apt-get install python3-dbus
sudo pip install evdev
```

Here is an outline of things I changed:
## Moved to Python3
I wanted to do this because not only is it a good thing to do but it also allowed some of the dependancies to be removed. After Python 3.3 Bluetooth sockets are supported in the native Python installs. The downside to this is that there are clear distinctions between str and bytes in the code. For me, this broke the keyboard client. This is what required the biggest re-write to get Python3 working.

## Reconfigure the Bluetooth Daemon
The instructions worked that were provided but things have moved on a little bit. To stop the Bluetooth daemon running then the following command is preferred:
```
sudo service bluetooth stop
```

The `input` Bluetooth plugin needs to be removed so that it does not grab the sockets we require access to. As the original author says the way this was documented could be improved. If you want to restart the daemon (without the input plugin) from the command line then the following would seem the preferred:
```
sudo /usr/lib/bluetooth/bluetoothd -P input
```

If you want to make this the default for this Raspberry Pi then modify the `/lib/systemd/system/bluetooth.service` file. You will need to change the Service line from:
```
ExecStart=/usr/lib/bluetooth/bluetoothd
```
to
```
ExecStart=/usr/lib/bluetooth/bluetoothd -P input
```

## Configure D-Bus
When a new service is created on the D-Bus, this service needs to be configured.
```
sudo cp org.yaptb.btkbservice.conf /etc/dbus-1/system.d
```

## Event loop
The original article used Gtk for the event loop. I changed it to the library that I normally use and this removed the warning the original author was getting.

## hciconfig
This command has been deprecated in the BlueZ project.
https://wiki.archlinux.org/index.php/bluetooth#Deprecated_BlueZ_tools

In the setup of the original article the `hciconfig` command used to get the BD address. I have modified this so that the code queries the adapter and gets the address.

There were also `os.system` calls to `hciconfig` from within the Python. With the new BlueZ D-Bus interface these are unnecessary and have been replaced with D-Bus calls.

## Sockets
Moving to a new version (> 3.3?) of Python will not require the `import bluetooth` line that was there previously.
More information on the Python socket support of Bluetooth is available at:
https://docs.python.org/3.4/library/socket.html#socket-families

## Registering of Profile
As the original author noted, the registering of the HID profile does not seem to work as documented at:
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
The `NewConnection` method did not seem to get called on a new connection being made. Requests to the BlueZ mailing list did not seem to yield any insight as to why this is.

## Pairing
With the settings used in this setup the pairing steps described in the original tutorial should not be required. While this is probably not a sensible choice for a real situation, for this experiment I chose convenience over security.

Below is a transcript from the two terminal I had open for this experiment.

### Terminal 1
```
pi@raspberrypi:~/python/bluetooth_hid/btkeyboard/server $ sudo service bluetooth stop
pi@raspberrypi:~/python/bluetooth_hid/btkeyboard/server $ sudo /usr/lib/bluetooth/bluetoothd -P input &
pi@raspberrypi:~/python/bluetooth_hid/btkeyboard/server $ sudo python3 btk_server.py
Setting up service
Setting up BT device
Configuring for name BT_HID_Keyboard
Configuring Bluez Profile
Reading service record
Profile registered
Waiting for connections
```
Scan for the keyboard Pi and connect from main computer
```
8C:2D:AA:44:0E:3A connected on the control socket
8C:2D:AA:44:0E:3A connected on the interrupt channel
```

### Terminal 2
```
pi@raspberrypi:~/python/bluetooth_hid/btkeyboard/keyboard $ python3 kb_client.py
Setting up keyboard
found a keyboard
starting event loop
Listening...
```

