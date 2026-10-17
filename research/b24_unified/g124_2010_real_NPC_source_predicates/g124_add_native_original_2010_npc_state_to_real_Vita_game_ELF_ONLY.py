#!/usr/bin/env python3
"""Source-only G124: add original 2010 native CNPC/kill/sky rules into the
EXISTING full G111 merged PS Vita source ELF only.
NOT an NPC AI spawner or a second combat actor; zero fake AI, no VPK.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];WORK=ROOT/'work'
D=WORK/'b24/b24_unified'
M=WORK/'src/main.c';C=WORK/'CMakeLists.txt'
def main():
 assert M.is_file() and C.is_file(), 'G124 requires original merged game first'
 main=M.read_text()
 cm=C.read_text()
 assert main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert main.count('b24_g83_timeline_tick(')==1
 assert main.count('b24_g8_motion_tick_g84(')==1
 assert 'B24_G111_NATIVE_SOURCE_GATES' in cm
 assert 'B24_G108_SOURCE_VISUAL_WALLS' in cm
 if 'B24_G124_ORIGINAL_NPC_SOURCE_RULES' in cm:
  raise ValueError('duplicate G124 source rules')
 for filename in ('b24_g124_real_original_NPC_source_state.h',
                  'b24_g124_real_original_NPC_source_state.c'):
  shutil.copyfile(HERE/filename,D/filename)
 cm+='''

# G124 real native 2010 iOS CNPC class small ARM mechanics, optional:
# 0xE1A20 attack state {4,5}, 0xE1694 priority-gated SetState,
# 0xE19E0 signed modular fire frequency with native source fields,
# 0xCB5B8 original MissionConditionKill empty/cached exits,
# 0xC2810 UpdateSkyBox mode prerequisite. This DOES NOT spawn NPCs,
# execute original mission AI, or prove full shader render fidelity.
option(B24_G124_ORIGINAL_NPC_SOURCE_RULES "Compile proven original iOS 2010 native NPC state, kill-objective early gate and sky update rules" OFF)
if(B24_G124_ORIGINAL_NPC_SOURCE_RULES)
 if(NOT B24_G111_NATIVE_SOURCE_GATES OR NOT B24_G108_SOURCE_VISUAL_WALLS)
  message(FATAL_ERROR "G124 must preserve G111 actor evidence and G108 one world")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g124_real_original_NPC_source_state.c")
 target_compile_definitions(im2_beta PRIVATE B24_G124_ORIGINAL_NPC_SOURCE_RULES=1)
endif()
'''
 C.write_text(cm)
 assert not list(WORK.rglob('*.vpk'))
 print('G124 owner 2010 native small NPC logic compiled into real merged C source-only; no second actor/AI, no Vita VPK.')
if __name__=='__main__':main()
