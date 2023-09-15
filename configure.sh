#!/bin/bash

#############################
### Pre Run Configuration ###
#############################

# confirure bluetooth service
sudo service bluetooth stop
sudo /usr/libexec/bluetooth/bluetoothd -P input &

if ! [[ -d "/var/log/hid" ]]; then
	echo "Creating log folder in /var/log/hid"
	# create log folder in /var/log/hid
	sudo mkdir /var/log/hid
	# change its permission to write
	sudo chmod a+w /var/log/hid
fi

echo "Now waiting 5sec to Configuration is done, starting server will continue afterwards."
for (( i = 1; i <= 5; i++ )); do
	sleep 1
	echo "waiting ${i} seconds"
done

#############################
###         Run           ###
#############################

# Run server
sudo python3 server.py &