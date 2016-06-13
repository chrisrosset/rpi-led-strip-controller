#!/usr/bin/env python

from flask import Flask
from flask import request
app = Flask(__name__)

import controller as C

control = C.Controller([ 17, 22, 24 ])

@app.route("/speed/<int:t>")
def speed(t):
    control.set_speed(t)
    return str(control.get_speed())

@app.route("/rgb/<string:name>")
@app.route("/program/<string:name>")
def program(name):
    control.program(name)
    return "set program: " + name

@app.route("/")
def arguments():
    if "program" in request.args:
        return program(request.args["program"])

    if "speed" in request.args:
        return speed(int(request.args["speed"]))

    return ""


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
