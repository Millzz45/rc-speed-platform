#!/bin/sh
# Rebuild every printed part from the CAD scripts and refresh stl/.
#   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
#   tools/rebuild.sh
# Needs about 1.5 GB of RAM and 15-20 minutes. Output: out/ (scratch, git-ignored) and stl/ (the shipped STLs).
set -e
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
(cd cad && ../$PY build_all.py)
mkdir -p stl
cp out/stl/*.stl stl/
cp out/parts.json out/anchors.json stl/
# the GT-2 body: built round the chassis above (every part checked for fit, bed and overlap)
(cd cad && ../$PY body_gt2.py)
mkdir -p stl/body_gt2
cp out/body_gt2/stl/*.stl stl/body_gt2/
cp out/body_gt2/parts.json stl/body_gt2/
echo "stl/: $(ls stl/*.stl | wc -l | tr -d ' ') chassis STLs, $(ls stl/body_gt2/*.stl | wc -l | tr -d ' ') body STLs"
