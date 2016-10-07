#!/bin/bash
# This scripts builds the connect package
# Required env variables:
# - ARCH: Build architecture
# - GPG_KEY: Signing key for GPG

# Prolog
pushd /build/dist >/dev/null

# Import GPG signing key
gpg --import <<__EOF__
${GPG_KEY}
__EOF__

#TODO Check if this is a repository; if not, warn and ask to create one.

###############################################################################
# Create repository index
###############################################################################

mkdir -p pool/conf

cp /build/dist_all_ro/connect/*.deb /build/dist_all_ro/requirements/*.deb .
dpkg-sig --sign builder *.deb

cat <<'__EOF__' > pool/conf/distributions
Origin: pool.openhsr.ch
Label: openHSR Ubuntu Xenial Pool
Suite: xernial
Codename: xenial
Version: 16.04
Architectures: i386 amd64 source
Components: main
Description: openHSR Ubuntu Xenial Pool
SignWith: Yes
__EOF__

reprepro -Vb pool export
#bash
find . -maxdepth 1 -name '*.deb' | xargs reprepro -Vb pool includedeb xenial

# Fine.
popd >/dev/null
