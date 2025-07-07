#!/bin/bash

# executed after archive extraction on USB install
# see https://github.com/victronenergy/meta-victronenergy/blob/15fa33c3e5430f7c08a688dc02171f5be9a81c84/meta-venus/recipes-core/initscripts/files/update-data.sh#L43

# search for venus-data.tar.gz in USB root and copy it, if found
for dir in /media/*; do
    if [ -f "$dir/venus-data.tar.gz" ]; then
        cp -f "$dir/venus-data.tar.gz" "/tmp/venus-data.tar.gz"
        break
    fi
done

# check if /data/apps/seplos3mqtt path exists
if [ ! -d "/data/apps/seplos3mqtt" ]; then
    mkdir -p /data/apps/seplos3mqtt
fi

# Intall Seplos3MQTT Driver
if [ -f "/data/seplos3mqtt/install.sh" ]; then
    bash /data/seplos3mqtt/install.sh >> "$dir/venus-data_install.log" 2>&1
    rm -rf "/data/seplos3mqtt"

# search for seplos3mqtt.ini in USB root and copy it, if found
for dir in /media/*; do
    if [ -f "$dir/seplos3mqtt.ini" ]; then
        cp -f $dir/seplos3mqtt.ini /data/apps/seplos3mqtt/seplos3mqtt.ini

        # remove backup config.ini
        if [ -f "/data/apps/seplos3mqtt.ini.backup" ]; then
            rm /data/apps/seplos3mqtt.ini.backup
        fi
    fi
done

# restore seplos3mqtt.ini
if [ -f "/data/apps/seplos3mqtt.ini.backup" ]; then
    mv /data/apps/seplos3mqtt.ini.backup /data/apps/seplos3mqtt/seplos3mqtt.ini
fi

# rename the venus-data.tar.gz else the data is overwritten, if the USB is not removed
for dir in /media/*; do
    if [ -f "$dir/venus-data.tar.gz" ]; then
        mv "$dir/venus-data.tar.gz" "$dir/venus-data_installed.tar.gz"
    fi
done

# Enable the services
svc -u /service/seplos3mqtt
svc -t /service/seplos3mqtt