"""
Seplos BMSv3 AutoDiscovery Class
---------------------------------------------------------------------------


"""
class AutoDiscovery:
    def battery (self, unitIdentifier):
        self.logger.info(f"Sending autodiscovery block Battery {unitIdentifier}")
        #Pack Main
        self.sensor ( "voltage","measurement", "V", "Pack Voltage", unitIdentifier)
        self.sensor ( "current","measurement", "A", "Current", unitIdentifier)
        self.sensor ( "","measurement", "Ah", "Remaining Capacity", unitIdentifier)
        self.sensor ( "","measurement", "Ah", "Total Capacity", unitIdentifier)
        self.sensor ( "","measurement", "Ah", "Total Discharge Capacity", unitIdentifier)
        self.sensor ( "","measurement", "%", "SOC", unitIdentifier)
        self.sensor ( "","measurement", "%", "SOH", unitIdentifier)
        self.sensor ( "","measurement", "cycles", "Cycles", unitIdentifier)
        self.sensor ( "voltage","measurement", "V", "Average Cell Voltage", unitIdentifier)
        self.sensor ( "temperature","measurement", "°C", "Average Cell Temp", unitIdentifier)
        self.sensor ( "voltage","measurement", "V", "Max Cell Voltage", unitIdentifier)
        self.sensor ( "voltage","measurement", "V", "Min Cell Voltage", unitIdentifier)
        self.sensor ( "temperature","measurement", "°C", "Max Cell Temp", unitIdentifier)
        self.sensor ( "temperature","measurement", "°C", "Min Cell Temp", unitIdentifier)
        self.sensor ( "current","measurement", "A", "MaxDisCurt", unitIdentifier)
        self.sensor ( "current","measurement", "A", "MaxChgCurt", unitIdentifier)
        self.sensor ( "power","measurement", "W", "Power", unitIdentifier)
        self.sensor ( "voltage","measurement", "mV", "Cell Delta", unitIdentifier)

        #Pack Cells
        for i in range(1, 17):
            self.sensor ( "voltage","measurement", "V", f"Cell {i}", unitIdentifier)

        #Pack Status and Alarm
        self.sensor ( "","", "", "Status", unitIdentifier)
        self.sensor ( "","", "", "TB09", unitIdentifier)
        self.sensor ( "","", "", "TB02", unitIdentifier)
        self.sensor ( "","", "", "TB03", unitIdentifier)
        self.sensor ( "","", "", "TB04", unitIdentifier)
        self.sensor ( "","", "", "TB05", unitIdentifier)
        self.sensor ( "","", "", "TB16", unitIdentifier)
        self.sensor ( "","", "", "TB06", unitIdentifier)
        self.sensor ( "","", "", "TB07", unitIdentifier)
        self.sensor ( "","", "", "TB08", unitIdentifier)
        self.sensor ( "","", "", "TB15", unitIdentifier)
        
        self.logger.info(f"Sending online signal for Battery {unitIdentifier}")
        self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/state", "online", retain=True)

    def sensor (self, dev_cla, state_class, sensor_unit, sensor_name, batt_number):
        
        name_under = self.to_lower_under (sensor_name)
        if dev_cla != "": dev_cla = f""" "dev_cla": "{dev_cla}", """
        if state_class != "": state_class = f""" "stat_cla": "{state_class}", """
        if sensor_unit != "": sensor_unit = f""" "unit_of_meas": "{sensor_unit}", """

        mqtt_packet = f"""
                        {{	 
                            "name": "{sensor_name}",
                            "stat_t": "{self.mqtt_prefix}/battery_{batt_number}/{name_under}",
                            "avty_t": "{self.mqtt_prefix}/battery_{batt_number}/state",
                            "uniq_id": "seplos_battery_{batt_number}_{name_under}",
                            {dev_cla}
                            {sensor_unit}
                            {state_class}
                            "dev": {{
                                "ids": "seplos_battery_{batt_number}",
                                "name": "Seplos BMS {batt_number}",
                                "sw": "seplos3mqtt 1.0",
                                "mdl": "Seplos BMSv3 MQTT",
                                "mf": "Domotica Solar"
                                }},
                            "origin": {{
                                "name":"seplos3mqtt by Domotica Solar",
                                "sw": "1.0",
                                "url": "https://domotica.solar/"
                            }}
                        }}
                        """
        self.mqtt_hass.publish(f"homeassistant/sensor/seplos_bms_{batt_number}/{name_under}/config", mqtt_packet, retain=True)

