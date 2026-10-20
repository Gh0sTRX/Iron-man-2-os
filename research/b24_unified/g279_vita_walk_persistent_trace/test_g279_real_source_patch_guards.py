#!/usr/bin/env python3
"""Negative + positive synthetic source fixture: install G279 once, no
actor / collision / GPU control path changes. Actual Vita ARM link uses
full original-game workflow separately; synthetic test is NOT that proof.
"""
import importlib.util, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("g279",HERE/"g279_install_file_trace_after_G278_one_Vita_game_NO_VPK.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixtures(root:Path):
 work=root/"work";(work/"src").mkdir(parents=True)
 (work/"b24/b24_unified").mkdir(parents=True)
 m=work/"src/main.c"
 m.write_text('''
#include "../b24/b24_unified/b24_g277_real_c1l1_ground_reject_reasons.h"
G278_INITIAL_BOOT_WORLD B24G229WalkWindow G277_GROUND_REJECTION_BREAKDOWN
B24_G227_WALK_ROOT_DIAGNOSTIC g278_has_native_floor
b24_original_walls b24_g74_near_original_floor(
unsigned g278_boot_sample_count=0u;
b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)
b24_g75_capsule_reconcile(
b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)
b24_g8_motion_tick_g84(
++g278_boot_sample_count;
b24_g229_window_reset(&b24_g229_window);
''')
 (work/"CMakeLists.txt").write_text('''
B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL
B24_G227_WALK_ROOT_DIAGNOSTIC B24_G75_SOURCE_CAPSULE
''')
 return m

with tempfile.TemporaryDirectory(prefix="g279_exact_vita_no_vpk_") as t:
 root=Path(t);m=fixtures(root)
 before=m.read_text()
 mod.install(root)
 after=m.read_text()
 for original in (
  "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
  "b24_g75_capsule_reconcile(",
  "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)",
  "b24_g8_motion_tick_g84("
 ):
  assert before.count(original)==after.count(original)==1,original
 assert after.count("b24_g279_trace_write(")==2
 assert after.count("b24_g279_trace_open(")==1
 assert after.count("g279_win.has_native_floor=")==1
 assert after.count("b24_g74_near_original_floor(&b24_original_walls,")==1
 assert "world.x,world.y,world.z,&g279_win.native_floor_z" in after
 assert 'B24_G279_WALK_TRACE_FILE' in (root/"work/CMakeLists.txt").read_text()
 assert (root/"work/b24/b24_unified/b24_g279_walk_trace.h").is_file()
 assert not list((root/"work").rglob("*.vpk"))
 try:
  mod.install(root)
  raise AssertionError("Double insertion must fail")
 except ValueError as e:
  assert "duplicate" in str(e),e
with tempfile.TemporaryDirectory(prefix="g279_fail_closed_") as t:
 root=Path(t);m=fixtures(root)
 m.write_text(m.read_text().replace("g278_has_native_floor","MISSING_TRUE_G278_FLOOR"))
 try:
  mod.install(root)
  raise AssertionError("Missing original boot floor source must fail")
 except ValueError as e:
  assert "G278" in str(e) or "g278" in str(e),e
 with_file=root/"work"/"existing_test.vpk"
 with_file.write_text("DO NOT TOUCH")
 try:
  mod.install(root)
  raise AssertionError("VPK presence must fail")
 except ValueError as e:
  assert "VPK" in str(e),e
with tempfile.TemporaryDirectory(prefix="g296_reject_missing_true_G66C_floor_") as t:
 root=Path(t);m=fixtures(root)
 m.write_text(m.read_text().replace("b24_g74_near_original_floor(","NO_G66C_SOURCE_FLOOR("))
 try:
  mod.install(root)
  raise AssertionError("Missing authentic G66C floor owner must fail")
 except ValueError as e:
  assert "b24_g74_near_original_floor" in str(e),e
print("G296 PASS G279 one-source Vita diagnostic with CURRENT 120-frame original G66C floor, guarded original source, NO VPK")
