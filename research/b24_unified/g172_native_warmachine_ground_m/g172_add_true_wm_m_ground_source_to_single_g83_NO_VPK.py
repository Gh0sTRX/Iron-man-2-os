#!/usr/bin/env python3
"""G172: source-verified ten WM Aim_M_Ground animations through existing G83
single actor/IM2V renderer. No assumed M weapon semantics, no VPK.
Run only AFTER G165 and G171 have patched work/ in G171 CI assembly.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/"work"
G=W/"b24/b24_unified/b24_g83_unified_movement_aim.c"
CM=W/"CMakeLists.txt"
MAIN=W/"src/main.c"
HEADER=W/"b24/b24_unified/b24_g172_wm_ground_m_source.h"
BANK=Path(__file__).with_name("b24_g172_wm_ground_m_source.h")
CATALOG=ROOT/"research/B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md"
SOURCE={
 "Warmachine_Aim_M_Ground_idle.anim":1600,
 "Warmachine_Aim_M_Ground_idle_Att.anim":1600,
 "Warmachine_Aim_M_Ground_move_F.anim":1600,
 "Warmachine_Aim_M_Ground_move_F_Att.anim":866,
 "Warmachine_Aim_M_Ground_move_B.anim":1600,
 "Warmachine_Aim_M_Ground_move_B_Att.anim":1399,
 "Warmachine_Aim_M_Ground_move_L.anim":1600,
 "Warmachine_Aim_M_Ground_move_L_Att.anim":866,
 "Warmachine_Aim_M_Ground_move_R.anim":1600,
 "Warmachine_Aim_M_Ground_move_R_Att.anim":866,
}
def one(text,old,new):
 count=text.count(old)
 if count!=1:
  raise ValueError(f"G172 source drift: exact anchor count {count}: {old[:100]!r}")
 return text.replace(old,new,1)
def apply():
 for file in (G,CM,MAIN,BANK,CATALOG):
  if not file.is_file():raise FileNotFoundError(str(file))
 native=CATALOG.read_text()
 for name,ms in SOURCE.items():
  if f"| `{name}` | {ms} |" not in native:
   raise ValueError(f"G172 mismatch to ORIGINAL B18 source inventory: {name} {ms}")
 code=G.read_text();cm=CM.read_text();main=MAIN.read_text()
 if "B24_G172_WM_NATIVE_M_GROUND_BANK" in cm:
  raise ValueError("already G172")
 for flag in ("B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK",
              "B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL",
              "B24_G85_NATIVE_MARKV_629"):
  if flag not in cm:raise ValueError("G172 original single Vita game prerequisite missing "+flag)
 if main.count("b24_g83_timeline_tick(")!=1 or main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G172 must preserve exactly ONE authored G83 animator and B14 physics")
 code=one(code,
  '#include "b24_g83_authentic_2010_source_durations.h"',
  '#include "b24_g83_authentic_2010_source_durations.h"\n#ifdef B24_G172_WM_NATIVE_M_GROUND_BANK\n#include "b24_g172_wm_ground_m_source.h"\n#endif')
 code=one(code,
  '''   if(aim!=B24G83_AIM_NONE){
    stem=(fire?wm_ground_aim_fire:wm_ground_aim)[dir];''',
  '''#ifdef B24_G172_WM_NATIVE_M_GROUND_BANK
   /* 10 actual 2010 War Machine Aim_M_Ground native clips. Unlike old
    * generic WM Ground aimed fallback, route authored M bank to the
    * G83/G8 owner. M is an UNKNOWN native weapon meaning; do not
    * assign missiles/gatling or change B16 accepted-fire authority. */
   if(aim==B24G83_AIM_M_UNCLASSIFIED)
    stem=b24_g172_wm_m_ground_clip((unsigned)dir,fire);
   else
#endif
   if(aim!=B24G83_AIM_NONE){
    stem=(fire?wm_ground_aim_fire:wm_ground_aim)[dir];''')
 code=one(code,
  ' out->original_source_duration_ms=b24_g83_authentic_source_duration(stem);',
  ''' out->original_source_duration_ms=b24_g83_authentic_source_duration(stem);
#ifdef B24_G172_WM_NATIVE_M_GROUND_BANK
 if(wm&&ground&&aim==B24G83_AIM_M_UNCLASSIFIED)
  out->original_source_duration_ms=b24_g172_wm_m_ground_duration(stem);
#endif''')
 cm+="""

# G172: B18 verified ten authored original 2010 WM Aim_M_Ground source
# clips + durations, integrated into SINGLE G83/G8 animation renderer.
# 'M' Gameloft weapon input semantics remain unverified; no invented
# projectile, attack window, root displacement, stage2/RUSH fire or VPK.
option(B24_G172_WM_NATIVE_M_GROUND_BANK "Real original WM M grounded pose and accepted-fire animation bank" OFF)
if(B24_G172_WM_NATIVE_M_GROUND_BANK)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER OR NOT B24_G85_NATIVE_MARKV_629)
  message(FATAL_ERROR "G172 requires source one-G83 original motion owner")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G172_WM_NATIVE_M_GROUND_BANK=1)
endif()
"""
 if list(W.rglob("*.vpk")):raise RuntimeError("G172 strict NO VPK")
 shutil.copyfile(BANK,HEADER)
 G.write_text(code);CM.write_text(cm)
 print("G172 PASS 10 original 2010 WM M-ground native bank source durations and one G83 animator; B14 movement unchanged; NO VPK")
if __name__=="__main__":apply()
