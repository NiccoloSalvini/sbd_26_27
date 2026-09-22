#!/usr/bin/env bash
# Does the setup line on the Setup page actually work? Run it on clean machines
# and see, instead of assuming.
#
#   ./run.sh              quick: script logic on three R versions, no downloads
#   ./run.sh --full       slow: really install every package on a clean R 4.6
#   ./run.sh --url        use the published script instead of the local file
#
# Covers Linux only. Docker on macOS cannot run Windows containers, and macOS
# itself cannot be containerised at all — see README.md in this folder.
set -u
cd "$(dirname "$0")"
REPO=$(cd ../.. && pwd)

FULL=0; USE_URL=0
for a in "$@"; do
  case "$a" in
    --full) FULL=1 ;;
    --url)  USE_URL=1 ;;
    *) echo "unknown flag: $a"; exit 2 ;;
  esac
done

if [ "$USE_URL" = 1 ]; then
  SRC="https://sbd-26-27.netlify.app/materials/setup.R"; MOUNT=()
else
  SRC="/work/materials/setup.R"; MOUNT=(-v "$REPO:/work:ro")
fi

if [ "$FULL" = 1 ]; then
  IMAGES=("rocker/r-ver:4.6.0"); MODE=""; LABEL="full install"
else
  IMAGES=("rocker/r-ver:4.6.0" "rocker/r-ver:4.5.1" "rocker/r-ver:4.4.1")
  MODE="-e MOCK=1"; LABEL="logic only"
fi

rc=0
for img in "${IMAGES[@]}"; do
  echo
  echo "======================================================================"
  echo "  $img   ($LABEL, source: $SRC)"
  echo "======================================================================"
  # linux/amd64: the package manager serves Linux binaries for that arch, so a
  # full run takes minutes rather than an hour of compiling on arm64
  docker run --rm --platform linux/amd64 $MODE \
    "${MOUNT[@]}" -v "$PWD/assert.R:/assert.R:ro" \
    "$img" Rscript /assert.R "$SRC"
  status=$?
  if [ $status -ne 0 ]; then echo ">>> $img FAILED (exit $status)"; rc=1; fi
done

echo
if [ $rc -eq 0 ]; then echo "ALL GREEN"; else echo "SOMETHING FAILED — see above"; fi
exit $rc
