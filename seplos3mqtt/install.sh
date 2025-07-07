echo "Copying seplos3mqtt scripts.."
cp -f /data/seplos3mqtt/seplos3mqtt.py /data/apps/seplos3mqtt/seplos3mqtt.py
cp -r /data/seplos3mqtt /data/apps/seplos3mqtt/service

echo "Copying QML Files"
cp /opt/victronenergy/gui/qml/PageSettingsServices.qml /opt/victronenergy/gui/qml/PageSettingsServices.qml.bk
cp /data/seplos3mqtt/qml/PageSettingsServices.qml /opt/victronenergy/gui/qml/PageSettingsServices.qml
cp /data/seplos3mqtt/qml/PageSettingsSeplos3MQTT.qml /opt/victronenergy/gui/qml/PageSettingsSeplos3MQTT.qml

echo "Fixing Permissions..."
chmod +x /data/apps/seplos3mqtt/seplos3mqtt.py
chmod +x /data/apps/seplos3mqtt/service/run
chmod +x /data/apps/seplos3mqtt/service/log/run

echo "Copy the Services..."
cp -rf "/data/apps/seplos3mqtt/service" "/opt/victronenergy/service-templates/seplos3mqtt"
ln -s /opt/victronenergy/service-templates/seplos3mqtt /service/seplos3mqtt