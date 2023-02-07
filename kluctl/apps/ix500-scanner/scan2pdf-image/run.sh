#!/usr/bin/env bash

function sigterm() {
    echo "Got SIGTERM"
    exit
}

trap sigterm SIGTERM

function process_scan() {
	if [ ! -f "$1/$DONE_MARKER" ]; then
		n=`basename "$1"`
		echo "Processing $n..."
		scan2pdf.sh "$1" "$OUTPUT_DIR/$n.pdf"
		SUCCESS=$?
		touch "$1/$DONE_MARKER"
		if [ "$SUCCESS" = "0" ]; then
			mv "$1" "$ARCHIVE_DIR"/
		fi
	fi
}

mkdir -p $OUTPUT_DIR
mkdir -p $ARCHIVE_DIR

while true; do
  find $INPUT_DIR -name $START_MARKER | while read file; do
  	d=`dirname "$file"`
  	process_scan "$d"
  done
  sleep 1
done
