#!/bin/bash
set -e

PACKAGE_PATH="/usr/local/lib/python3.5/dist-packages/openhsr_connect"
BACKEND_SCRIPT="/usr/lib/cups/backend/openhsr-connect"

# Add new script (a copy - no symlink because AppArmor)
cp ${PACKAGE_PATH}/resources/openhsr-connect ${BACKEND_SCRIPT}
chmod 700 ${BACKEND_SCRIPT}
chown root:root ${BACKEND_SCRIPT}

# Add the printer if not yet installed
if lpstat -a openhsr-connect 2&> /dev/null; then
    echo "Printer openhsr-connect already installed"
else
    echo "Adding printer openhsr-connect..."
    lpadmin -p openhsr-connect -E -v openhsr-connect:/tmp -P ${PACKAGE_PATH}/resources/Generic-PostScript_Printer-Postscript.ppd
fi
