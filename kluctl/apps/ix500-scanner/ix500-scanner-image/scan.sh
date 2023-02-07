#!/bin/bash

#set -e

cd /pdfs

OUT_DIR=./tiffs
SCAN_NAME=scan_`date +%Y-%m-%d-%H%M%S`

mkdir -p $OUT_DIR/$SCAN_NAME

echo 'scanning...'
if scanimage --resolution 300 \
  --batch="$OUT_DIR/$SCAN_NAME/scan_%03d.tif" \
  --format=tiff \
  --mode Color \
  --source 'ADF Duplex' \
  --page-height 298 -y 298; then
  touch $OUT_DIR/$SCAN_NAME/.scan-done
fi
