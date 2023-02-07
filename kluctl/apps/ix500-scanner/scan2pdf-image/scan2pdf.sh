#!/usr/bin/env bash

set -e

INPUT_DIR=$1
OUTPUT_FILE=$2
TMP_DIR=$INPUT_DIR/tmp

LANGUAGE="deu+eng"

mkdir -p $TMP_DIR

IMAGES=""
for i in $INPUT_DIR/scan_*.tif; do
	if empty-page -i $i &> /dev/null; then
	  echo "Skipping empty page $i"
	else
		IMAGES="$IMAGES $i"
	fi
done

echo "Converting images ($IMAGES) to $TMP_DIR/scan.pdf"
img2pdf $IMAGES > $TMP_DIR/scan.pdf

echo "Calling ocrmypdf"
ocrmypdf -l $LANGUAGE $TMP_DIR/scan.pdf $TMP_DIR/scan_ocr.pdf

echo "Copying output pdf"
mv $TMP_DIR/scan_ocr.pdf $OUTPUT_FILE
rm -rf $TMP_DIR
