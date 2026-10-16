#!/usr/bin/env python3
"""Replay ONLY the verified G9 source assembly step with G70 native G68 scene.
Then inject opt-in G75 speed, camera and capsule changes. NEVER invoke
vita packaging, CMake/VPK build or the remaining G9 steps.
B24 remains the sole gameplay owner; source-only host/Vita ARM QA.
"""
from pathlib import Path
import importlib.util,subprocess,os
R=Path(__file__).resolve().parents[3]
p=R/'research/b24_unified/g70_reverse_merge/g70_replay_g9_workflow.py'
spec=importlib.util.spec_from_file_location('g70_source_replay',str(p))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names=[s.get('name','') for s in m.steps]
assert len(m.steps)>19
matching=[s for s in m.steps if 'Combine known-good viewer and original animation B7' in s.get('name','')]
assert len(matching)==1,'Upstream G9 assembly step missing'
source_script=m.patch_script(matching[0]['run'],matching[0]['name'])
for forbidden in ['cmake --build','vita_create_vpk','zip -q build-vita','actions/upload-artifact']:
    assert forbidden not in source_script, 'Source-only boundary crossed: '+forbidden
assert 'g70_stage_g68_source_scene.py' in source_script
print('G75 starting real G9 B24 source assembly + G68 originals. No Vita packages.',flush=True)
subprocess.run(['bash','-eo','pipefail'],input=source_script,text=True,cwd=R,check=True)
subprocess.run(['python3',str(R/'research/b24_unified/g75_device_qa/g75_apply_to_G70_original_B24_SOURCE_ONLY.py')],
    cwd=R,check=True)
world=(R/'work/src/b14_world.c').read_text()
game=(R/'work/src/main.c').read_text()
cm=(R/'work/CMakeLists.txt').read_text()
assert game.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
assert game.count('b24_g75_capsule_reconcile(')==1
assert '-.92f,1.05f' in world and 'speed_target' in world
assert 'B24_G75_SOURCE_CAPSULE' in cm
assert 'B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE' in cm
assert 'G75_SOURCE_ONLY_GAMEPLAY_RECOVERY' in game
assert not list((R/'work').rglob('*.vpk'))
print('PASS G75 fully reassembled original G9 B24 + verified G68 actual city source + optional G75 collision/flight/lighting; NO VPK',flush=True)
