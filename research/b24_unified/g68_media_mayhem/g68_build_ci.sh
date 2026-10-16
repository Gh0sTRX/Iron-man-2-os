#!/usr/bin/env bash
set -euo pipefail
# G68 reproduces the LAST source-proven G65 city + G59 original collision
# and replaces Mark VI with original owner-owned Mark V suitcase.bdae.
# This is an independent mission slice, NOT complete original CLARA/Lua.
cd "${GITHUB_WORKSPACE:-.}"
ROOT=research/b24_unified
OUT="$ROOT/g68_media_mayhem/build_src"
WORK=/tmp/g68_private_source
mkdir -p "$OUT/assets" "$WORK/previous" "$WORK/native" "$WORK/owner"
cleanup(){ rm -rf "$WORK/owner" "$WORK/native" "$WORK/previous"; }
trap cleanup EXIT
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 "$ROOT/g68_media_mayhem/test_g68_mission.c" -lm -o /tmp/g68_mission
/tmp/g68_mission
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 "$ROOT/g66_playable/test_g67_collision.c" -lm -o /tmp/g68_collision
/tmp/g68_collision
python3 -m py_compile "$ROOT/g68_media_mayhem/g68_pack_source_mark_v.py" "$ROOT/g68_media_mayhem/g68_assemble.py"
python3 -m pip install -q numpy pillow trimesh scipy texture2ddecoder gdown
gh run download 38872391947 --repo "${GITHUB_REPOSITORY:-Gh0sTRX/Iron-man-2-os}" \
 -n G64_REAL_SOURCE_BRES_20457_NATIVE_UV_PVR_WEBGL2_GLB_JSON_NO_VPK \
 -D "$WORK/previous"
test -s "$WORK/previous/G64_SOURCE_REAL_UV_PVR_RECOVERED_VIEWER.html"
gdown '1bjkPiM9WvU_WrzIaUUnx-Lq3bnyJTE0I' -O "$WORK/owner/original.ipa" ||
gdown '131--LA4lrPKxpieS6LFKftIpkMY8YWsA' -O "$WORK/owner/original.ipa"
test "$(wc -c <"$WORK/owner/original.ipa")" -eq 248613763
python3 "$ROOT/g66_playable/g66_rebuild_owner_g65.py" \
 --g64html "$WORK/previous/G64_SOURCE_REAL_UV_PVR_RECOVERED_VIEWER.html" \
 --b11zip research/B11_C1L1_Source_Parser.zip \
 --ipa "$WORK/owner/original.ipa" --out "$WORK/native"
python3 "$ROOT/b24_g59_native_2010_C1L1_collision_original_source_audit.py" \
 --zip research/B11_C1L1_Source_Parser.zip \
 --json "$WORK/native/G59_COLLISION_EVIDENCE.json" \
 --glb "$WORK/native/G59_original_collision.glb"
python3 - "$WORK/native/mark_vi_placeholder.glb" <<'PY'
import sys,zipfile
with zipfile.ZipFile('research/B11_C1L1_Source_Parser.zip') as z:
 open(sys.argv[1],'wb').write(z.read('assets/Iron_man_mark6_textured.glb'))
PY
python3 "$ROOT/g66_playable/g66_pack_scene.py" \
 --g65glb "$WORK/native/G65_C1L1_SOURCE_FVF24_REAL_PVR_UV.glb" \
 --mark6glb "$WORK/native/mark_vi_placeholder.glb" \
 --collisionglb "$WORK/native/G59_original_collision.glb" \
 --out "$OUT/assets"
python3 "$ROOT/g68_media_mayhem/g68_pack_source_mark_v.py" \
 --ipa "$WORK/owner/original.ipa" --out "$OUT/assets"
python3 "$ROOT/g68_media_mayhem/g68_assemble.py" \
 --src "$ROOT/g66_playable" --dst "$OUT"
python3 - "$OUT/assets" <<'PY'
import json,struct,sys
from pathlib import Path
a=Path(sys.argv[1])
j=json.loads((a/'G68_MARK_V_SOURCE_PROVENANCE.json').read_text())
assert j['original_player_BRES']=='suitcase.bdae'
assert j['genuine_weighted_body_vertices']==629
assert len(j['original_authored_motion_clips'])==7
assert j['source_inverse_bind_error']<.0002
assert len(list(a.glob('G66_city_tex_*.g66t')))==31
assert len(list(a.glob('G66_armor_tex_*.g66t')))==1
assert struct.unpack_from('<4I',(a/'G66_city.g66m').read_bytes(),4)==(1,67323,32,31)
(a/'G66_manifest.json').unlink()
print('G68 VERIFIED authentic source MarkV 629 skinned verts; 7 original motion samples')
PY
# The original IPA is not in the VPK and is never committed.
rm -rf "$WORK/owner"
docker run --rm -v "$PWD:/workspace" \
 -w "/workspace/$OUT" vitasdk/vitasdk:2026.08 sh -lc \
 'cmake -S . -B build-vita -DCMAKE_TOOLCHAIN_FILE="$VITASDK/share/vita.toolchain.cmake" -DCMAKE_BUILD_TYPE=Release && cmake --build build-vita --parallel 4'
VPK="$OUT/build-vita/IronMan2_B24_G68_MarkV_Expo_Combat.vpk"
test -s "$VPK"
unzip -t "$VPK" | tail -2
python3 - "$VPK" <<'PY'
import struct,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
 paths=set(z.namelist())
 assert b'IM2G68001' in z.read('sce_sys/param.sfo')
 assert len(z.read('eboot.bin'))>25000
 assert all('assets/'+p in paths for p in ('G66_city.g66m','G66_armor.g66m',
  'G66_original_collision.g66c','G68_suitcase_motion.g68a','G68_armor_mapping.g68i'))
 assert len([x for x in paths if x.endswith('.g66t')])==32
 assert struct.unpack_from('<4sIII',z.read('assets/G68_suitcase_motion.g68a'))==(b'G68A',1,629,7)
 assert not any(x.endswith(('.ipa','.bdae','.bclara')) for x in paths)
 print('G68 REAL VitaSDK VPK integrity validated, hardware FPS not tested')
PY
