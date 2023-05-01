# OctoPrint-I2ctempcontrol

I2ctempcontrol attempts at helping to maintain a stable chamber temperature. It uses a LM75 i2c thermometer to measure the temperature of the chamber. It then uses a simple bang bang control for turning on either an exhaust fan, or a heater to keep the chamber within two values. The LM75 hardware adress, GPIO pins, and min/max temperature are all configurable in settings.

Currently, the controller has to be manually started and stopped on it's own tab. An eventual idea is to have a custom Gcode that can be used to start the process and then have it stop automatically after the print is complete.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/niget2002/OctoPrint-I2ctempcontrol/archive/master.zip

## Configuration

The code is set up to use the BOARD pin number for the GPIOPins. It is also setup to use channel 1 on the SMBUS for the I2C. You'll need to login to the Pi through SSH and use i2cdetect to get the hardware address of your LM75.

![Chamber Config](https://github.com/niget2002/Octoprint-I2cTempControl/blob/master/images/ChamberConfig.png)

## Usage

Once configured, you can go to the I2C Temperature Controller tab in octoprint. You will see 2 buttons. One will start the chamber controller, the other will stop it. There is currently a bug that the controller shows 'off' even though it's running. You'll see it flicker 'on' then 'off' when the temperature is updated.

![Chamber Controller](https://github.com/niget2002/Octoprint-I2cTempControl/blob/master/images/ChamberController.png)

## How it works

The logic is silly simple. If the temperature is below the Min value, it turns the heater pin on. If it goes above the Max value, it turns the exhaust fan on. Any temperature in betwen Min and Max, it does nothing.

The plugin does add the chamber temperature and current target value to the temperature graph. The target value will change from either showing Min or Max depending on if the controller is trying to heat or cool the chamber.

There is some logic for the end of a print to turn the exhaust fan on. This is to help cool the chamber back down after a print. I don't have a way of disabling this feature. I should probably add that.

## Hardware Used

I used the following hardware in my build:

* [Temp sensor](https://a.co/d/8xrasrw)
* [Chamber Heater](https://a.co/d/aMrDE8q)
* [Exhast/heater fan](https://a.co/d/86eDWm1)
* [Relay](https://a.co/d/hu0r7RQ)
* [Irf520 board](https://a.co/d/cWC2N0w)

The GPIO pins from the Raspberry Pi go to the Irf520 board. The Exhaust fan is driven directly off of the Irf520. The heater Irf520 is used to drive both the heater fan, and the relay that is controlling the heater. I used 24v fans because I'm running 24v to my SKR Pro controller.

I mounted my heater so that the fan blows across the heater and pulls air from outside. If the thermal fuse gets too hot on the heater, it will shut the heater off. Having cool air blowing onto the thermal fuse helps keep it from tripping.

I have an 80mm filter on the heater fan to keep dust from being blowin into the chamber.

The heater fan produces enough wind to push air past the heater core, but not so much that it produces any turbulance inside the chamber.

I mounted the heater in the bottom of the chamber and the exhaust fan in the lid pulling air out the top. The temperature sensor is mounted near the middle of the lid of my printer.