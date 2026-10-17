#!/usr/bin/env python3
"""G173 fix concrete G169->G8/G85 dropped UniBeam source pose:
- original Mark V G169 chose suitcase_ironman_* already, while G85
  rejected anything not ironman_* and then rebuilt suitcase_ prefix.
- G8's accepted repulsor pending gate could hide the verified G169
  three-phase Beam1/2/3 clip in the SINGLE live source IM2V animator.
No change to weapon timing, B16 damage, B14 physics, world, G171, or UI.
Only exact 12 source-authored clip stems may override this pose priority.
Not a claim of 2010 native weapon/input semantics. Strict NO VPK.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/"work"
C=W/"b24/b24_unified/b24_g8_live_original_motion.c"
H=W/"b24/b24_unified/b24_g173_authored_beam_priority.h"
CM=W/"CMakeLists.txt"
MAIN=W/"src/main.c"
HERE=Path(__file__).resolve().parent
def one(text,old,new,label):
 n=text.count(old)
 if n!=1:raise ValueError(f"G173 {label} exact owner drift, found {n}: {old[:120]!r}")
 return text.replace(old,new,1)
def patch():
 for f in (C,CM,MAIN,HERE/"b24_g173_authored_beam_priority.h"):
  if not f.is_file():raise FileNotFoundError(str(f))
 s=C.read_text();cm=CM.read_text();main=MAIN.read_text()
 if "B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY" in cm:raise ValueError("G173 already applied")
 for flag in ("B24_G169_AUTHENTIC_BEAM_3_PHASE",
              "B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL",
              "B24_G172_WM_NATIVE_M_GROUND_BANK",
              "B24_G85_NATIVE_MARKV_629"):
  if flag not in cm:raise ValueError("G173 requires previous one-Vita owner "+flag)
 if main.count("b24_g8_motion_tick_g84(")!=1 or main.count("b24_g83_timeline_tick(")!=1:
  raise ValueError("G173 cannot add any new animation owner")
 if main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G173 cannot add any new physics owner")
 if main.count("b24_g169_native_beam_clip(")!=1:
  raise ValueError("G173 requires current authentic G169 source clip provenance")
 s=one(s,'#include "b24_g8_live_original_motion.h"',
 '''#include "b24_g8_live_original_motion.h"
#ifdef B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY
#include "b24_g173_authored_beam_priority.h"
#endif''',"G8 source include")
 s=one(s,
 ''' if(g84_source_clip&&!melee&&!a->repulsor_pending)
   desired=g84_source_clip;''',
 '''#ifdef B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY
 /* G169 source-authored Beam1/2/3 was dropped by old repulsor pose
  * priority. Only the accepted B16->G169 actor-selected ORIGINAL Beam
  * source clip gets preference. We do not synthesize an extra shot.
  * G8 melee retains its existing higher priority. */
 const int g173_original_beam=b24_g173_authored_beam_pose_priority(
     suit,g84_source_clip,melee!=NULL);
 if(g173_original_beam){
    a->repulsor_pending=0;
    a->whole_body_repulsor_active=0;
 }
 if(g84_source_clip&&!melee&&(!a->repulsor_pending||g173_original_beam))
    desired=g84_source_clip;
#else
 if(g84_source_clip&&!melee&&!a->repulsor_pending)
    desired=g84_source_clip;
#endif''',"G85 live sole G8 clip priority")
 s=one(s,
 ''' if(suit==4&&desired){
   if(strncmp(desired,"ironman_",8)!=0)return 0;
   int n=snprintf(g85_native_desired,sizeof(g85_native_desired),"suitcase_%s",desired+8);
   if(n<=0||(size_t)n>=sizeof(g85_native_desired))return 0;
   desired=g85_native_desired;
 }''',
 '''  if(suit==4&&desired){
#ifdef B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY
    /* G169 already supplies the genuine 2010 Mark V suitcase_ name.
     * Preserve its exact original 629-vertex IM2V filename. All
     * other clips continue through unchanged G85 conversion. */
    if(!b24_g173_is_authored_beam(4,desired)){
#endif
      if(strncmp(desired,"ironman_",8)!=0)return 0;
      int n=snprintf(g85_native_desired,sizeof(g85_native_desired),"suitcase_%s",desired+8);
      if(n<=0||(size_t)n>=sizeof(g85_native_desired))return 0;
      desired=g85_native_desired;
#ifdef B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY
    }
#endif
  }''',"MarkV genuine-source prefix double-conversion")
 cm+="""

# G173 only fixes the single G8/G85 original IM2V renderer accepting
# the EXISTING G169 three-phase 2010 Mark V and Mark VI Beam source clip.
# B16 is still the sole accepted weapon event; G82/G8 melee takes priority.
option(B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY "Preserve exactly-authored G169 Unibeam pose through G8/G85 single source animator" OFF)
if(B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY)
 if(NOT B24_G169_AUTHENTIC_BEAM_3_PHASE OR NOT B24_G85_NATIVE_MARKV_629 OR
    NOT B24_G84_ORIGINAL_MOVESET_ROUTER)
  message(FATAL_ERROR "G173 requires single G8 source streamer with real 2010 G169 Beam and G85 Mark V")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY=1)
endif()
"""
 if list(W.rglob("*.vpk")):raise RuntimeError("G173 source-only: NO VPK")
 shutil.copyfile(HERE/"b24_g173_authored_beam_priority.h",H)
 C.write_text(s);CM.write_text(cm)
 assert s.count("b24_g173_authored_beam_pose_priority(")==1
 assert s.count("b24_g173_is_authored_beam(4,desired)")==1
 print("G173 authentic 2010 G169->G8 single animator beam pose priority + MarkV exact suitcase filename fixed; no new event/damage/world/physics/VPK")
if __name__=="__main__":patch()
