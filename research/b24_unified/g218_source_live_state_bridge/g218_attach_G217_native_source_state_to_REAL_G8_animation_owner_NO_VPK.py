#!/usr/bin/env python3
"""G218 attach G217 SOURCE-AUTHENTIC original iOS 2010 StateData to real
live main/G8's actually LOADED IM2V source clip, read-only observation.

NO second StateMgr, B14 world integrator, G83 selector, G8 streamer,
accepted B16 weapon, gameplay clock, hit/damage, missile or fabricated
attack effect. G217 complete state table is taken from GitHub Actions
SOURCE-GENERATED owner file, never from guessed comments or manual data.
Source integration into Vita ELF only, NEVER build/package VPK.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3]
W=R/"work"
M=W/"src/main.c"
CM=W/"CMakeLists.txt"
D=W/"b24/b24_unified"
HERE=Path(__file__).resolve().parent
NATIVE_HEADER="b24_g217_AUTHENTIC_original_2010_iOS_source_states_ONLY_NO_VPK.h"
OBSERVER="b24_g218_live_authentic_2010_state_observer.h"
ORIGINAL_ARM_DISPATCH_HEADER="b24_g197_original_2010_attack_dispatch_reference.h"
ORIGINAL_ARM_DISPATCH=R/"research/b24_unified/g197_source2010_attack_dispatch"/ORIGINAL_ARM_DISPATCH_HEADER
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise ValueError("G218 strict ORIGINAL one-owner "+label+" source drift count="+str(n))
 return s.replace(old,new,1)
def apply(source_g217_header:Path):
 for p in (source_g217_header,HERE/OBSERVER,ORIGINAL_ARM_DISPATCH,M,CM,
          D/"b24_g8_live_original_motion.c"):
  if not p.is_file():raise FileNotFoundError("G218 authentic original source prerequisite absent: "+str(p))
 if source_g217_header.name!=NATIVE_HEADER:
  raise ValueError("G218 owner source header must be original G217 known file")
 header=source_g217_header.read_text()
 if (header.count("#define B24G217_SOURCE_STATES_PER_ARMOR 194")!=1 or
     "B24G217_TRUE_SOURCE_ATTACK_TRAIL_EVENT_COUNT" not in header or
     "b24g217_true_2010_owner_states[4][194]" not in header):
  raise ValueError("G218 cannot accept hand-generated/fake G217 2010 StateData")
 main=M.read_text();cm=CM.read_text()
 if "B24_G218_SOURCE_STATE_OBSERVER" in main or "B24_G218_SOURCE_STATE_OBSERVER" in cm:
  raise ValueError("G218 cannot install twice")
 required=("B24_G84_ORIGINAL_MOVESET_ROUTER",
           "B24_G85_NATIVE_MARKV_629",
           "B24_G169_AUTHENTIC_BEAM_3_PHASE",
           "B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY")
 for flag in required:
  if flag not in cm:raise ValueError("G218 requires real current original 2010 single source owner: "+flag)
 if (main.count("b24_g83_timeline_tick(")!=1 or
     main.count("b24_g8_motion_tick_g84(")!=1 or
     main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1 or
     main.count("b16_combat_fire(&combat,&world,muzzle)")!=1):
  raise ValueError("G218 original main has drifted: never insert second physics/stream/combat source")
 include='#include "../b24/b24_unified/b24_g83_authentic_timed_router.h"'
 main=one(main,include,include+'''
#ifdef B24_G218_SOURCE_STATE_OBSERVER
#include "../b24/b24_unified/b24_g218_live_authentic_2010_state_observer.h"
/* G218 sole passive original iOS 2010 StateData observer, NOT StateMgr. */
static B24G218LiveObserver b24_g218_live_source_state={0};
#endif''',"G84 one native C11 StateData observer include")
 actual='''          if(!b24_g8_motion_tick_g84(&b24_original_motion,
                "app0:animations",model.vertices,sizeof(IM2Vertex),
                model.nv,idx,original_stage,move_x,move_y,
                (uint32_t)now,g84_route.stem)){running=0;break;}'''
 observer='''#ifdef B24_G218_SOURCE_STATE_OBSERVER
          /* G218 observes the ACTUAL successfully opened original 2010
           * G8 selected source IM2V, not G83's intended candidate.
           * This original owner-authenticated 194-state lookup makes
           * source AttackType / native event data available for QA.
           * No original touch meaning, hit time, missile/projectile,
           * physics or callback is changed. */
          (void)b24_g218_observe_actually_loaded_G8_clip(
             &b24_g218_live_source_state,idx,
             b24_original_motion.selected,b24_original_motion.active,
             b24_original_motion.missing);
#endif'''
 main=one(main,actual,actual+"\n"+observer,"G8 actual load after one native 2010 owner frame")
 cm+='''
# G218 bind recovered owner-authentic G217 state records to ACTUALLY
# loaded G8 IM2V source clips. PASSIVE-only: no weapon/input/movement
# changes or pseudo-native StateMgr. G217 data must be original source
# from 2010 IPA G213B, never guessed weapon-to-animation mapping.
option(B24_G218_SOURCE_STATE_OBSERVER "Read-only original iOS 2010 StateData/StateTrack for real loaded G8 IM2V original clips" OFF)
if(B24_G218_SOURCE_STATE_OBSERVER)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER OR NOT B24_G85_NATIVE_MARKV_629 OR
    NOT B24_G169_AUTHENTIC_BEAM_3_PHASE OR
    NOT B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY)
  message(FATAL_ERROR "G218 original 2010 owner source requires existing exact single G83/G8 native source animator and G169/G173")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G218_SOURCE_STATE_OBSERVER=1)
endif()
'''
 if list(W.rglob("*.vpk")):raise RuntimeError("G218 never accept/create VPK")
 shutil.copyfile(source_g217_header,D/NATIVE_HEADER)
 shutil.copyfile(ORIGINAL_ARM_DISPATCH,D/ORIGINAL_ARM_DISPATCH_HEADER)
 shutil.copyfile(HERE/OBSERVER,D/OBSERVER)
 M.write_text(main);CM.write_text(cm)
 assert main.count("b24_g218_observe_actually_loaded_G8_clip(")==1
 assert main.count("b24_g8_motion_tick_g84(")==1
 assert main.count("b24_g83_timeline_tick(")==1
 assert main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert main.count("b16_combat_fire(&combat,&world,muzzle)")==1
 assert cm.count('option(B24_G218_SOURCE_STATE_OBSERVER ')==1
 print("G218 PASS G217 776 real 2010 StateData and authentic raw attack track timestamps wired PASSIVE to real G8 selected loaded source animation in single actual Vita main; NO added damage/weapon/physics/VPK")
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--g217-header",type=Path,required=True)
 args=p.parse_args()
 apply(args.g217_header)
