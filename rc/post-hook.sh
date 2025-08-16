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

rc_local=/data/rc.local

# check if /data/apps/seplos3mqtt path exists
if [ ! -d "/data/apps/seplos3mqtt" ]; then
    mkdir -p /data/apps/seplos3mqtt
fi

# Intall Seplos3MQTT Driver
echo "Copying seplos3mqtt scripts and Services.." >> "$dir/venus-data_install.log" 2>&1
if [ ! -f /data/apps/seplos3mqtt/seplos3mqtt.py ]; then
    cp -f /data/seplos3mqtt/seplos3mqtt.py /data/apps/seplos3mqtt/seplos3mqtt.py
    cp -r /data/seplos3mqtt/service /data/apps/seplos3mqtt/
    cp -r /data/seplos3mqtt/startup.sh /data/apps/seplos3mqtt/startup.sh

    echo "Fixing Permissions..."
    chmod +x /data/apps/seplos3mqtt/seplos3mqtt.py
    chmod +x /data/apps/seplos3mqtt/service/run
    chmod +x /data/apps/seplos3mqtt/service/log/run
    chmod +x /data/seplos3mqtt/startup.sh

fi

#echo "Copying QML Files"
#if [ ! -f /opt/victronenergy/gui/qml/PageSettingsServices.qml.bk ]; then
#    cp -f /opt/victronenergy/gui/qml/PageSettingsServices.qml /opt/victronenergy/gui/qml/PageSettingsServices.qml.bk
#    cp -f /data/seplos3mqtt/qml/PageSettingsServices.qml /opt/victronenergy/gui/qml/PageSettingsServices.qml
#    cp -f /data/seplos3mqtt/qml/PageSettingsSeplos3MQTT.qml /opt/victronenergy/gui/qml/PageSettingsSeplos3MQTT.qml
#fi

echo "Copying Service Files" >> "$dir/venus-data_install.log" 2>&1
if [ ! -f /opt/victronenergy/service-templates/seplos3mqtt ]; then
    cp -r /data/apps/seplos3mqtt/service /opt/victronenergy/service-templates/seplos3mqtt
    ln -s /opt/victronenergy/service-templates/seplos3mqtt /services/seplos3mqtt
fi

echo "Creating rc.local file" >> "$dir/venus-data_install.log" 2>&1
# Check if rc_local exist
if [ ! -f $rc_local ]
then
    touch $rc_local
    chmod 755 $rc_local
    echo "#!/bin/bash" >> $filename
    echo >> $rc_local
fi

grep -qxF "/data/apps/seplos3mqtt/startup.sh" $rc_local || echo "/data/apps/seplos3mqtt/startup.sh" >> $rc_local

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

echo "Generate mqtt self-sign cert (cerbo.crt)" >> "$dir/venus-data_install.log" 2>&1
openssl s_client -connect localhost:8883 2>/dev/null </dev/null |  sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /data/apps/seplos3mqtt/cerbo.crt