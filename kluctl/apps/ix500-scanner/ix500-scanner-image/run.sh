#!/usr/bin/env bash

set -e

echo TZ=$TZ

if [ -n "$TZ" ]; then
  echo "Setting up localtime"
  ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
  dpkg-reconfigure -f noninteractive tzdata
fi

exec scanbd -d7 -f
