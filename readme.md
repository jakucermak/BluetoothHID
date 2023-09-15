was an experiment to turn a Raspberry Pi into a Human Interface Device (HID).

I followed the instructions at the following location to get me started:
http://yetanotherpointlesstechblog.blogspot.com/2016/04/emulating-bluetooth-keyboard-with.html

I wanted to move to Python3 and tidy things up on the Bluetooth side to bring it in to line with current ways things are
done in BlueZ.

## Configure Raspberry Pi.

These instructions assuming you have BlueZ 5.43 installed. You can check this with:

```
$ bluetoothctl -v
5.43
```

Ensure Raspberry Pi is at the latest version:

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
```

Check that the packages required for this are installed

```
sudo apt-get install python3-dbus
sudo pip install -r requirements.txt
```

## Reconfigure the Bluetooth Daemon

The instructions worked that were provided but things have moved on a little bit. To stop the Bluetooth daemon running
then the following command is preferred:

```
sudo service bluetooth stop
```

The `input` Bluetooth plugin needs to be removed so that it does not grab the sockets we require access to. As the
original author says the way this was documented could be improved. If you want to restart the daemon (without the input
plugin) from the command line then the following would seem the preferred:

```
sudo /usr/libexec/bluetooth/bluetoothd -P input
```

If you want to make this the default for this Raspberry Pi then modify the `/lib/systemd/system/bluetooth.service` file.
You will need to change the Service line from:

```
ExecStart=/usr/libexec/bluetooth/bluetoothd
```

to

```
ExecStart=/usr/libexec/bluetooth/bluetoothd -P input
```

## Configure D-Bus

When a new service is created on the D-Bus, this service needs to be configured.

```
sudo cp org.jc.btkbservice.conf /etc/dbus-1/system.d
```

## Registering of Profile

As the original author noted, the registering of the HID profile does not seem to work as documented at:
https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/profile-api.txt
The `NewConnection` method did not seem to get called on a new connection being made. Requests to the BlueZ mailing list
did not seem to yield any insight as to why this is.


## Running in Docker Container

For Direct access the bluetooth service needs to be stopped.
To this run following in the hosts terminal:
```
pi@raspberrypi:~$ sudo killall -9 bluetoothd
```

Build docker image
```
pi@raspberrypi:~/BLuetoothHID $ docker build -t <whatever_image_name> . 
```

Running our container with mounted dbus volume, with detached interactive shell 
```
pi@raspberrypi:~/BLuetoothHID $ docker run -v /var/run/dbus:/var/run/dbus --net=host --cap-add=NET_ADMIN -it <our_whatever_image_name>
```

### TODO

- [x] Unify file and service names (as mentioned at the beginning of mouse client and keyboard client)
- [x] ***INVESTIGATE***: OSError: [Errno 98] Address already in use #1
- [ ] add catch of wrongly configurated YAML files

