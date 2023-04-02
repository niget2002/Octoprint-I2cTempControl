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

class I2ctempcontrolPlugin(octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.ProgressPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SimpleApiPlugin
):

    def __init__(self):
        self.currentTemperature=0
        self.fanState=0
        self.heaterState=0
        self.runTimer = None

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            hardwareAddress="0x48",
            heaterGPIOPin="00",
            fanGPIOPin="01",
            temperatureMin=10,
            temperatureMax=20
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
        self._logger.info("I2c Hardware Set to: %s" % self._settings.get(["hardwareAddress"]))

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
        self.currentTemperature = self.currentTemperature+1
        if self.currentTemperature < self._settings.get(["temperatureMin"]):
            self.fanState = -1
            self.heaterState = 1
        elif self.currentTemperature > self._settings.get(["temperatureMax"]):
            self.fanState = 1
            self.heaterState = -1
        elif self._settings.get(["temperatureMin"]) < self.currentTemperature < self._settings.get(["temperatureMax"]):
            self.fanstate = -1
            self.heaterState = -1
        self.update_data()
        self._logger.info("I2c Temperature: %s, Fan State: %s, Heater State: %s" % (self.currentTemperature, self.fanState, self.heaterState))


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
