#!/bin/bash
set -e

PACKAGE_PATH="/usr/local/lib/python3.5/dist-packages/openhsr_connect"
BACKEND_SCRIPT="/usr/lib/cups/backend/openhsr-connect"

# Remove printer if installed
if [ lpstat -a openhsr-connect 2&> /dev/null]; then
    echo "Removing printer openhsr-connect..."
    lpadmin -x openhsr-connect
fi

# Remove printing symlink
if [ -e ${BACKEND_SCRIPT} ]; then
	rm ${BACKEND_SCRIPT}
fi
