#!/usr/bin/env python3
"""G169 original 2010 IM2V three-phase beam animation in live ONE Vita game.

No speculative missile, VFX, damage, iOS native input binding, gyro or rig.
The current port B16_UNIBEAM ACCEPTED shot is the only bridge; authentic
2010 ground/hover Beam1/Beam2/Beam3 original frames+durations. This
experimental source event translation is opt-in (not original native
AttackType GameLoft mapping until touch emulation proves it).
Never changes G75 original geometry / B14 movement / model size.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3]
W=R/"work";M=W/"src/main.c";CM=W/"CMakeLists.txt"
D=W/"b24/b24_unified";HERE=Path(__file__).resolve().parent
ORIG=R/"research/b24_unified"
def one(s,a,b,where):
 n=s.count(a)
 if n!=1:raise ValueError("G169 actual code owner drift "+where+": "+str(n)+" "+repr(a[:80]))
 return s.replace(a,b,1)
def apply():
 for f in [M,CM,D/"b24_g8_live_original_motion.c"]:
  if not f.is_file():raise FileNotFoundError(str(f))
 s=M.read_text();cm=CM.read_text()
 if "B24_G169_AUTHENTIC_BEAM_3_PHASE" in cm:raise ValueError("G169 duplicate")
 for flag in ["B24_G168_ORIGINAL_SUIT_RENDER_FOOT","B24_G84_ORIGINAL_MOVESET_ROUTER",
              "B24_G85_NATIVE_MARKV_629","B24_G75_SOURCE_CAPSULE"]:
  if flag not in cm:raise ValueError("G169 needs real integrated 2010 owner "+flag)
 if s.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G169 forbids second movement engine")
 if s.count("b24_g83_timeline_tick(")!=1:
  raise ValueError("G169 preserves real G83 selected source animation")
 if s.count("int fired=b16_combat_fire(&combat,&world,muzzle);")!=1:
  raise ValueError("G169 requires REAL current B16 accepted original attack event")
 anchor='#include "../b24/b24_unified/b24_g75_source_capsule.h"'
 s=one(s,anchor,anchor+'''
#ifdef B24_G169_AUTHENTIC_BEAM_3_PHASE
#include "../b24/b24_unified/b24_g169_native_source_unibeam.h"
static B24G169Beam b24_g169_l1_source_beam_actor={0};
#endif''',"header")
 anchor="int fired=b16_combat_fire(&combat,&world,muzzle);"
 s=one(s,anchor,anchor+'''
#ifdef B24_G169_AUTHENTIC_BEAM_3_PHASE
           /* Exact 2010 authored original 3×Beam IM2V: ONLY when the
            * existing B16 combat accepted a unibeam energy/damage event.
            * Current B16 accepted event remains port HLE, not proven
            * native Gameloft dispatch. Mark V=629 and MarkVI=802 real
            * bind sources. No WarMachine Beam original and no Stage2
            * cruise or Rush fire. Original QTE/weapon type not forged. */
           if(fired>=0 && combat.mode==B16_UNIBEAM &&
              (!world.flying||world.flight_stage<=1))
             (void)b24_g169_native_beam_begin(
                 &b24_g169_l1_source_beam_actor,idx,world.flying!=0,
                 (uint32_t)now);
#endif''',"accepted_attack")
 # G301 retains the original 2010 Beam priority between G83 selection
 # and the sole G8 renderer, but G84 no longer feeds back the pinned
 # VISUAL clip direction into physical Stage2 steering history.
 # Never restore the stale old feedback as a convenient insertion anchor.
 if "g84_last_flight_dir=world.flying?g84_route.direction" in s or "g84_route.direction" in s:
  raise ValueError("G169 refuses stale G84 visual-to-physical flight feedback")
 anchor="g84_last_flight_dir=b24_g83_physical_flight_dir("
 s=one(s,anchor,'''#ifdef B24_G169_AUTHENTIC_BEAM_3_PHASE
           /* One REAL G83/G8 source streaming owner, no second animated
            * model: accepted weapon event routes through normal motion
            * sample selection, respecting native beam source durations. */
           const char *g169_original_source_beam_clip=
               b24_g169_native_beam_clip(
                  &b24_g169_l1_source_beam_actor,idx,
                  world.flying!=0,world.flying?world.flight_stage:0,
                  (uint32_t)now);
           if(g169_original_source_beam_clip)
              g84_route.stem=g169_original_source_beam_clip;
#endif
           '''+anchor,"original G83 select before G8 stream")
 for name in ["b24_g169_native_source_unibeam.h","b24_g169_native_source_unibeam.c"]:
  shutil.copyfile(HERE/name,D/name)
 for name in ["b24_g11_original_unibeam_sequence.h","b24_g11_original_unibeam_sequence.c"]:
  shutil.copyfile(ORIG/name,D/name)
 cm+='''

# G169 actual 2010 all six Beam IM2V sequences with phase timings. Source
# authored anim clips but B16 source input is our port, not proven native
# original attack/input mapping. Retain user first-world WIP scope.
option(B24_G169_AUTHENTIC_BEAM_3_PHASE "Source-original 2010 MarkV/VI ground/hover 3-phase Beam IM2V on accepted current B16 Unibeam event" OFF)
if(B24_G169_AUTHENTIC_BEAM_3_PHASE)
 if(NOT B24_G85_NATIVE_MARKV_629 OR NOT B24_G84_ORIGINAL_MOVESET_ROUTER
    OR NOT B24_G168_ORIGINAL_SUIT_RENDER_FOOT)
  message(FATAL_ERROR "G169 requires genuine single G83 original 2010 animation, G168 original armor foot, one B14")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g169_native_source_unibeam.c"
  "b24/b24_unified/b24_g11_original_unibeam_sequence.c")
 target_compile_definitions(im2_beta PRIVATE
   B24_G169_AUTHENTIC_BEAM_3_PHASE=1)
endif()
'''
 if s.count("b24_g169_native_beam_begin(")!=1 or s.count("b24_g169_native_beam_clip(")!=1:
  raise ValueError("G169 must use ONE real accepted local B16 event and one G83 stream")
 M.write_text(s);CM.write_text(cm)
 if list(W.rglob("*.vpk")):raise RuntimeError("G169 NO VPK")
 print("G169 original 2010 six beam IM2V source clips actual B16 accepted shot->one G83/G8 owner compiled opt-in; no invented VFX native input or new physics, NO VPK")
if __name__=="__main__":apply()
