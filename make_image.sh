#!/bin/bash

<<<<<<< HEAD
# ./make_image.sh "quote" "name" "profile.jpg" "result.jpg"
=======
# ./make_image.sh "quote" "name" "context" "profile.jpg" "result.jpg"
>>>>>>> a251422... Add context to quotes

set -e

QUOTE=`python3 wordwrap.py "$1"`
NAME=$2
<<<<<<< HEAD
PROFILE=$3
RESULT=$4
=======
PROFILE=$4
RESULT=$5
>>>>>>> a251422... Add context to quotes

echo `date`

convert \
  -background black \
  -fill white \
  -pointsize 80 \
  -bordercolor Black \
  -border 30x10 \
  -style Italic \
  label:"\“$QUOTE\”" \
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
   xc:none \
  "${RESULT}-quote.png" -append \
  "${RESULT}-name.png" \
  -gravity SouthEast \
  -append \
  +repage \
  -bordercolor Black \
  -border 20x20 \
  "${RESULT}-namequote.png"

convert \
  "$PROFILE" \
  -colorspace Gray \
  "$PROFILE-black.png"

convert \
  -background black \
   xc:none \
  "${RESULT}-namequote.png" -append \
   "$PROFILE-black.png" \
  -gravity center \
  +append \
  +repage \
  -bordercolor Black \
  -border 20x20 \
  "$RESULT"

rm "${RESULT}-quote.png"
rm "${RESULT}-name.png"
rm "${RESULT}-namequote.png"
rm "${PROFILE}-black.png"
