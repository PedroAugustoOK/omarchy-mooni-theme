#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

background="#FFF9E8"
foreground="#302713"
accent="#8A5A00"
canvas_w=3840
canvas_h=2160
# Match the official Omarchy wordmark wallpaper proportions (1600x376 on a
# 3840x2160 canvas). Rasterize at 2x and downsample for cleaner antialiasing.
wordmark_w=1600
wordmark_h=376
wordmark_render_w=$((wordmark_w * 2))
wordmark_render_h=$((wordmark_h * 2))

command -v magick >/dev/null
command -v rsvg-convert >/dev/null
test -f /usr/share/omarchy/logo.svg
test -f assets/unlock-source.png

work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

# Normalize both Mooni variants to the midpoint between their original visible
# bounds. A shared 800x400 canvas also keeps Plymouth's password field aligned.
magick assets/unlock-source.png -trim +repage -resize '344x234' \
  -gravity center -background none -extent 800x400 -strip unlock.png

rsvg-convert -w "$wordmark_render_w" -h "$wordmark_render_h" /usr/share/omarchy/logo.svg -o "$work_dir/wordmark-hi.png"
magick "$work_dir/wordmark-hi.png" -resize "${wordmark_w}x${wordmark_h}" "$work_dir/wordmark.png"
magick "$work_dir/wordmark.png" -channel RGB +level-colors "$accent","$accent" "$work_dir/wordmark.png"
magick -size "${canvas_w}x${canvas_h}" "xc:$background" \
  "$work_dir/wordmark.png" -gravity center -composite \
  -depth 8 -strip backgrounds/04-omarchy-wordmark.png

for asset in bullet.png entry.png lock.png; do
  cp "/usr/share/omarchy/default/plymouth/$asset" "$work_dir/$asset"
  magick "$work_dir/$asset" -channel RGB +level-colors "$foreground","$foreground" "$work_dir/$asset"
done

logo_w=$(magick identify -format '%w' unlock.png)
logo_h=$(magick identify -format '%h' unlock.png)
entry_w=$(magick identify -format '%w' "$work_dir/entry.png")
entry_h=$(magick identify -format '%h' "$work_dir/entry.png")
lock_h=$((entry_h * 8 / 10))
lock_w=$((84 * lock_h / 96))
logo_x=$(((1920 - logo_w) / 2))
logo_y=$(((1080 - logo_h) / 2))
entry_x=$(((1920 - entry_w) / 2))
entry_y=$((logo_y + logo_h + 40))
lock_x=$((entry_x - lock_w - 15))
lock_y=$((entry_y + entry_h / 2 - lock_h / 2))
bullet_y=$((entry_y + entry_h / 2 - 4))

set --
for index in 0 1 2 3; do
  bullet_x=$((entry_x + 20 + index * 12))
  set -- "$@" \( "$work_dir/bullet.png" -resize 7x7 \) -geometry "+${bullet_x}+${bullet_y}" -composite
done

magick -size 1920x1080 "xc:$background" \
  unlock.png -geometry "+${logo_x}+${logo_y}" -composite \
  "$work_dir/entry.png" -geometry "+${entry_x}+${entry_y}" -composite \
  \( "$work_dir/lock.png" -resize "${lock_w}x${lock_h}" \) -geometry "+${lock_x}+${lock_y}" -composite \
  "$@" -depth 8 -strip preview-unlock.png
