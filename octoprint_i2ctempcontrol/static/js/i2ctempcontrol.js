/*
 * View model for OctoPrint-I2ctempcontrol
 *
 * Author: David Walling
 * License: AGPLv3
 */
$(function() {
    function I2ctempcontrolViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.temperatureValue = ko.observable();
        self.fanState = ko.observable("Off");
        self.heaterState = ko.observable("Off");
        self.controlState = ko.observable("Off");
        self.setTempMin = ko.observable(0);
        self.setTempMax = ko.observable(0);

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (data.temperatureValue) { self.temperatureValue(data.temperatureValue); }
            if (data.setTempMin) {self.setTempMin(data.setTempMin)}
            if (data.setTempMax) {self.setTempMax(data.setTempMax)}
            if (data.controlState == 1) { self.controlState("On");}
            else {self.controlState("Off")}       
            if (data.fanState == 1) { self.fanState("On") }
            else {self.fanState("Off") }        
            if (data.heaterState == 1) { self.heaterState("On") }
            else { self.heaterState("Off") }     
        }

        self.startLoop = function() {
            OctoPrint.simpleApiCommand('i2ctempcontrol', 'start_timer');
        }

        self.stopLoop = function() {
            OctoPrint.simpleApiCommand('i2ctempcontrol', 'stop_timer');       
        }

        self.onBeforeBinding = function() {
            OctoPrint.simpleApiCommand('i2ctempcontrol', 'force_update');
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: I2ctempcontrolViewModel,
        dependencies: [ "settingsViewModel" ],
        elements: ["#tab_plugin_i2ctempcontrol" ]
    });
});
