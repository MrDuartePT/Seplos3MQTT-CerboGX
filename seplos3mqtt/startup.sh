#!/bin/bash
if [ ! -d "/service/seplos3mqtt" ]; then
    ln -s /opt/victronenergy/service-templates/seplos3mqtt/ /service/seplos3mqtt
fi

# Enable services
svc -u /service/seplos3mqtt