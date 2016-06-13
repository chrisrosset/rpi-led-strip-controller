#!/usr/bin/env python

import math
from functools import partial
import re
import struct
import time
import threading

import pigpio

COLORS = {
    "red"     : "FF0000",
    "green"   : "00FF00",
    "blue"    : "0000FF",
    "white"   : "FFFFFF",
    "purple"  : "A020F0",
    "black"   : "000000",
}

def is_rgb(rgb):
    return re.match("[a-fA-F0-9]{6}", rgb) is not None

class Controller:

    def __init__(self, pins):

        assert len(pins) == 3

        self.PINS = pins
        self.MIN_SPEED = 1
        self.MAX_SPEED = 20

        self.interval = 1
        self.speed    = 1
        self.set_speed(self.MIN_SPEED)

        self.gpio = None
        self.gpio = pigpio.pi()

        self.stop_event = threading.Event()

        self.thread = None

        self.programs = {
            "off"    : self.off,
            "fade"   : self.fade,
            "flash"  : self.flash,
            "strobe" : self.strobe,
            "smooth" : self.smooth
        }

    def __del__(self):
        if self.gpio is not None:
            self.gpio.close()
            
    def clear(self):
        if (self.thread is not None) and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()

        self.stop_event.clear()
        self.thread = None

    def status(self):
        pass

    def get_speed(self):
        return self.speed

    def set_speed(self, speed):
        if speed < self.MIN_SPEED:
            speed = self.MIN_SPEED
        elif speed > self.MAX_SPEED:
            speed = self.MAX_SPEED
            
        self.speed    = speed
        self.interval = 2.0 / speed

    def program(self, name):
        self.clear()

        target = None

        if name in self.programs:
            target = self.programs[name]
        elif name in COLORS:
            target = partial(self.color, struct.unpack('BBB', COLORS[name].decode('hex')))
        elif is_rgb(name):
            target = partial(self.color, struct.unpack('BBB', name.decode('hex')))
        else:
            print("invalid program: " + name)

        if target is not None:
            print("Starting program: " + name)
            self.thread = threading.Thread(target=target)
            self.thread.start()

        return

    ###### PROGRAM UTILITIES ###################################################

    def color(self, rgb):
        assert len(self.PINS) == len(rgb)

        for i in range(len(rgb)):
            self.gpio.set_PWM_dutycycle(self.PINS[i], rgb[i])

    def presets(self, l):
        while True:
            for preset in l:
                self.color(preset)
                self.stop_event.wait(timeout=self.interval)
                if self.stop_event.is_set():
                    return

    ###### PROGRAMS ############################################################

    def off(self):
        self.color((0, 0, 0))

    def fade(self):

        phase = [0, math.pi * 2/3, math.pi*4/3]
        width = 127
        center = 128
        length = 50
        
        i = 0
        while True:
            self.color([ math.sin(0.05 * i + phase[x]) * width + center for x in range(len(phase)) ])
            i += 1
            self.stop_event.wait(timeout=self.interval / 5)
            if self.stop_event.is_set():
                return

    def flash(self):
        self.presets([
            (255,   0,   0),
            (  0, 255,   0),
            (  0,   0, 255),
            (255, 255,   0),
            (255,   0, 255),
            (  0, 255, 255),
            (255, 255, 255),
        ])

    def smooth(self):
        self.presets([ (255, 0, 0), (0, 255, 0), (0, 0, 255) ])

    def strobe(self):
        self.presets([ [x,x,x] for x in range(1, 256, 2) + range(254, 0, -2) ])

