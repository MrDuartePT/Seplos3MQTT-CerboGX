#!/usr/bin/env python

"""
Seplos BMSv3 to MQTT
---------------------------------------------------------------------------


"""
# --------------------------------------------------------------------------- #
# import the various needed libraries
# --------------------------------------------------------------------------- #
import signal
import sys
import logging
import serial
import configparser
import paho.mqtt.client as mqtt
import os
import ssl

from modules.logger import setup_logger
from modules.Modbus import PackModbus

# --------------------------------------------------------------------------- #
# declare the sniffer
# --------------------------------------------------------------------------- #
class SerialSnooper:

    def __init__(self, port, mqtt_server, mqtt_port, mqtt_user, mqtt_pass, mqtt_tls, mqtt_cert):
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.data = bytearray(0)
        self.trashdata = False
        self.trashdataf = bytearray(0)
        self.batts_declared_set = set()
        # init the signal handler for a clean exit
        signal.signal(signal.SIGINT, self.signal_handler)

        self.logger.info(f"Opening serial interface, port: {port} 19200 8N1 timeout: 0.001750")
        self.connection = serial.Serial(port=port, baudrate=19200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.001750)
        self.logger.debug(self.connection)
       
        self.mqtt_hass = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_hass.username_pw_set(username=mqtt_user, password=mqtt_pass)
        if (mqtt_tls == "True" or mqtt_tls == "true"):
            if os.path.isfile(mqtt_cert):
                self.mqtt_hass.tls_set(ca_certs=mqtt_cert, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE)
            else:
                self.logger.warning("SSL cert (" + mqtt_cert + ") dosen't exist! SSL autentication disable!!!")
        try:
            self.logger.info(f"Opening MQTT connection, server: {mqtt_server}\tport: {mqtt_port}")
            self.mqtt_hass.connect(mqtt_server, mqtt_port) 
        except ConnectionRefusedError:
            print("Error: Unable to connect to MQTT server.")
        except Exception as e:
            print(f"MQTT Unexpected error: {str(e)}")


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.connection.open()

    def close(self):
        self.connection.close()
    
    def read_raw(self, n=1):
        return self.connection.read(n)
    
    # --------------------------------------------------------------------------- #
    # configure a clean exit (even with the use of kill, 
    # may be useful if saving the data to a file)
    # --------------------------------------------------------------------------- #
    def signal_handler(self, sig, frame):
        for batt_number in self.batts_declared_set:
            self.logger.info(f"Sending offline signal for Battery {batt_number}")
            self.mqtt_hass.publish(f"{mqtt_prefix}/battery_{batt_number}/state", "offline", retain=True)
        print('\nGoodbye\n')
        sys.exit(0)
    
    def to_lower_under(self, text):
        text = text.lower()
        text = text.replace(' ', '_')
        return text


    # --------------------------------------------------------------------------- #
    # Bufferise the data and call the decoder if the interframe timeout occur.
    # --------------------------------------------------------------------------- #
    def process_data(self, data):
        if len(data) <= 0:
            if len(self.data) > 2:
                self.data = PackModbus.decode(self.data)
            return
        for dat in data:
            self.data.append(dat)
        

# --------------------------------------------------------------------------- #
# Print the usage help
# --------------------------------------------------------------------------- #
def printHelp():
    print("\nUsage:")
    print("  python seplos3mqtt.py")
    print("")
    print("Seplos3mqtt gets the configuration from seplos3mqtt.ini")
    print("Remember to create the file and include the following data:")
    print("[seplos3mqtt]")
    print("serial = ")
    print("mqtt_server = ")
    print("mqtt_port = ")
    print("mqtt_user = ")
    print("mqtt_pass = ")
    print("mqtt_prefix = ")
    print("")


# --------------------------------------------------------------------------- #
# get variable config from environment or config file
# --------------------------------------------------------------------------- #

def get_config_variable(name,default='mandatory'):
   try:
      # try to get variable from environment
      value = os.getenv(name)
      if value is not None:
         return value

      # the environment variable uis not defined, find in file .ini
      config = configparser.ConfigParser()
      config.read(os.path.dirname(__file__) + '/seplos3mqtt.ini')
      if not config.sections():  # Verificar si se cargaron secciones
            raise FileNotFoundError()

      return config.get('seplos3mqtt', name)

   except configparser.NoSectionError as e:
      if default != 'mandatory':
         return default
      else:
         print(f'Error: Section [seplos3mqtt] not found in the file seplos3mqtt.ini for variable {name}, exception: {e}')
         printHelp()
         sys.exit()
   except configparser.NoOptionError as e:
       if default != 'mandatory':
          return default
       else:
          print(f'Error: Parameter {name} not found in environment variable or in the file seplos3mqtt.ini Details: {e}')
          printHelp()
          sys.exit()
   except FileNotFoundError as e:
        if default != 'mandatory':
           return default
        else:
           print(f'Error: seplos3mqtt.ini was not found or environment variable {name} not defined.')
           printHelp()
           sys.exit()
   except Exception as e:
        print(f'Unexpected error: {e}')
        printHelp()
        sys.exit()




# --------------------------------------------------------------------------- #
# main routine
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print(" ")
    # Setup Logging
    setup_logger()

    try:
        port = get_config_variable('serial')
        mqtt_server =  get_config_variable('mqtt_server')
        mqtt_port = int(get_config_variable('mqtt_port',"1883"))
        mqtt_user = get_config_variable('mqtt_user',"")
        mqtt_pass = get_config_variable('mqtt_pass',"")
        mqtt_prefix = get_config_variable('mqtt_prefix',"seplos")
        mqtt_tls = get_config_variable('mqtt_tls', "False")
        mqtt_cert = get_config_variable('mqtt_cert', "/data/apps/seplos3mqtt/cerbo.crt")

        with SerialSnooper(port, mqtt_server, mqtt_port, mqtt_user, mqtt_pass, mqtt_tls, mqtt_cert) as sniffer:
            while True:
                data = sniffer.read_raw()
                sniffer.process_data(data)
    except Exception as e:
        print(f'Unexpected error: {e}')
        printHelp()

#Master: ID: 3, Read Input Registers: 0x04, Read address: 4096, Read Quantity: 18 //Pack Main information
#Slave:  ID: 3, Read Input Registers: 0x04, Read byte count: 36, Read data: [14 94 f4 c9 56 f4 6d 60 01 a6 03 1b 03 e5 00 1a 0c dc 0b 7d 0c de 0c d9 0b 80 0b 77 00 00 00 46 00 46 03 e8]
#Master: ID: 3, Read Input Registers: 0x04, Read address: 4352, Read Quantity: 26 //Pack Cells information
#Slave:  ID: 3, Read Input Registers: 0x04, Read byte count: 52, Read data: [0c dd 0c dd 0c dd 0c dc 0c dd 0c dd 0c dc 0c dc 0c d9 0c dc 0c dd 0c de 0c de 0c dd 0c dc 0c de 0b 7e 0b 80 0b 77 0b 80 0a ab 0a ab 0a ab 0a ab 0b 81 0b 6b]
#Master: ID: 3, Read Coils: 0x01, Read address: 4608, Read Quantity: 144 //Pack Alarms and Status
#Slave:  ID: 3, Read Coils: 0x01, Read byte count: 18, Read data: [00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 03 00 00]
