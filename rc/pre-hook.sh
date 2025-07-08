#!/bin/bash

# executed before archive extraction on USB install
# see https://github.com/victronenergy/meta-victronenergy/blob/15fa33c3e5430f7c08a688dc02171f5be9a81c84/meta-venus/recipes-core/initscripts/files/update-data.sh#L42

# search for venus-data.tar.gz in USB root and copy it, if found
for dir in /media/*; do
    if [ -f "$dir/venus-data.tar.gz" ]; then
        break
    fi
done

rc_local=/data/rc.local

# backup seplos3mqtt.ini
if [ -f "/data/apps/seplos3mqtt/seplos3mqtt.ini" ]; then
    mv /data/apps/seplos3mqtt/seplos3mqtt.ini /data/apps/seplos3mqtt.ini.backup
fi

# remove old driver
if [ -f "/data/apps/seplos3mqtt" ]; then
    rm -rf /data/apps/seplos3mqtt
    rm -rf /opt/victronenergy/gui/qml/PageSettingsSeplos3MQTT.qml
    if  [ -e /service/seplos3mqtt ]
    then
        rm /service/seplos3mqtt
        kill $(pgrep -f 'seplos3mqtt.py')
        kill $(pgrep -f 'seplos3mqtt.py')  /dev/null 2> /dev/null
    fi
    #rm -rf "/opt/victronenergy/service-templates/seplos3mqtt"
    #mv /opt/victronenergy/gui/qml/PageSettingsServices.qml.bk /opt/victronenergy/gui/qml/PageSettingsServices.qml
    [ -f "$rc_local" ] && sed -i '\|/data/apps/seplos3mqtt/startup.sh|d' "$rc_local"
fi

# Initialize log
echo -e "\n\n\n" >> "$dir/venus-data_install.log" 2>&1
echo "$(date +%Y-%m-%d\ %H:%M:%S) INFO: *** Starting Seplos3MQTT installation! ***" >> "$dir/venus-data_install.log" 2>&1
