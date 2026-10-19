#!/usr/bin/env python3
"""G278 source-only smoke/negative tests for exact one-main Vita injection.
The fixture contains only tokens needed to validate guarded insertion and
single-owner flow; Vita ARM ELF CI is a separate real-source test.
"""
from __future__ import annotations
import importlib.util,tempfile
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("g278",here/"g278_install_first_rendered_Vita_world_and_original_G66C_support_probe_NO_VPK.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory(prefix="G278_single_2010_Vita_source_static_") as t:
 r=Path(t);w=r/"work";(w/"src").mkdir(parents=True);(w/"b24/b24_unified").mkdir(parents=True)
 main=w/"src/main.c"
 main.write_text("""B24_G227_WALK_ROOT_DIAGNOSTIC
 B24G229WalkWindow
 G277_GROUND_REJECTION_BREAKDOWN
 b24_original_walls
 B14World world; b14_world_init(&world);world.head_height=b15_suit_head(&model);world.cam_z=world.head_height;
 b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)
 b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)
 b24_g75_capsule_reconcile(
 b24_g227_probe.frame_num=(uint32_t)frame;
 """)
 (w/"CMakeLists.txt").write_text("B24_G75_SOURCE_CAPSULE\nB24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL\n")
 before=main.read_text()
 mod.patch(r)
 after=main.read_text()
 assert after!=before
 assert after.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert after.count("b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)")==1
 assert after.count("b24_g75_capsule_reconcile(")==1
 assert after.count("G278_INITIAL_BOOT_WORLD")==1
 assert after.count("g278_boot_sample_count")==4
 assert after.count("b24_g74_near_original_floor(&b24_original_walls")==1
 assert after.count("b24_g277_last_collision_reasons()")==1
 assert "B14_initial=" in after and "resolved_WORLD=" in after and "GPU_actor=" in after
 assert not list(w.rglob("*.vpk"))
 try:mod.patch(r)
 except ValueError as e:assert "cannot patch source twice" in str(e)
 else:raise AssertionError("G278 erroneously permits duplicate injection")
 main.write_text(before.replace("b24_original_walls","missing_original_C1L1_geo"))
 try:mod.patch(r)
 except ValueError as e:assert "G66C city variable missing" in str(e)
 else:raise AssertionError("G278 emits initial boot without actual original city source")
 print("G278 PASS guarded source-only first three successful real Vita GPU frame hook, native-floor trace and fail-closed on missing G66C; NO VPK")
