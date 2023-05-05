#!/bin/bash
sudo service bluetooth stop
sudo /usr/libexec/bluetooth/bluetoothd -P input &
