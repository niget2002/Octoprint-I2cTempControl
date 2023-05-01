# OctoPrint-I2ctempcontrol

I2ctempcontrol attempts at helping to maintain a stable chamber temperature. It uses a LM75 i2c thermometer to measure the temperature of the chamber. It then uses a simple bang bang control for turning on either an exhaust fan, or a heater to keep the chamber within two values. The LM75 hardware adress, GPIO pins, and min/max temperature are all configurable in settings.

Currently, the controller has to be manually started and stopped on it's own tab. An eventual idea is to have a custom Gcode that can be used to start the process and then have it stop automatically after the print is complete.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/niget2002/OctoPrint-I2ctempcontrol/archive/master.zip

## Configuration

The code is set up to use the BOARD pin number for the GPIOPins. It is also setup to use channel 1 on the SMBUS for the I2C. You'll need to login to the Pi through SSH and use i2cdetect to get the hardware address of your LM75.

## Usage

Once configured, you can go to the I2C Temperature Controller tab in octoprint. You will see 2 buttons. One will start the chamber controller, the other will stop it. There is currently a bug that the controller shows 'off' even though it's running. You'll see it flicker 'on' then 'off' when the temperature is updated.

![Chamber Controller](https://github.com/niget2002/Octoprint-I2cTempControl/blob/master/images/ChamberController.png)