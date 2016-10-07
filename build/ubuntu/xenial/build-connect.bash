#!/bin/bash
# This scripts builds the connect package
# Required env variables:
# - ARCH: Build architecture
# - FPM_DEFAULTS: Default FPM call
# - FPM_DEFAULTS_CONNECT: Default FPM build parameter for connect

FPM_DEB="-t deb --python-easyinstall easy_install3"
INSTALL_SCRIPT_PATH="/build/connect/build/ubuntu/xenial"

if [[ $ARCH == "x86_64" ]]; then
  ${FPM_DEFAULTS}  ${FPM_DEB} ${FPM_DEFAULTS_CONNECT} \
     --after-install ${INSTALL_SCRIPT_PATH}/connect-after-install.sh \
     --before-remove ${INSTALL_SCRIPT_PATH}/connect-before-remove.sh \
    connect/setup.py
fi

if [[ $ARCH == "i386" ]]; then
  echo "i386 not yet implemented!" >&2; exit 254
fi
