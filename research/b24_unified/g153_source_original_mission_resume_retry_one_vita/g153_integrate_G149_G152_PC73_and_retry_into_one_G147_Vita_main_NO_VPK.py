#!/usr/bin/env python3
"""G153: opt-in source typed original Lua condition into canonical G149
single actual PS Vita game. Restore retry of G137 BLOCKED source event on
subsequent ticks without replaying completed PC1..PC3 actions.
Source QTE/Wait/StopVoice/TextBox callbacks STILL missing: fail CLOSED,
never fake original 2010 MissionResume, PC914/927 inputs, timed approval,
or native Wait(10) time unit. No alternate physics/game ticks. NO VPK.
"""
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
W=R/'work'
D=W/'b24/b24_unified'
M=W/'src/main.c'
CM=W/'CMakeLists.txt'
SRC=R/'research/b24_unified/g152_source_original_tutorial_condition_runtime'

def once(text,old,new):
    count=text.count(old)
    if count!=1:
        raise ValueError('G153 canonical G149 anchor source drift '+str(count)+' '+repr(old[:120]))
    return text.replace(old,new,1)

def run():
    if not M.is_file() or not CM.is_file():
        raise FileNotFoundError('G153 needs canonical G147 + G149 one PS Vita game source')
    m=M.read_text()
    cm=CM.read_text()
    requirements=(
      'B24_G137_MISSION000_REAL_SOURCE_EVENTS',
      'B24_G145_SOURCE_MISSION_AUDIO',
      'B24_G146_SOURCE_2010_QTE_1456',
      'B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE',
      'B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE',
    )
    for x in requirements:
        if x not in cm:raise ValueError('G153 missing canonical prior gate '+x)
    if 'B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP' in cm:
        raise ValueError('G153 source duplicate refused')
    for text in (
      'b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)',
      'b24_unified_tick(&b24_game,&b24_obs);',
      'b24_g83_timeline_tick(',
      'b24_g137_mission000_dispatch_verified_prefix(',
    ):
        if text=='b24_g137_mission000_dispatch_verified_prefix(':
            if m.count(text)<1:raise ValueError('G153 source mission has no real dispatcher')
        elif m.count(text)!=1:
            raise ValueError('G153 multiple/missing authoritative owner '+text)
    for name in ('b24_g152_source_tutorial_loop.h','b24_g152_source_tutorial_loop.c'):
        source=SRC/name
        if not source.is_file():raise FileNotFoundError(str(source))
        D.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,D/name)

    m=once(m,
        '#include "../b24/b24_unified/b24_g149_native_lua_bool_return.h"',
        '#include "../b24/b24_unified/b24_g149_native_lua_bool_return.h"\n'
        '#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP\n'
        '#include "../b24/b24_unified/b24_g152_source_tutorial_loop.h"\n'
        '#endif')
    m=once(m,
        'static B24G147Tutorial g147_original_L1_source_tutorial;',
        'static B24G147Tutorial g147_original_L1_source_tutorial;\n'
        '#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP\n'
        'static B24G152TutorialLoop g153_original_source_L1_PC73_wait_loop;\n'
        '#endif')
    m=once(m,
        'b24_g147_tutorial_init(&g147_original_L1_source_tutorial);',
        'b24_g147_tutorial_init(&g147_original_L1_source_tutorial);\n'
        '#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP\n'
        '            b24_g152_tutorial_loop_init(&g153_original_source_L1_PC73_wait_loop);\n'
        '#endif')

    m=once(m,
        '        b24_unified_tick(&b24_game,&b24_obs);',
        '''        b24_unified_tick(&b24_game,&b24_obs);
#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP
        /* G137 previously invoked source Mission000 only once at boot.
         * Retry EXACT blocked Lua event on later frames. G137's cursor
         * guarantees PC1 MissionPause and PC3 PauseMusic are NOT replayed
         * after their authentic ACK; current QTE Show1456 (PC6) remains
         * unacknowledged without actual render and does not release input. */
        if(g137_real_source_initialized &&
           g137_real_source_Mission000.phase==
             B24_G137_BLOCKED_NATIVE_SCENE_BINDING){
          (void)b24_g137_mission000_dispatch_verified_prefix(
            &g137_real_source_Mission000,
            g137_real_scene_MissionPause_only,
            &g145_original_2010_music);
        }
        /* Only after original PC1..72 actually ACK can original PC73
         * EQ evaluate. G152 waits on REAL native Wait(10) bridge
         * (currently NULL), StopVoice (NULL) and HUD340 (NULL).
         * This is deliberately fail-closed, not an in-game QTE claim. */
        if(g137_real_source_initialized &&
           g137_real_source_Mission000.phase==
             B24_G137_WAITING_2010_LUA_BRANCH_PC73){
          (void)b24_g152_tutorial_loop_step(
            &g153_original_source_L1_PC73_wait_loop,
            &g147_original_L1_source_tutorial,
            0, NULL, NULL, NULL, NULL);
        }
#endif''')

    cm+='''
# G153 uses the SAME one gameplay B14/G137 owner. Source QTE/Wait/HUD
# callbacks remain unsatisfied, retry G137 failed Lua PC every later
# frame, typed PC72->PC73->Wait(10)->StopVoice->ShowTut340 gate.
# NO guessed Wait time, fake device input, PC914/927/935 or new VPK.
option(B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP "Native original Mission000 PC73 loop and fail-closed exact Lua retry in single G149 Vita engine" OFF)
if(B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP)
 if(NOT B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE
    OR NOT B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
    OR NOT B24_G145_SOURCE_MISSION_AUDIO
    OR NOT B24_G137_MISSION000_REAL_SOURCE_EVENTS)
  message(FATAL_ERROR "G153 requires original G137/G145/G147/G149 single game source")
 endif()
 target_sources(im2_beta PRIVATE
   "b24/b24_unified/b24_g152_source_tutorial_loop.c")
 target_compile_definitions(im2_beta PRIVATE
   B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP=1)
endif()
'''
    M.write_text(m)
    CM.write_text(cm)
    if list(W.rglob('*.vpk')):
        raise RuntimeError('G153 NO VPK contract violated')
    assert m.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
    assert m.count('b24_unified_tick(&b24_game,&b24_obs);')==1
    assert m.count('b24_g83_timeline_tick(')==1
    print('G153 original 2010 G137 blocked mission Lua PC retry each tick, G152 original typed PC73 Wait10 StopVoice ShowTut340 linked in one B14 Vita game, all original renderer/Wait input missing = FAIL CLOSED. NO VPK.')
if __name__=='__main__':
    run()
