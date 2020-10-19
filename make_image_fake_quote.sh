#!/bin/bash

# ./make_image.sh "quote" "name" "profile.jpg" "result.jpg"

set -e

QUOTE=`python3 wordwrap.py "$1"`
NAME=$2
PROFILE=$3
FAKER=$4
RESULT=$5

echo `date`

convert \
  -background black \
  -fill white \
  -pointsize 80 \
  -bordercolor Black \
  -border 30x10 \
  -style Italic \
  pango:"<span font=\"Twitter-Color-Emoji-SVGinOT\"><i>\“$QUOTE\”</i></span>" \
  "${RESULT}-quote.png"

convert \
  -background black \
  -fill white \
  -pointsize 40 \
  -bordercolor Black \
  -border 30x10 \
  label:"$NAME" \
  "${RESULT}-name.png"

convert \
  -background black \
  -fill white \
  -pointsize 18 \
  -bordercolor Black \
  -border 30x10 \
  label:"$FAKER" \
  "${RESULT}-faker.png"

convert \
  -background black \
   xc:none \
  "${RESULT}-quote.png" -append \
  "${RESULT}-name.png" -append \
  "${RESULT}-faker.png" \
  -gravity SouthEast \
  -append \
  +repage \
  -bordercolor Black \
  -border 20x20 \
  "${RESULT}-namequotefaker.png"

convert \
  "$PROFILE" \
  -colorspace Gray \
  -resize 500x500 \
  "$PROFILE-black.png"

convert \
  -background black \
   xc:none \
  "${RESULT}-namequotefaker.png" -append \
   "$PROFILE-black.png" \
  -gravity center \
  +append \
  +repage \
  -bordercolor Black \
  -border 20x20 \
  "$RESULT"

rm "${RESULT}-quote.png"
rm "${RESULT}-name.png"
rm "${RESULT}-namequotefaker.png"
rm "${RESULT}-faker.png"
rm "${PROFILE}-black.png"
