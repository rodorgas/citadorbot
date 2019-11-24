#!/bin/bash

# ./make_image.sh "quote" "name" "profile.jpg" "result.jpg"

QUOTE=`python3 wordwrap.py "$1"`
NAME=$2
PROFILE=$3
RESULT=$4

echo `date`

convert \
  -background black \
  -fill white \
  -font "Noto Color Emoji" \
  -pointsize 80 \
  -bordercolor Black \
  -border 30x10 \
  -style Italic \
  label:"\“$QUOTE\” " \
  "${RESULT}-quote.png"

convert \
  -background black \
  -fill white \
  -font "Arial" \
  -pointsize 40 \
  -bordercolor Black \
  -border 30x10 \
  label:"$NAME" \
  "${RESULT}-name.png"

convert \
  -background black \
   xc:none \
  "${RESULT}-quote.png" -append \
  "${RESULT}-name.png" \
  -gravity SouthEast \
  -append \
  +repage \
  -colorspace Gray \
  -bordercolor Black \
  -border 20x20 \
  "${RESULT}-namequote.png"

convert \
  -background black \
   xc:none \
  "${RESULT}-namequote.png" -append \
   "$PROFILE" \
  -gravity center \
  +append \
  +repage \
  -colorspace Gray \
  -bordercolor Black \
  -border 20x20 \
  "$RESULT"

rm "${RESULT}-quote.png"
rm "${RESULT}-name.png"
rm "${RESULT}-namequote.png"
