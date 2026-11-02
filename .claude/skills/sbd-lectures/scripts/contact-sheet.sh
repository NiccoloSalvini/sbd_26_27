#!/usr/bin/env bash
# Frames of a clip at the given seconds, tiled two per row, to read a clip at a glance.
# Usage: contact-sheet.sh clip.mp4 out.png 6 20 34 47
set -euo pipefail
clip=$1; out=$2; shift 2
dir=$(mktemp -d)
inputs=(); n=0
for t in "$@"; do
  ffmpeg -v error -y -ss "$t" -i "$clip" -frames:v 1 "$dir/f$n.png"
  inputs+=(-i "$dir/f$n.png"); n=$((n + 1))
done
if (( n % 2 )); then                      # an odd count gets a blank last tile
  ffmpeg -v error -y -f lavfi -i color=c=black:s=1280x720 -frames:v 1 "$dir/f$n.png"
  inputs+=(-i "$dir/f$n.png"); n=$((n + 1))
fi
if (( n == 2 )); then                     # one row: vstack wants at least two inputs
  graph="[0][1]hstack,scale=1600:-1"
else
  rows=""; parts=""
  for ((i = 0; i < n; i += 2)); do
    rows+="[$i][$((i + 1))]hstack[r$i];"; parts+="[r$i]"
  done
  graph="${rows}${parts}vstack=inputs=$((n / 2)),scale=1600:-1"
fi
ffmpeg -v error -y "${inputs[@]}" -filter_complex "$graph" "$out"
rm -rf "$dir"
echo "$out"
