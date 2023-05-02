#!/usr/bin/python3
"""
Bluetooth HID keyboard emulator DBUS Service
Original idea taken from:
https://yetanotherpointlesstechblog.blogspot.com/2016/04/emulating-bluetooth-keyboard-with.html
Moved to Python 3 and tested with BlueZ 5.43
"""
import os
import sys
import time

import dbus
import dbus.service
import socket

from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

import xml.etree.ElementTree as ET
from utils.logger import Logger, LogLevels


logger = Logger("hid")

class HumanInterfaceDeviceProfile(dbus.service.Object):
    """
    BlueZ D-Bus Profile for HID
    """
    fd = -1

    @dbus.service.method('org.bluez.Profile1',
                         in_signature='', out_signature='')
    def Release(self):
        print('Release')
        mainloop.quit()

    @dbus.service.method('org.bluez.Profile1',
                         in_signature='oha{sv}', out_signature='')
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print('NewConnection({}, {})'.format(path, self.fd))
        for key in properties.keys():
            if key == 'Version' or key == 'Features':
                print('  {} = 0x{:04x}'.format(key,
                                               properties[key]))
            else:
                print('  {} = {}'.format(key, properties[key]))

    @dbus.service.method('org.bluez.Profile1',
                         in_signature='o', out_signature='')
    def RequestDisconnection(self, path):
        print('RequestDisconnection {}'.format(path))

        if self.fd > 0:
            os.close(self.fd)
            self.fd = -1


class BTKbDevice:
    """
    create a bluetooth device to emulate a HID keyboard
    """
    MY_DEV_NAME = 'BT_HID'
    # Service port - must match port configured in SDP record
    P_CTRL = 17
    # Service port - must match port configured in SDP record#Interrrupt port
    P_INTR = 19
    # BlueZ dbus
    PROFILE_DBUS_PATH = '/bluez/jc/btkb_profile'
    ADAPTER_IFACE = 'org.bluez.Adapter1'
    DEVICE_INTERFACE = 'org.bluez.Device1'
    DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
    DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'

    # file path of the sdp record to load
    install_dir = os.path.dirname(os.path.realpath(__file__))
    SDP_RECORD_PATH = os.path.join(install_dir,
                                   'bt_config/sdp_record.xml')
    # UUID for HID service (1124)
    # https://www.bluetooth.com/specifications/assigned-numbers/service-discovery
    UUID = '00001124-0000-1000-8000-00805f9b34fb'

    def __init__(self, hci=0):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the Bluetooth device and configures it for use as a keyboard.


    :param self: Represent the instance of the class
    :param hci: Specify which bluetooth device to use
    :return: Nothing
    :doc-author: Jakub Cermak
    """
        self.scontrol = None
        self.ccontrol = None  # Socket object for control
        self.sinterrupt = None
        self.cinterrupt = None  # Socket object for interrupt
        self.dev_path = '/org/bluez/hci{}'.format(hci)
        logger.log('Setting up BT device',LogLevels.INFO)
        self.bus = dbus.SystemBus()
        self.adapter_methods = dbus.Interface(
            self.bus.get_object('org.bluez', self.dev_path), self.ADAPTER_IFACE)
        self.adapter_property = dbus.Interface(
            self.bus.get_object('org.bluez', self.dev_path), self.DBUS_PROP_IFACE)

        self.bus.add_signal_receiver(self.interfaces_added,
                                     dbus_interface=self.DBUS_OM_IFACE,
                                     signal_name='InterfacesAdded')

        self.bus.add_signal_receiver(self._properties_changed,
                                     dbus_interface=self.DBUS_PROP_IFACE,
                                     signal_name='PropertiesChanged',
                                     arg0=self.DEVICE_INTERFACE,
                                     path_keyword='path')

        logger.log('Configuring for name {}'.format(BTKbDevice.MY_DEV_NAME),LogLevels.INFO)
        self.config_hid_profile()

        # set the Bluetooth device configuration
        self.alias = BTKbDevice.MY_DEV_NAME
        self.discoverable_timeout = 0
        self.discoverable = True

    def interfaces_added(self, path, device_info):
        pass

    def _properties_changed(self, interface, changed, invalidated, path):
        """
    The _properties_changed function is a callback function that gets called whenever the
    properties of an object change. In this case, we are interested in the Connected property
    of our device. If it changes to False, then we know that our device has disconnected, and
    we can call on_disconnect().

    :param self: Access the object itself, and is used to call other functions within the class
    :param interface: Specify which interface the signal is coming from
    :param changed: Determine if the device is connected or not
    :param invalidated: Check if the properties have been invalidated
    :param path: Specify the path of the object that has changed
    :return: The value of the connected property
    :doc-author: Jakub Cermak
    """
        if self.on_disconnect is not None:
            if 'Connected' in changed:
                if not changed['Connected']:
                    self.on_disconnect()

    def on_disconnect(self):
        """
    The on_disconnect function is called when the client disconnects from the server.
    It prints a message to let you know that it has disconnected and then calls listen()
    to wait for another connection.

    :param self: Represent the instance of the class
    :return: The client has been disconnected
    :doc-author: Jakub Cermak
    """
        logger.log('The client has been disconnect', LogLevels.INFO)
        self.listen()

    @property
    def address(self):
        """
    The address function returns the MAC address of the adapter.
    The function uses dbus to get the property 'Address' from interface
    self.ADAPTER_IFACE, which is a string representing a MAC address.

    :param self: Refer to the object itself
    :return: The adapter mac address
    :doc-author: Jakub Cermak
    """
        return self.adapter_property.Get(self.ADAPTER_IFACE, 'Address')

    @property
    def powered(self):
        """
    The powered function returns the current state of the adapter.
        :returns: True if powered, False otherwise.

    :param self: Represent the instance of the class
    :return: A boolean value
    :doc-author: Jakub Cermak
    """
        return self.adapter_property.Get(self.ADAPTER_IFACE, 'Powered')

    @powered.setter
    def powered(self, new_state):
        """
    The powered function sets the adapter's Powered property to new_state.

    :param self: Represent the instance of the class
    :param new_state: Set the powered state of the adapter
    :return: The new state of the adapter
    :doc-author: Jakub Cermak
    """
        self.adapter_property.Set(self.ADAPTER_IFACE, 'Powered', new_state)

    @property
    def alias(self):

        """
    The alias function returns the alias of the adapter.

    :param self: Represent the instance of the class
    :return: The alias of the adapter
    :doc-author: Jakub Cermak
    """
        return self.adapter_property.Get(self.ADAPTER_IFACE, 'Alias')

    @alias.setter
    def alias(self, new_alias):

        """
    The alias function sets the alias of the adapter to a new value.

    :param self: Represent the instance of the class
    :param new_alias: Set the new alias for the adapter
    :return: The alias of the adapter
    :doc-author: Jakub Cermak
    """
        self.adapter_property.Set(self.ADAPTER_IFACE, 'Alias', new_alias)

    @property
    def discoverable_timeout(self):
        """
    The discoverable timeout function returns the timeout value of the adapter.

    :param self: Represent the instance of the class
    :return: The timeout value in seconds that the local adapter is discoverable
    :doc-author: Jakub Cermak
    """
        return self.adapter_props.Get(self.ADAPTER_IFACE, 'DiscoverableTimeout')

    @discoverable_timeout.setter
    def discoverable_timeout(self, new_timeout):
        self.adapter_property.Set(self.ADAPTER_IFACE,
                                  'DiscoverableTimeout',
                                  dbus.UInt32(new_timeout))

    @property
    def discoverable(self):
        """
    The discoverable function is a getter function that returns the discoverable state of the adapter.
    The discoverable state is a boolean value that indicates whether the adapter can be discovered by other devices.

    :param self: Refer to the object itself
    :return: The boolean value of the discoverable property
    :doc-author: Jakub Cermak
    """
        return self.adapter_props.Get(self.ADAPTER_INTERFACE, 'Discoverable')

    @discoverable.setter
    def discoverable(self, new_state):

        """
    The discoverable function sets the discoverable state of the adapter.

    :param self: Represent the instance of the class
    :param new_state: Set the value of discoverable property
    :return: The state of the adapter
    :doc-author: Jakub Cermak
    """
        self.adapter_property.Set(self.ADAPTER_IFACE, 'Discoverable', new_state)

    def config_hid_profile(self):

        """
    The config_hid_profile function is used to configure the Bluez Profile.
    The service record is read from the SDP Service Record file and then options are set for the profile.
    The manager interface is created and then a Human Interface Device Profile object is created with
    the bus, path, and UUID as parameters. The profile manager registers this new profile.

    :param self: Represent the instance of the class
    :return: The profile manager and the human interface device profile
    :doc-author: Jakub Cermak
    """
        logger.log('Configuring Bluez Profile', LogLevels.INFO)
        service_record = self.read_sdp_service_record()

        opts = {
            'Role': 'server',
            'RequireAuthentication': False,
            'RequireAuthorization': False,
            'AutoConnect': True,
            'ServiceRecord': service_record,
        }

        manager = dbus.Interface(self.bus.get_object('org.bluez', '/org/bluez'),
                                 'org.bluez.ProfileManager1')

        HumanInterfaceDeviceProfile(self.bus, BTKbDevice.PROFILE_DBUS_PATH)

        manager.RegisterProfile(BTKbDevice.PROFILE_DBUS_PATH, BTKbDevice.UUID, opts)

        logger.log('Profile registered', LogLevels.INFO)

    @staticmethod
    def read_sdp_service_record():

        """
    The read_sdp_service_record function reads the SDP record from a file and returns it as a string.
    The function is called by the __init__ method of BTKbDevice class.

    :return: The contents of the sdp record
    :doc-author: Jakub Cermak
    """

        logger.log('Reading service record', LogLevels.INFO)
        try:
            fh = open(BTKbDevice.SDP_RECORD_PATH, 'r')
        except OSError:
            sys.exit('Could not open the sdp record. Exiting...')

        return fh.read()

    def listen(self):
        """
    The listen function is used to listen for incoming connections.
    It will wait until a connection is made and then return the socket object
    and address of the client that connected. The function takes one argument:

    :param self: Represent the instance of the class
    :return: The control and interrupt sockets
    :doc-author: Jakub Cermak
    """
        logger.log('Waiting for connections', LogLevels.INFO)
        self.scontrol = socket.socket(socket.AF_BLUETOOTH,
                                      socket.SOCK_SEQPACKET,
                                      socket.BTPROTO_L2CAP)
        self.scontrol.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sinterrupt = socket.socket(socket.AF_BLUETOOTH,
                                        socket.SOCK_SEQPACKET,
                                        socket.BTPROTO_L2CAP)
        self.sinterrupt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.scontrol.bind((self.address, self.P_CTRL))
        self.sinterrupt.bind((self.address, self.P_INTR))

        # Start listening on the server sockets
        self.scontrol.listen(1)  # Limit of 1 connection
        self.sinterrupt.listen(1)

        self.ccontrol, cinfo = self.scontrol.accept()
        logger.log('{} connected on the control socket'.format(cinfo[0]), LogLevels.INFO)

        self.cinterrupt, cinfo = self.sinterrupt.accept()
        logger.log('{} connected on the interrupt channel'.format(cinfo[0]), LogLevels.INFO)

    def send(self, msg):

        """
    The send function is used to send a message to the C interrupt.
    The function takes in a string and converts it into bytes, then sends it through the serial port.


    :param self: Represent the instance of the class
    :param msg: Send the message to the arduino
    :return: The number of bytes sent
    :doc-author: Jakub Cermak
    """

        logger.log(msg,LogLevels.INFO)
        self.cinterrupt.send(bytes(bytearray(msg)))

    def reconnect(self, hid_host):
        """
    The reconnect function is used to re-establish a connection with the controller.
    It will attempt to connect every second until it succeeds.

    :param self: Represent the instance of the class
    :param hid_host: Specify the mac address of the device to connect to
    :return: The following:
    :doc-author: Jakub Cermak
    """
        logger.log("Trying reconnect...", LogLevels.INFO)
        while True:
            try:
                # hidHost = 'XX:XX:XX:XX:XX:XX'
                self.ccontrol = socket.socket(socket.AF_BLUETOOTH,
                                              socket.SOCK_SEQPACKET,
                                              socket.BTPROTO_L2CAP)
                self.cinterrupt = socket.socket(socket.AF_BLUETOOTH,
                                                socket.SOCK_SEQPACKET,
                                                socket.BTPROTO_L2CAP)
                self.ccontrol.connect((hid_host, self.P_CTRL))
                self.cinterrupt.connect((hid_host, self.P_INTR))
                print("Connected!")
            except Exception as ex:
                print("didnt connect, will retry..." + str(ex))
                time.sleep(1)


class BTKbService(dbus.service.Object):
    """
    Setup of a D-Bus service to receive HID messages from other
    processes.
    Send the received HID messages to the Bluetooth HID server to send
    """
    logger = Logger("service")

    def __init__(self):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the service and creates a BTKbDevice object to handle all of our bluetooth stuff.

    :param self: Represent the instance of the class
    :return: Nothing
    :doc-author: Jakub Cermak
    """
        logger.log('Setting up service', LogLevels.INFO)

        bus_name = dbus.service.BusName('org.jc.btkbservice',
                                        bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/org/jc/btkbservice')

        # create and set up our device
        self.device = BTKbDevice()

        # start listening for socket connections
        self.device.listen()

    @dbus.service.method('org.jc.btkbservice',
                         in_signature='ay')
    def send_keys(self, keys):
        """
    The send_keys function sends a string of characters to the device.

    :param self: Represent the instance of the class
    :param keys: Send the keys to the device
    :return: The keys that were sent to the device
    :doc-author: Jakub Cermak
    """
        self.device.send(keys)

    @dbus.service.method('org.jc.btkbservice', in_signature='ai')
    def send_mouse(self, state):
        """
    The send_mouse function takes in a state variable, which is the current mouse position.
    It then sends that information to the device via Bluetooth.

    :param self: Represent the instance of the class
    :param state: Send the state of the mouse to be sent via bluetooth
    :return: The state of the mouse
    :doc-author: Jakub Cermak
    """
        self.device.send(state)

    @dbus.service.method('org.freedesktop.DBus.Introspectable', out_signature='s')
    def Introspect(self):
        """
    The Introspect function is used to return the XML introspection data for this object.
    This function should be overridden by any subclasses that wish to provide their own
    introspection data.

    :param self: Represent the instance of the class
    :return: The xml introspection data for the plugin
    :doc-author: Jakub Cermak
    """
        return ET.tostring(ET.parse(os.getcwd() + '/bt_config/org.jc.hidbluetooth.introspection').getroot(),
                           encoding='utf8',
                           method='xml')


if __name__ == '__main__':
    # The sockets require root permission
    if not os.geteuid() == 0:
        sys.exit('Only root can run this script')

    DBusGMainLoop(set_as_default=True)
    myservice = BTKbService()
    mainloop = GLib.MainLoop()
    mainloop.run()
