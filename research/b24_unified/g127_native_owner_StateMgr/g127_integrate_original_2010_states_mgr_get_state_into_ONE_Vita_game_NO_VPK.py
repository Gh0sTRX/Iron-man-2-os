#!/usr/bin/env python3
"""Append G127 original 2010 iOS StatesMgr::GetState(-1) native source
to the same G124/G111 Vita game ELF main. 2010 native state graph is
not yet instantiated as real enemy; never substitute fake AI/hitframes.
No VPK ever.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
R=HERE.parents[2];W=R/'work';D=W/'b24/b24_unified'
CM=W/'CMakeLists.txt';M=W/'src/main.c'
def run():
 if not CM.is_file() or not M.is_file():raise FileNotFoundError('G127 requires G124 source rebuilt first')
 cm=CM.read_text();main=M.read_text()
 assert 'B24_G124_ORIGINAL_NPC_SOURCE_RULES' in cm
 assert 'B24_G111_NATIVE_SOURCE_GATES' in cm
 assert 'B24_G108_SOURCE_VISUAL_WALLS' in cm
 assert main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert main.count('b24_g83_timeline_tick(')==1
 assert main.count('b24_g8_motion_tick_g84(')==1
 if 'B24_G127_ORIGINAL_STATESMGR_SOURCE' in cm:raise ValueError('G127 duplicate state helper')
 for n in ('b24_g127_authentic_2010_states_mgr.h','b24_g127_authentic_2010_states_mgr.c'):
  shutil.copyfile(HERE/n,D/n)
 cm+='''
# G127 original iOS 2010 native StatesMgr::GetState 0x9F910 source:
# GetState(-1) = this+0xC current pointer;
# positive: this+0x14 group-index, this+0x8 group array,
# group+0x2AC count; group+0x2B0 State* array, fallback current.
# CNPC::isAttackState 0xE1A20 now callable from REAL class layout
# with ORIGINAL values; source group instance population still separate.
option(B24_G127_ORIGINAL_STATESMGR_SOURCE "Link original 2010 iOS StatesMgr GetState and CNPC attack-state chain into native Vita source" OFF)
if(B24_G127_ORIGINAL_STATESMGR_SOURCE)
 if(NOT B24_G124_ORIGINAL_NPC_SOURCE_RULES)
  message(FATAL_ERROR "G127 requires G124 real native NPC state predicates")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g127_authentic_2010_states_mgr.c")
 target_compile_definitions(im2_beta PRIVATE B24_G127_ORIGINAL_STATESMGR_SOURCE=1)
endif()
'''
 CM.write_text(cm)
 assert not list(W.rglob('*.vpk'))
 print('G127 genuine owner 2010 state manager native logic linked to ONE compiled original Vita game source, no new game actor, NO VPK.')
if __name__=='__main__':run()
