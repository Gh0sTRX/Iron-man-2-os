#!/usr/bin/env python3
"""G301 G169 integration regression: synthetic ONE B24 source skeleton only.
No original IPA, no actual Vita gameplay/VPK. Real G171 rebuild is separate.
"""
import importlib.util
from pathlib import Path
import tempfile
HERE=Path(__file__).resolve().parent
PATH=HERE/"g169_integrate_accepted_B16_to_original_2010_three_phase_beam_G168_one_game_NO_VPK.py"
spec=importlib.util.spec_from_file_location("g169_source",PATH)
patch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
OLD="g84_last_flight_dir=world.flying?g84_route.direction:B24G83_DIR_IDLE;"
NEW="g84_last_flight_dir=b24_g83_physical_flight_dir(\n                g84_input.motion,g84_input.axis_x,g84_input.axis_y);"
BASE='''#include "../b24/b24_unified/b24_g75_source_capsule.h"
void synthetic_owner_only(void){
 b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
 int fired=b16_combat_fire(&combat,&world,muzzle);
 b24_g83_timeline_tick(&g84_time,NULL,(uint32_t)now,&g84_input,&g84_route);
 '''+NEW+'''
 if(!b24_g8_motion_tick_g84(&b24_original_motion,
      "app0:animations",model.vertices,sizeof(IM2Vertex),
      model.nv,idx,original_stage,move_x,move_y,
      (uint32_t)now,g84_route.stem)){running=0;break;}
}
'''
def build(work,game):
 p=work/"src/main.c"
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(game)
 cm=work/"CMakeLists.txt"
 cm.write_text("B24_G168_ORIGINAL_SUIT_RENDER_FOOT\n"+
               "B24_G84_ORIGINAL_MOVESET_ROUTER\n"+
               "B24_G85_NATIVE_MARKV_629\n"+
               "B24_G75_SOURCE_CAPSULE\n")
 (work/"b24/b24_unified").mkdir(parents=True,exist_ok=True)
 (work/"b24/b24_unified/b24_g8_live_original_motion.c").write_text("/* synthetic fixture */\n")
 patch.W=work
 patch.M=p
 patch.CM=cm
 patch.D=work/"b24/b24_unified"
 return p,cm
with tempfile.TemporaryDirectory(prefix="g301_g169_valid_") as d:
 p,cm=build(Path(d)/"work",BASE)
 patch.apply()
 game=p.read_text()
 assert game.count(NEW)==1
 assert OLD not in game
 assert game.count("b24_g169_native_beam_begin(")==1
 assert game.count("b24_g169_native_beam_clip(")==1
 assert game.index("b24_g83_timeline_tick(")<game.index("b24_g169_native_beam_clip(")
 assert game.index("b24_g169_native_beam_clip(")<game.index(NEW)
 assert game.index(NEW)<game.index("b24_g8_motion_tick_g84(")
 assert "B24_G169_AUTHENTIC_BEAM_3_PHASE" in cm.read_text()
 assert not list((Path(d)/"work").rglob("*.vpk"))
 try:
  patch.apply()
  raise AssertionError("duplicate source install must be rejected")
 except ValueError as e:
  assert "duplicate" in str(e)
with tempfile.TemporaryDirectory(prefix="g301_g169_legacy_") as d:
 p,cm=build(Path(d)/"work",BASE.replace(NEW,OLD))
 try:
  patch.apply()
  raise AssertionError("stale G84 feedback must fail closed")
 except ValueError as e:
  assert "stale" in str(e)
 assert cm.read_text().count("B24_G169_AUTHENTIC_BEAM_3_PHASE")==0
print("G301 PASS G169 true selection -> Beam -> B14 physical direction -> G8 path; old visual-direction feedback fails closed. Synthetic integration only, NO VPK")
