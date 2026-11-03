#!/usr/bin/env bash
# Rebuild both courses and the home page, and put them in the folders the Desktop version uses.
# Needs Python 3 with no extra packages. Run from anywhere: bash source/build_all.sh
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(dirname "$SRC")"
(cd "$SRC/course1" && python3 build.py --public >/dev/null)
(cd "$SRC/course2" && python3 build.py >/dev/null)
(cd "$SRC/home" && python3 build_home.py >/dev/null)
install() {
  mkdir -p "$2"; cp "$1"/*.html "$2/"; mv "$2/index.html" "$2/START HERE.html"
  for f in "$2"/*.html; do sed -i.bak 's#href="index.html"#href="START HERE.html"#g' "$f" && rm "$f.bak"; done
}
install "$SRC/course1/public_dist" "$ROOT/1 How SPAM DVC Works"
install "$SRC/course2/dist" "$ROOT/2 SPAM Commands"
cp "$SRC/home/dist/home.html" "$ROOT/START HERE.html"
echo "Rebuilt. Open: $ROOT/START HERE.html"
