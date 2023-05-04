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
        self.fanState = ko.observable();
        self.heaterState = ko.observable();
        self.controlState = ko.observable();
        self.setTempMin = ko.observable(0);
        self.setTempMax = ko.observable(0);

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (data.temperatureValue) { 
                self.temperatureValue(data.temperatureValue); 
            }
            if (data.setTempMin) {
                self.setTempMin(data.setTempMin)
            }
            if (data.setTempMax) {
                self.setTempMax(data.setTempMax)
            }
            if (data.controlState == 1) { 
                self.controlState("<span style='color:green;'>On</span>");
            }
            else {
                self.controlState("<span style='color:red;'>Off</span>")
            }       
            if (data.fanState == 1) {
                self.fanState("<span style='color:green;'>On</span>")
            }
            else {
                self.fanState("<span style='color:red;'>Off</span>")
            }        
            if (data.heaterState == 1) {
                self.heaterState("<span style='color:green;'>On</span>")
            }
            else {
                self.heaterState("<span style='color:red;'>Off</span>")
            }     
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
