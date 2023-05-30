#!/bin/bash
# start services
sudo service dbus start
sudo service bluetooth start

# wait for startup of services
msg="Waiting for services to start..."
time=0
echo -n $msg
while [[ "$(pidof start-stop-daemon)" != "" ]]; do
    sleep 1
    time=$((time + 1))
    echo -en "\r$msg $time s"
done
echo -e "\r$msg done! (in $time s)"

sudo service bluetooth stop
sudo /usr/libexec/bluetooth/bluetoothd -P input &

if ! [[ -d "/var/log/hid" ]]; then
    echo "Creating log folder in /var/log/hid"
    # create log folder in /var/log/hid
    sudo mkdir /var/log/hid
    # change its permission to write
    sudo chmod a+w /var/log/hid
fi

#############################
###         Run           ###
#############################

# Run server
sudo python3 server.py 