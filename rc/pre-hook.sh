#!/bin/bash

# executed before archive extraction on USB install
# see https://github.com/victronenergy/meta-victronenergy/blob/15fa33c3e5430f7c08a688dc02171f5be9a81c84/meta-venus/recipes-core/initscripts/files/update-data.sh#L42

# search for venus-data.tar.gz in USB root and copy it, if found
for dir in /media/*; do
    if [ -f "$dir/venus-data.tar.gz" ]; then
        break
    fi
done

# backup seplos3mqtt.ini
if [ -f "/data/apps/seplos3mqtt/seplos3mqtt.ini" ]; then
    mv /data/apps/seplos3mqtt/seplos3mqtt.ini /data/apps/seplos3mqtt.ini.backup
fi

# remove old driver
if [ -f "/data/apps/seplos3mqtt" ]; then
    rm -rf /data/apps/seplos3mqtt
    rm -rf /opt/victronenergy/gui/qml/PageSettingsSeplos3MQTT.qml
    svc -u /service/seplos3mqtt
    rm -rf "/opt/victronenergy/service-templates/seplos3mqtt"
    rm -rf /service/seplos3mqtt
    mv /opt/victronenergy/gui/qml/PageSettingsServices.qml.bk /opt/victronenergy/gui/qml/PageSettingsServices.qml
fi

# Initialize log
echo -e "\n\n\n" >> "$dir/venus-data_install.log" 2>&1
echo "$(date +%Y-%m-%d\ %H:%M:%S) INFO: *** Starting Seplos3MQTT installation! ***" >> "$dir/venus-data_install.log" 2>&1
