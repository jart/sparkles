#!/bin/bash

VERSION="$1"
[[ $VERSION ]] || VERSION="2.4.10"

apt-get install -y build-essential g++ openssl libssl-dev

pushd /usr/src
[[ -f node-v$VERSION.tar.gz ]] || wget http://nodejs.org/dist/v$VERSION/node-v$VERSION.tar.gz
[[ -d node-v$VERSION ]] || tar xzf node-v$VERSION.tar.gz
pushd node-v$VERSION
./configure --openssl-libpath=/usr/lib/ssl || exit $?
make -j4 || exit $?
make install || exit $?
popd
popd
