/////// Menu for Seplos3MQTTSettings

import QtQuick 1.1
import "utils.js" as Utils
import com.victron.velib 1.0

MbPage {
	id: root
	title: qsTr("Seplos3MQTT Settings")
    property string bindPrefixSeplos3MQTTMods: "com.victronenergy.settings/Settings/Services/Seplos3MQTTSettings"
    property string iniPath: "/data/apps/seplos3mqqt/seplos3mqtt.ini"
    property string iniContent: readFile(iniPath)

	model: VisibleItemModel
    MbSwitch
    {
        id: Seplos3MQTT
        name: qsTr("Enable Seplos3Mqtt")
        bind: Utils.path(bindPrefixSeplos3MQTTMods, "/Enable")
        text: item.value === 1 ? qsTr("Enabled") : qsTr("Disabled")
        checked: Utils.runCommand("svstat /service/seplos3mqqt").indexOf("run") !== -1
        onValueChanged: {
            if (item.value === 1) {
                Utils.runCommand("svc -u /service/seplos3mqtt");
            } else {
                Utils.runCommand("svc -k /service/seplos3mqtt");
            }
        }
        writeAccessLevel: User.AccessUser
    }
    MbEditBox
        {
            name: qsTr("Serial Port")
            bind: Utils.path (bindPrefixSeplos3MQTTMods, "/SerialPort")
            writeAccessLevel: User.AccessSuperUser
            text: extractValue(iniContent, "serial")
            onEditDone: {
                iniContent = iniContent.replace(/^(serial\s*=\s*).*/m, "$1" + text);
                writeFile(iniPath, iniContent);
                iniContent = readFile(iniPath);
            }
        }
    MbEditBox
        {
            name: qsTr("MQQT Server")
            bind: Utils.path (bindPrefixSeplos3MQTTMods, "/MQQTServer")
            writeAccessLevel: User.AccessUser
            text: extractValue(iniContent, "mqtt_server")
            onEditDone: {
                iniContent = iniContent.replace(/^(mqtt_server\s*=\s*).*/m, "$1" + text);
                writeFile(iniPath, iniContent);
                iniContent = readFile(iniPath);
            }
        }
    MbEditBox
        {
            name: qsTr("MQQT Port")
            bind: Utils.path (bindPrefixSeplos3MQTTMods, "/MQQTPort")
            writeAccessLevel: User.AccessUser
            text: extractValue(iniContent, "mqtt_port")
            onEditDone: {
                iniContent = iniContent.replace(/^(mqtt_port\s*=\s*).*/m, "$1" + text);
                writeFile(iniPath, iniContent);
                iniContent = readFile(iniPath);
            }
        }
    MbEditBox
        {
            name: qsTr("MQQT User")
            bind: Utils.path (bindPrefixSeplos3MQTTMods, "/MQQTUser")
            writeAccessLevel: User.AccessUser
            text: extractValue(iniContent, "mqtt_user")
            onEditDone: {
                iniContent = iniContent.replace(/^(mqtt_user\s*=\s*).*/m, "$1" + text);
                writeFile(iniPath, iniContent);
                iniContent = readFile(iniPath);
            }
        }
    MbEditBox
        {
            name: qsTr("MQQT Password")
            bind: Utils.path (bindPrefixSeplos3MQTTMods, "/MQQTPass")
            writeAccessLevel: User.AccessUser
            text: extractValue(iniContent, "mqtt_user")
            onEditDone: {
                iniContent = iniContent.replace(/^(mqtt_pass\s*=\s*).*/m, "$1" + text);
                writeFile(iniPath, iniContent);
                iniContent = readFile(iniPath);
            }
        }
    MbEditBox
        {
            name: qsTr("MQQT Prefix")
            bind: Utils.path (bindPrefixSeplos3MQTTMods, "/MQQTPrefix")
            writeAccessLevel: User.AccessUser
            text: extractValue(iniContent, "mqtt_prefix")
            onEditDone: {
                iniContent = iniContent.replace(/^(mqtt_prefix\s*=\s*).*/m, "$1" + text);
                writeFile(iniPath, iniContent);
                iniContent = readFile(iniPath);
            }
        }
}
