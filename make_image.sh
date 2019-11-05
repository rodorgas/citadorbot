#!/bin/sh

# ./make_image.sh "quote" "name" "profile.jpg" "result.jpg"

OUT=`python3 wordwrap.py "$1"`

echo "$OUT"

convert \
  -background black \
  -fill white \
  -font "Arial" \
  -pointsize 80 \
  -bordercolor Black \
  -border 30x0 \
  -style Italic \
  label:"\“$OUT\”" \
  quote.png

convert \
  -background black \
  -fill white \
  -font "Arial" \
  -pointsize 40 \
  -bordercolor Black \
  -border 30x10 \
  label:"$2" \
  name.png

convert \
  -background black \
   xc:none \
   quote.png -append \
   name.png \
  -gravity SouthEast \
  -append \
  +repage \
  -colorspace Gray \
  -bordercolor Black \
  -border 20x20 \
  image.png

convert \
  -background black \
   xc:none \
   image.png -append \
   "$3" \
  -gravity center \
  +append \
  +repage \
  -colorspace Gray \
  -bordercolor Black \
  -border 20x20 \
  "$4"
