# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint.util
import time
import smbus
import RPi.GPIO as GPIO


I2C_BUS_NUMBER			= 1
LM75_ADDRESS		 	= 0x48  #Default address if not supplied

LM75_TEMP_REGISTER 	 	= 0
LM75_CONF_REGISTER 	 	= 1
LM75_THYST_REGISTER  	= 2
LM75_TOS_REGISTER 	 	= 3

LM75_CONF_SHUTDOWN  	= 0
LM75_CONF_OS_COMP_INT 	= 1
LM75_CONF_OS_POL 	 	= 2
LM75_CONF_OS_F_QUE 	 	= 3


class LM75(object):
	def __init__(self, mode=LM75_CONF_OS_COMP_INT, i2c_address=LM75_ADDRESS,
							 busnum=I2C_BUS_NUMBER):
		self._mode = mode
		self.i2c_address = i2c_address
		self._bus = smbus.SMBus(busnum)

	def getRegisterVal(self):
		"""
		Reads the temp from the LM75 sensor.
		Returns the raw register value.
		"""
		try:
			#Read from the temperature register on the chip
			raw = self._bus.read_word_data(self.i2c_address, LM75_TEMP_REGISTER) & 0xFFFF
			#Swap LSB and MSB
			reordered_raw = ((raw << 8) & 0xFF00) + (raw >> 8)
			#Check to see if we have a positive or negative temperature
			# Bit 16 is the positive or negative flag.
			# Shift it over into bit 1 so we can use it as a boolean
			temperature_is_negative = (reordered_raw >> 15)
			#Only the 11 most significant bits contain temperature data
			# For positive temperatures we just shift over 5 bits
			# For negative temperatures we shift over 5 bits and take two complement
			if temperature_is_negative:
				register_value = (((reordered_raw >> 5) & 0xFFFF) - 1) - 0b0000011111111111
			else:
				register_value = reordered_raw >> 5
		except:
			print("Error while trying to read i2c bus at chip address", hex(self.i2c_address), "\n")
			raise
		return register_value

	def getCelsius(self):
		"""
		Converts raw register value into celsius temperature reading.
		Returns celsius degrees to three decimal places.
		"""
		c_val = self.getRegisterVal() * 0.125
		return round(c_val, 3)

	def getFahrenheit(self):
		"""
		Converts celsius temperature reading into fahrenheit.
		Returns fahrenheit degrees to thre decimal places.
		"""
		f_val = (self.getCelsius() * (9.0/5.0)) + 32.0
		return round(f_val, 3)

class I2ctempcontrolPlugin(octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.ProgressPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SimpleApiPlugin
):

    def __init__(self):
        self.fanState=0
        self.heaterState=0
        self.runTimer = None

        # setup LM75 Temp Sensor
        self.sensor = LM75()
        self.currentTemperature= self.sensor.getCelsius()

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            hardwareAddress="0x48",
            heaterGPIOPin=13,
            fanGPIOPin=15,
            temperatureMin=20,  # decent for PLA
            temperatureMax=30   # decent for PLA
            )

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/i2ctempcontrol.js"],
            "css": ["css/i2ctempcontrol.css"],
            "less": ["less/i2ctempcontrol.less"]
        }

    ##~~ Startup Plugin
    def on_after_startup(self):
        self._logger.info("I2c Temp Probe Set to: %s" % self._settings.get(["hardwareAddress"]))
        self._logger.info("I2c Fan Set to: %s" % self._settings.get(["fanGPIOPin"]))
        self._logger.info("I2c Heater Set to: %s" % self._settings.get(["heaterGPIOPin"]))
        self.update_data()

        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._settings.get(["fanGPIOPin"]), GPIO.OUT)
        GPIO.setup(self._settings.get(["heaterGPIOPin"]), GPIO.OUT)

    def get_template_vars(self):
        return dict(
            hardwareAddress=self._settings.get(["hardwareAddress"]),
            heaterGPIOPin=self._settings.get(["heaterGPIOPin"]),
            fanGPIOPin=self._settings.get(["fanGPIOPin"]),
            temperatureMin=self._settings.get(["temperatureMin"]),
            temperatureMax=self._settings.get(["temperatureMax"])
            )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]
    
    def get_api_commands(self):
        return dict(
            start_timer=[],
            stop_timer=[]
        )

    def on_api_command(self, command, data):
        self._logger.info("I2c Got API Call (%s)" % command)
        if command == "start_timer":
            if self.runTimer == None:
                self._logger.info("I2c starting timer")
                self.runTimer = octoprint.util.RepeatedTimer(5.0, self.get_temperature)
                self.runTimer.start()

        elif command == "stop_timer":
            if self.runTimer != None:
                self._logger.info("I2c stopping timer")
                self.runTimer.cancel()
                self.runTimer = None
                self.fanState = -1
                self.heaterState = -1
                self.update_data()
 
    def get_temperature(self):
        self._logger.info("Getting Chamber Temperature")
        self.currentTemperature = self.sensor.getCelsius()
        if self.currentTemperature < self._settings.get(["temperatureMin"]):
            self.fanState = -1
            self.heaterState = 1
        elif self.currentTemperature > self._settings.get(["temperatureMax"]):
            self.fanState = 1
            self.heaterState = -1
        elif self._settings.get(["temperatureMin"]) < self.currentTemperature < self._settings.get(["temperatureMax"]):
            self.fanstate = -1
            self.heaterState = -1
        self.update_relays()
        self.update_data()
        self._logger.info("I2c Temperature: %s, Fan State: %s, Heater State: %s" % (self.currentTemperature, self.fanState, self.heaterState))

    def update_relays(self):
        if self.heaterState:
            GPIO.output(self._settings.get(["heaterGPIOPin"]), GPIO.HIGH)
        else:
             GPIO.output(self._settings.get(["heaterGPIOPin"]), GPIO.LOW)
        if self.fanState:
            GPIO.output(self._settings.get(["fanGPIOPin"]), GPIO.HIGH)
        else:
             GPIO.output(self._settings.get(["fanGPIOPin"]), GPIO.LOW)

    def update_data(self):
        msg = dict( 
            temperatureValue = self.currentTemperature,
            fanState = self.fanState,
            heaterState = self.heaterState
            )
        self._plugin_manager.send_plugin_message(self._identifier, msg)

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "i2ctempcontrol": {
                "displayName": "I2ctempcontrol Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "niget2002",
                "repo": "OctoPrint-I2ctempcontrol",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/niget2002/OctoPrint-I2ctempcontrol/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "I2C Temperature Controller"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = I2ctempcontrolPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
