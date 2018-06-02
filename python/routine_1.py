# -*- coding: utf-8 -*-
"""
routine_1.py

Sends commands to Arduino Uno via serial port to control a drone
using the nRF24L01 wireless boards.

@author: Andrew Kouri
"""
import time
from threading import Thread

from syma_controller import SymaController


def routine_1():
    controller = SymaController()
    controller.POWER_ON = True
    read_thread = Thread(target=controller.read_input)
    read_thread.start()
    # controller.reboot_arduino()
    controller.connect()
    time.sleep(3)
    controller.send_command("initbind")
    controller.bypass_safety_check()
    for i in range(5):
        controller.set_throttle(0.1)
        controller.set_aileron(i / 10)
        time.sleep(0.3)
        # controller.set_throttle(0.0)
        # time.sleep(0.2)
    controller.set_throttle(0.0)
    controller.POWER_ON = False
    controller.disconnect()
    read_thread.join()


if __name__ == "__main__":
    routine_1()
