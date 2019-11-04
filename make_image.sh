#!/bin/sh

# ./make_image.sh "quote" "profile.jpg" "result.jpg"

OUT=`python3 wordwrap.py "$1"`

echo "$OUT"

convert \
  -background black \
  -fill white \
  -font "Arial" \
  -pointsize 80 \
  -bordercolor Black \
  -border 20x0 \
  label:"$OUT" \
  image.png

convert \
  -background black \
   xc:none \
   image.png -append \
   "$2" \
  -gravity center \
  +append \
  +repage \
  -colorspace Gray \
  -bordercolor Black \
  -border 20x20 \
  "$3"
