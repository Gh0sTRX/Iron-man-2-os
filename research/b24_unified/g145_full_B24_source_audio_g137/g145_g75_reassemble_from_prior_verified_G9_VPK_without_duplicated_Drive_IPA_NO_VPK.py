#!/usr/bin/env python3
"""G145 physical source-only B24 game rebuild UNBLOCKER.
The old 2010 G9 source assembly unnecessarily re-downloads the SAME
owner 248,613,763-byte original IPA just to generate the 1,048,596-byte
original iOS 2010 C1L1_Vehicles.c1tx. The already SUCCESSFUL ORIGINAL
2010 G9 Vita build *contains* that exact user-owned decoded texture.
Retrieve the existing verified G9 VPK via GitHub Actions artifact, read
just C1TX original converted source and never create a VPK here.
Retain EVERY source-code step, G70 G68 scene, G75 original B14 collision.
No invented replacement, no reencoded fake texture, NO NEW VPK.
"""
from pathlib import Path
import importlib.util,subprocess,zipfile,struct,hashlib,os
R=Path(__file__).resolve().parents[3]
OLD=Path('/tmp/g145_authenticated_previous_G9/IronMan2_GPU_B24_G9_BETA.vpk')
if not OLD.is_file():raise FileNotFoundError('Missing prior successful original user G9 Vita package artifact (read-only)')
with zipfile.ZipFile(OLD) as z:
 if z.testzip():raise ValueError('existing original G9 VPK corrupt')
 name='maps/C1L1_Vehicles.c1tx'
 if name not in z.namelist():raise ValueError('G9 original authenticated asset C1TX not available; no fake fallback')
 original=z.read(name)
if len(original)!=1048596 or struct.unpack_from('<4sIIII',original)!=(b'C1TX',1,512,512,0):
 raise ValueError('previous genuine owner 2010 G9 512px vehicles C1TX original format does not match')
print('G145 reused EXACT original G9 source vehicles C1TX',len(original),
      'SHA256',hashlib.sha256(original).hexdigest(),flush=True)
src=R/'research/b24_unified/g70_reverse_merge/g70_replay_g9_workflow.py'
spec=importlib.util.spec_from_file_location('g70_source_replay',src)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
match=[x for x in m.steps if 'Combine known-good viewer and original animation B7' in x.get('name','')]
if len(match)!=1:raise ValueError('Original G9 one authoritative assembly step expected')
script=m.patch_script(match[0]['run'],match[0]['name'])
start='python3 -m pip install -q gdown texture2ddecoder'
end='rm -rf /tmp/b24g7-owner'
if script.count(start)!=1 or script.count(end)!=1 or script.count('gdown ' )!=1:
 raise ValueError('gdown original owner IPA source script not unique; refuse blind source patch')
i=script.index(start);j=script.index(end,i)+len(end)
stage="""python3 - <<'PYSOURCEG145'
from pathlib import Path
import hashlib,struct,zipfile
original=Path('/tmp/g145_authenticated_previous_G9/IronMan2_GPU_B24_G9_BETA.vpk')
with zipfile.ZipFile(original) as source:
    data=source.read('maps/C1L1_Vehicles.c1tx')
assert len(data)==1048596
assert struct.unpack_from('<4sIIII',data)==(b'C1TX',1,512,512,0)
dest=Path('work/maps/C1L1_Vehicles.c1tx')
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_bytes(data)
print('G145 ORIGINAL-G9-PROVEN iOS VEHICLES C1TX REUSED SHA256',hashlib.sha256(data).hexdigest())
PYSOURCEG145"""
script=script[:i]+stage+script[j:]
if 'gdown ' in script or 'owner.ipa' in script:
 raise ValueError('G145 original IPA re-download remnants not removed')
for forbidden in ('cmake --build','vita_create_vpk','actions/upload-artifact','zip -q build-vita'):
 if forbidden in script:raise ValueError('prohibited package creation in G145 source assembly: '+forbidden)
print('G145 rebuilding sole original G9/G70 B24 source with already-authenticated C1TX from prior G9, no new 2010 IPA download / NO VPK',flush=True)
subprocess.run(['bash','-eo','pipefail'],input=script,text=True,cwd=R,check=True)
subprocess.run(['python3',str(R/'research/b24_unified/g75_device_qa/g75_apply_to_G70_original_B24_SOURCE_ONLY.py')],cwd=R,check=True)
game=(R/'work/src/main.c').read_text()
cm=(R/'work/CMakeLists.txt').read_text()
assert game.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
assert game.count('b24_g75_capsule_reconcile(')==1
assert 'B24_G75_SOURCE_CAPSULE' in cm
assert (R/'work/maps/C1L1_Vehicles.c1tx').read_bytes()==original
assert not list((R/'work').rglob('*.vpk'))
print('G145 G75 real B14 original source reassembled with original G9 C1TX without Google Drive quota, NO NEW VPK',flush=True)
