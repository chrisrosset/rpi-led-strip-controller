# rpi-led-strip-controller

A software controller for generic LED strips for the Raspberry Pi.

![LED Strip image](http://www.3egadgets.com/79-240-thickbox/non-waterproof-flexible-rgb-led-strip.jpg)

This software is meant to enable replacing the hardware controller and remote
combo that is bundled with these strips. Hooking these up to a Raspberry Pi
allows for a multitude of new possibilities:

* custom color transitions
* remote control
* integration with home automation systems

## Wiring

Popoklopsi has written [a great tutorial on how to connect an RGB LED strip to a
Raspberry Pi](http://popoklopsi.github.io/RaspberryPi-LedStrip/).

## Installation and Dependencies

At the moment, there is no automated installation process. In order to run this
project, you will need in manually install the following libraries:

* [pigpio](http://abyz.co.uk/rpi/pigpio/)
* [Flask](http://flask.pocoo.org/)

With these in place, just run `server.py` which will start the server on port 5000.

## Interface

The server works by accepting HTTP requests for `program` (which can be either
a static color or a name of a particular color transition type) and `speed`.

Examples:

```
curl localhost:5000/speed/1
curl localhost:5000/program/red
curl localhost:5000/program/00FF00
curl localhost:5000/program/smooth
curl localhost:5000/?speed=1
curl localhost:5000/?program=red
curl localhost:5000/?program=00FF00
curl localhost:5000/?program=smooth
curl localhost:5000/?program=smooth?speed=10
```

## Home Assistant Integration

One of the main motivations of this project was gaining the ability to control
LED strips from a [Home Assistant](http://home-assistant.io) dashboard.

First, we define two notification services:

```
notify:
  - platform: rest
    name: led_program
    resource: http://rasbperrypi.lan:5000/
    method: GET
    message_param_name: "program"
  - platform: rest
    name: led_speed
    resource: http://raspberrypi.lan:5000/
    method: GET
    message_param_name: "speed"
```

Then, we define two user inputs that correspond to the requests that our server
can process:

```
input_select:
  led_program:
    name: "Program"
    options:
      - 'off'
      - red
      - blue
      - green
      - white
      - purple
      - flash
      - fade
      - strobe
      - smooth

input_slider:
  led_speed:
    name: "Speed"
    icon: mdi:speedometer
    initial: 1
    min: 1
    max: 20
    step: 1
```

We tie the two by creating two corresponding automation triggers that will call
the appropriate service when the state of our inputs changes:

```
automation:
  - trigger:
      platform: state
      entity_id: input_select.led__program
    action:
      service: notify.led__program
      data_template:
        message: '{{ trigger.to_state.state }}'
  - trigger:
      platform: state
      entity_id: input_slider.led__speed
    action:
      service: notify.led__speed
      data_template:
        message: '{{ trigger.to_state.state }}'

```

Finally, we can groups these two together in the UI by creating a group:

```
group:
  'LED':
    entities:
    - input_select.led_program
    - input_slider.led_speed
```

And we're done. Voila!

