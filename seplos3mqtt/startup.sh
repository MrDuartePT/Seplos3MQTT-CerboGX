#!/bin/bash
ln -s /opt/victronenergy/service-templates/seplos3mqtt/ /service/seplos3mqtt

# Enable services
svc -u /service/seplos3mqtt
svc -t /service/seplos3mqtt