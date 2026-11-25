#!/bin/bash
# RogueArena helper.  Run from the repository root (edit B to your Blender path):
#   bash source/blender/ra_run.sh <module> [views]        preview renders + stand-in STL + interference check
#   bash source/blender/ra_run.sh <module> finish         full finish (textures, rig, clips, GLB / FBX) on the stand-in STL
#   bash source/blender/ra_run.sh <module> final          full finish on the real Fusion output in out/RA/<NAME>
# <module> is e.g. ra01_sidearm.  Output: out/RA_preview/<module>/ (png), out/RA_standin/<module>/ (stl), .../final
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
M="$1"; MODE="${2:-right,q,top}"
export GUN_MODULE="$M"
unset GUN_NAME GUN_VIEW_SCALE GUN_VIEW_CENTER
FILTER='^(Fra:|Saved|Blender|Info|Timer|$|.*INFO: )'
NAME=$(cd source/fusion/RogueArena && python -c "import $M; print($M.G.NAME)") || exit 1
if [ "$MODE" = "finish" ]; then
  "$B" -b --python source/blender/orbis_finish.py -- source/fusion/RogueArena "out/RA_standin/$M" "out/RA_standin/$M/final" res=2048 2>&1 | grep -vE "$FILTER" | grep -E "BBOX|INTERF|HIT|MESH|BAKE|SITE|OK|DONE|Error|Traceback|rror"
elif [ "$MODE" = "final" ]; then
  "$B" -b --python source/blender/orbis_finish.py -- source/fusion/RogueArena "out/RA/$NAME" "out/RA/$NAME/final" res=2048 2>&1 | grep -vE "$FILTER" | grep -E "BBOX|INTERF|HIT|MESH|BAKE|SITE|OK|DONE|Error|Traceback|rror"
else
  "$B" -b --python source/blender/orbis_preview.py -- source/fusion/RogueArena "out/RA_preview/$M" "$MODE" "out/RA_standin/$M" 2>&1 | grep -vE "$FILTER" | grep -E "BBOX|STANDIN|Error|Traceback|rror|assert"
  "$B" -b --python source/blender/orbis_finish.py -- source/fusion/RogueArena "out/RA_standin/$M" "out/RA_standin/$M/final" checkonly 2>&1 | grep -E "INTERF|HIT|FIRST|Error|Traceback"
fi
