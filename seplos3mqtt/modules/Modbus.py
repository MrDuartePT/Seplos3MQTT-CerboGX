"""
Seplos BMSv3 Modbus Class
---------------------------------------------------------------------------


"""
# --------------------------------------------------------------------------- #
# import the various needed libraries
# --------------------------------------------------------------------------- #
import signal
import sys
import serial
import os
from autodiscovery import AutoDiscovery


# ------------------------------------------------------------------------------- #
# This class is reponsible for Modbus Comunication when using only one Seplos BMS
# ------------------------------------------------------------------------------- #

class BatteryModbus:
    TODO # pyright: ignore[reportUndefinedVariable]

# --------------------------------------------------------------------------- #
# This class is reponsible for Modbus Comunication when using Seplos BMS pack 
# (Multiple Batteries)
# --------------------------------------------------------------------------- #
class PackModbus:
    # --------------------------------------------------------------------------- #
    # Debuffer and decode the modbus frames (Request, Responce, Exception)
    # --------------------------------------------------------------------------- #
    def decode(self, data):
        modbusdata = data
        bufferIndex = 0
        
        while True:
            unitIdentifier = 0
            functionCode = 0
            readByteCount = 0
            readData = bytearray(0)
            crc16 = 0
            responce = False
            needMoreData = False
            frameStartIndex = bufferIndex           
            if len(modbusdata) > (frameStartIndex + 2):
                # Unit Identifier (Slave Address)
                unitIdentifier = modbusdata[bufferIndex]
                bufferIndex += 1
                # Function Code
                functionCode = modbusdata[bufferIndex]
                bufferIndex += 1
                if functionCode == 1:
                    # Responce size: UnitIdentifier (1) + FunctionCode (1) + ReadByteCount (1) + ReadData (n) + CRC (2)
                    expectedLenght = 7 # 5 + n (n >= 2)
                    if len(modbusdata) >= (frameStartIndex + expectedLenght):
                        bufferIndex = frameStartIndex + 2
                        # Read Byte Count (1)
                        readByteCount = modbusdata[bufferIndex]
                        bufferIndex += 1
                        expectedLenght = (5 + readByteCount)
                        if len(modbusdata) >= (frameStartIndex + expectedLenght):
                            # Read Data (n)
                            index = 1
                            while index <= readByteCount:
                                readData.append(modbusdata[bufferIndex])
                                bufferIndex += 1
                                index += 1
                            # CRC16 (2)
                            crc16 = (modbusdata[bufferIndex] * 0x0100) + modbusdata[bufferIndex + 1]
                            metCRC16 = self.calcCRC16(modbusdata, bufferIndex)
                            bufferIndex += 2
                            if crc16 == metCRC16:
                                if self.trashdata:
                                    self.trashdata = False
                                    self.trashdataf += "]"
                                    #log.info(self.trashdataf)
                                responce = True

                                #### Pack Alarms and Status ###
                                if readByteCount == 18:   
                                    if unitIdentifier not in self.batts_declared_set:
                                        AutoDiscovery.battery(unitIdentifier)
                                        self.batts_declared_set.add(unitIdentifier)

                                    strStatus = "" 
                                    if   (readData[8] >> 0) & 1: strStatus = "Discharge"
                                    elif (readData[8] >> 1) & 1: strStatus = "Charge"
                                    elif (readData[8] >> 2) & 1: strStatus = "Floating charge"
                                    elif (readData[8] >> 3) & 1: strStatus = "Full charge"
                                    elif (readData[8] >> 4) & 1: strStatus = "Standby mode"
                                    elif (readData[8] >> 5) & 1: strStatus = "Turn off"

                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/status", strStatus, retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb09", readData[8], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb02", readData[9], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb03", readData[10], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb04", readData[11], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb05", readData[12], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb16", readData[13], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb06", readData[14], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb07", readData[15], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb08", readData[16], retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/tb15", readData[17], retain=True)

                                modbusdata = modbusdata[bufferIndex:]
                                bufferIndex = 0
                        else:
                            needMoreData = True
                    else:
                        needMoreData = True
                # FC03 (0x03) Read Holding Registers  FC04 (0x04) Read Input Registers
                elif functionCode == 4:
                    # Responce size: UnitIdentifier (1) + FunctionCode (1) + ReadByteCount (1) + ReadData (n) + CRC (2)
                    expectedLenght = 7 # 5 + n (n >= 2)
                    if len(modbusdata) >= (frameStartIndex + expectedLenght):
                        bufferIndex = frameStartIndex + 2
                        # Read Byte Count (1)
                        readByteCount = modbusdata[bufferIndex]
                        bufferIndex += 1
                        expectedLenght = (5 + readByteCount)
                        if len(modbusdata) >= (frameStartIndex + expectedLenght):
                            # Read Data (n)
                            index = 1
                            while index <= readByteCount:
                                readData.append(modbusdata[bufferIndex])
                                bufferIndex += 1
                                index += 1
                            # CRC16 (2)
                            crc16 = (modbusdata[bufferIndex] * 0x0100) + modbusdata[bufferIndex + 1]
                            metCRC16 = self.calcCRC16(modbusdata, bufferIndex)
                            bufferIndex += 2
                            if crc16 == metCRC16:
                                if self.trashdata:
                                    self.trashdata = False
                                    self.trashdataf += "]"
                                    # log.info(self.trashdataf)
                                responce = True

                                # Cell Pack information #######################################
                                celdas = {}
                                if readByteCount == 52:   
                                    celda = 0
                                    ## HASS Autodiscovery 
                                    if unitIdentifier not in self.batts_declared_set:
                                        AutoDiscovery.battery(unitIdentifier)
                                        self.batts_declared_set.add(unitIdentifier)

                                    for i in range(0, 32, 2):
                                        celda =  (((readData[i] << 8) | readData[i + 1]) / 1000.0)
                                        self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/cell_{int(i/2)+1}", celda, retain=True)

                                # Pack Main information #######################################
                                if readByteCount == 36:   
                                    readDataNumber = []

                                    for i in range(0, 36, 2):
                                        readDataNumber.append((readData[i] << 8) | readData[i + 1])
                                    # HASS autodiscovery MQTT    
                                    if unitIdentifier not in self.batts_declared_set:
                                        AutoDiscovery.battery(unitIdentifier)
                                        self.batts_declared_set.add(unitIdentifier)

                                    # Pack Voltage
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/pack_voltage", readDataNumber[0]/100.0, retain=True)
                                    # Current
                                    current_decimal = readDataNumber [1] if readDataNumber [1] <= 32767 else readDataNumber [1] - 65536
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/current", current_decimal/100.0, retain=True)
                                    # Remaining Capacity
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/remaining_capacity", readDataNumber[2]/100.0, retain=True)
                                    # Total Capacity
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/total_capacity", readDataNumber[3]/100.0, retain=True)
                                    # Total Discharge Capacity
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/total_discharge_capacity", readDataNumber[4]*10, retain=True)
                                    # SOC
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/soc", readDataNumber[5]/10.0, retain=True)
                                    # SOH
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/soh", readDataNumber[6]/10.0, retain=True)
                                    # Cycles
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/cycles", readDataNumber[7], retain=True)
                                    # Average Cell Voltage
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/average_cell_voltage", readDataNumber[8]/1000.0, retain=True)
                                    # Average Cell Temp
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/average_cell_temp", round ((readDataNumber[9]/10 - 273.15) ,1), retain=True)
                                    # Max Cell Voltage
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/max_cell_voltage", readDataNumber[10]/1000.0, retain=True)
                                    # Min Cell Voltage
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/min_cell_voltage", readDataNumber[11]/1000.0, retain=True)
                                    # Max Cell Temp
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/max_cell_temp", round ((readDataNumber[12]/10 - 273.15),1), retain=True)
                                    # Min Cell Temp
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/min_cell_temp", round ((readDataNumber[13]/10 - 273.15),1), retain=True)
                                    # Reserve readDataNumber [14]
                                    # MaxDisCurt
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/maxdiscurt", readDataNumber[15], retain=True)
                                    # MaxChgCurt
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/maxchgcurt", readDataNumber[16], retain=True)        
                                    #Calculated Power end Delta
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/power", int(-(current_decimal/100.0)*(readDataNumber[0]/100.0)), retain=True)
                                    self.mqtt_hass.publish(f"{self.mqtt_prefix}/battery_{unitIdentifier}/cell_delta", int((readDataNumber[10]) - (readDataNumber[11])), retain=True)

                                modbusdata = modbusdata[bufferIndex:]
                                bufferIndex = 0
                        else:
                            needMoreData = True
                    else:
                        needMoreData = True
            else:
                needMoreData = True

            if needMoreData:
                return modbusdata
            elif  (responce == False):
                if self.trashdata:
                    self.trashdataf += " {:02x}".format(modbusdata[frameStartIndex])
                else:
                    self.trashdata = True
                    self.trashdataf = "Ignoring data: [{:02x}".format(modbusdata[frameStartIndex])
                bufferIndex = frameStartIndex + 1
                modbusdata = modbusdata[bufferIndex:]
                bufferIndex = 0

    # --------------------------------------------------------------------------- #
    # Calculate the modbus CRC
    # --------------------------------------------------------------------------- #
    def calcCRC16(self, data, size):
        crcHi = 0XFF
        crcLo = 0xFF
        
        crcHiTable	= [	0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
                        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
                        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
                        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
                        0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
                        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
                        0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
                        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
                        0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
                        0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
                        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
                        0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
                        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
                        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
                        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
                        0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
                        0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
                        0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
                        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
                        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40]

        crcLoTable = [  0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06,
                        0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD,
                        0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
                        0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A,
                        0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4,
                        0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
                        0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3,
                        0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4,
                        0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
                        0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29,
                        0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED,
                        0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
                        0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60,
                        0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67,
                        0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
                        0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68,
                        0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E,
                        0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
                        0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71,
                        0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92,
                        0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
                        0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B,
                        0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B,
                        0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
                        0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42,
                        0x43, 0x83, 0x41, 0x81, 0x80, 0x40]

        index = 0
        while index < size:
            crc = crcHi ^ data[index]
            crcHi = crcLo ^ crcHiTable[crc]
            crcLo = crcLoTable[crc]
            index += 1

        metCRC16 = (crcHi * 0x0100) + crcLo
        return metCRC16
