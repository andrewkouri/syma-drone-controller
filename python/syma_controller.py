"""
syma_controller.py

Contains a basic "remote controller" that sends commands to Arduino Uno
via serial port to control a drone
using the nRF24L01 wireless boards.

@author: Andrew Kouri
"""

import time

import serial


class SymaController:
    arduino = None
    THROTTLE = 1000
    AILERON = 1500
    ELEVATOR = 1500
    RUDDER = 1500  # yaw, rotates the drone
    POWER_ON = False  # the "controllers" power -- just says whether or not to read lines from arduino

    def connect(self):
        if not self.arduino:
            print("connecting...")
            self.arduino = serial.Serial('/dev/cu.wchusbserial1420', 115200, timeout=.01)
            time.sleep(1)  # give the connection a second to settle

    def reboot_arduino(self):
        print("rebooting arduino...")
        # re-open the serial port which will also reset the Arduino Uno and
        # this forces the quadcopter to power off when the radio loses conection.
        self.arduino = serial.Serial('/dev/cu.wchusbserial1420', 115200, timeout=.01)
        self.arduino.setDTR(False)
        time.sleep(2)
        # toss any data already received, see
        # http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.flushInput
        self.arduino.flushInput()
        self.arduino.setDTR(True)
        time.sleep(0.1)

    def disconnect(self):
        if self.arduino:
            print("disconnecting")
            # close the connection
            self.arduino.close()
            self.arduino = None

    def _build_throttle_command(self):
        """ returns string needed to send over serial bus """
        return "%i,%i,%i,%i" % (self.THROTTLE, self.AILERON, self.ELEVATOR, self.RUDDER)

    def send_command(self, command):
        if self.arduino:
            # string commands to the Arduino are prefaced with  [PC]
            print("[PC]: " + command)
            command += "\n"
            self.arduino.write(command.encode())
            time.sleep(0.25)

    def read_input(self):
        while self.POWER_ON:
            if self.arduino:
                data = self.arduino.readline()
                if data:
                    # String responses from Arduino Uno are prefaced with [AU]
                    print("[AU]: " + str(data))
                else:
                    print(".")
            else:
                print(self.arduino)
            time.sleep(.10)

    def set_throttle(self, percent):
        assert(0.00 <= percent <= 1.0)
        self.THROTTLE = 0 + 1000 * percent
        self.send_command(self._build_throttle_command())

    def set_aileron(self, percent):
        assert(-0.5 <= percent <= .5)
        self.AILERON = 1500 + 500 * percent
        self.send_command(self._build_throttle_command())

    def bypass_safety_check(self):
        assert(self.POWER_ON)
        for i in range(10):
            self.set_throttle(float(i) / 10.0)
            time.sleep(0.01)
        self.set_throttle(0.0)
