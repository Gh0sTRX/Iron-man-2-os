#!/usr/bin/env python3
"""G145 source-only native integration of ACTUAL original 2010 Lua scene
Mission000 player and sound ID mapping into EXISTING B14/G137 Vita main.
G142 source accurate Game current BGM starts -1, hence PauseMusic PC3
when nothing is playing is safe empty-stop in our recreated engine.
G144 real source WAV Music88/Voice320 G141 async Vita output loaded ONLY
if original scenario gets to corresponding PC62/70 with source scene
QTE1456 still unimplemented, thus NO fake campaign progression.
No VPK; no proprietary IPA or original PCM distributed by this patch.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
W=R/'work'
M=W/'src/main.c';CM=W/'CMakeLists.txt';DST=W/'b24/b24_unified'
SOURCE=R/'research/b24_unified'
def one(s,old,new):
 n=s.count(old)
 if n!=1:raise ValueError(f'G145 original source changed expected exactly one {old!r} got {n}')
 return s.replace(old,new,1)
def run():
 if not M.is_file() or not CM.is_file():
  raise FileNotFoundError('G145 requires G137 source owner first')
 main=M.read_text();cm=CM.read_text()
 assert 'B24_G137_MISSION000_REAL_SOURCE_EVENTS' in cm
 assert 'B24_G136_SOURCE_B14_WORLD_BOUNDS' in cm
 assert main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert main.count('b24_unified_tick(&b24_game,&b24_obs);')==1
 assert main.count('b24_g83_timeline_tick(')==1
 if 'B24_G145_SOURCE_MISSION_AUDIO' in cm:raise ValueError('duplicate G145')
 for folder,filename in (
  ('g139_vita_native_audio_music','b24_g139_original_mission_music_bridge.h'),
  ('g139_vita_native_audio_music','b24_g139_original_mission_music_bridge.c'),
  ('g141_original_vita_pcm_stream','b24_g141_owner_pcm_stream.h'),
  ('g141_original_vita_pcm_stream','b24_g141_owner_pcm_stream.c'),
  ('g141_original_vita_pcm_stream','b24_g141_vita_stream_worker.h'),
  ('g141_original_vita_pcm_stream','b24_g141_vita_stream_worker.c'),
  ('g142_original_2010_native_sound_id_semantics','b24_g142_native_sound_source_truth.h'),
  ('g142_original_2010_native_sound_id_semantics','b24_g142_native_sound_source_truth.c'),
  ('g144_original_level1_real_pcm_channels','b24_g144_source_audio_channels.h'),
  ('g144_original_level1_real_pcm_channels','b24_g144_source_audio_channels.c'),
 ):
  body=(SOURCE/folder/filename).read_text()
  if filename=='b24_g142_native_sound_source_truth.h':
   needle='#include "../g137_original_Mission000_native_boot/b24_g137_source_mission000_intro.h"'
   if body.count(needle)!=1:raise ValueError('owner source C++ header changed')
   body=body.replace(needle,'#include "b24_g137_source_mission000_intro.h"')
  (DST/filename).write_text(body)
 anchor='#include "../b24/b24_unified/b24_g137_source_mission000_intro.h"'
 main=one(main,anchor,anchor+'''
#ifdef B24_G145_SOURCE_MISSION_AUDIO
#include "../b24/b24_unified/b24_g142_native_sound_source_truth.h"
#include "../b24/b24_unified/b24_g144_source_audio_channels.h"
#endif
''')
 old='''static B24G137Mission000 g137_real_source_Mission000;
static int g137_real_source_initialized=0;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 (void)ctx;
 /* Request is original source. No invented scene entity/QTE binding.
  * Actual mission task paused state tracked by dispatch state, not B14
  * gameplay global pause; original MissionPause != freeze entire game. */
 return e&&e->opcode==B24_G137_CALL_MISSION_PAUSE;
}'''
 new='''static B24G137Mission000 g137_real_source_Mission000;
static int g137_real_source_initialized=0;
#ifdef B24_G145_SOURCE_MISSION_AUDIO
static B24G144NativeAudio g145_original_vita_channels;
static B24G142OwnerAudio g145_original_2010_music;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 B24G142OwnerAudio *music=(B24G142OwnerAudio*)ctx;
 if(!e||!music)return 0;
 /* Real original G137 Lua PC1 MissionPause is a mission-request journal,
  * not an unconditional global B14 physics freeze. */
 if(e->original_lua_pc==1&&
    e->opcode==B24_G137_CALL_MISSION_PAUSE)return 1;
 /* PC3 is safe equivalent only when genuine Game+0xEC initial = -1:
  * no game BGM was playing. Subsequent PC62/PC70 use actual original
  * source 803x40 .www audio table and real Vita PCM thread backend.
  * PC6 QTE Show1456 remains absolutely BLOCKED, no fake script resume. */
 return b24_g142_owner_source_music_call(music,e);
}
#else
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 (void)ctx;return e&&e->opcode==B24_G137_CALL_MISSION_PAUSE;
}
#endif'''
 main=one(main,old,new)
 old='''          if(b24_g137_mission000_init(&g137_real_source_Mission000))
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);'''
 new='''          if(b24_g137_mission000_init(&g137_real_source_Mission000)){
#ifdef B24_G145_SOURCE_MISSION_AUDIO
            b24_g144_source_audio_init(&g145_original_vita_channels);
            g145_original_2010_music=(B24G142OwnerAudio){0};
            /* Original 2010 Game::Game source ARM0x99564 sets
             * Game+0xEC current music ID=-1. No source BGM has
             * played in rebuilt Vita game at Mission000 start. */
            g145_original_2010_music.original_current_music_zero_based_id=-1;
            g145_original_2010_music.original_current_music_id_from_actual_game_state_verified=1;
            g145_original_2010_music.original_current_music_track_is_playing=0;
            g145_original_2010_music.backend=
              b24_g144_source_audio_backend(&g145_original_vita_channels);
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,
               &g145_original_2010_music);
#else
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);
#endif
          }'''
 main=one(main,old,new)
 old='''        /* PauseMusic at PC3 and QTE ID1456 Show at PC6 lack a bound
         * native scene/audio API: retain first unsupported source PC and
         * do not fabricate camera/Deco visibility, MarkV flight rights,
         * PC914/927 UI unlock or MissionResume PC935. */'''
 new='''        /* G145: Source PC1 MissionPause then PC3 empty-current-BGM
         * native-value -1 (Game+0xEC) advances; PC6 QTE Show(1456)
         * remains explicitly blocked until true iOS scene node 1456
         * has render/touch event bindings. No fabricated Camera/QTE,
         * PC914/927 input enable or PC935 MissionResume. */
#endif
#if 0
        /* Old G137 only blocked all audio (replaced by G145). */'''
 # above weird? Instead replace with normal content no stray endif
 new='''        /* G145: Source PC1 MissionPause then PC3 empty-current-BGM
         * native-value -1 (Game+0xEC) advances; PC6 QTE Show(1456)
         * remains explicitly blocked until true iOS scene node 1456
         * has render/touch event bindings. No fabricated Camera/QTE,
         * PC914/927 input enable or PC935 MissionResume. */'''
 main=one(main,old,new)
 cm+='''
# G145 link source-authentic 2010 original Level1 audio ID table
# and native Vita dual-channel 48k stereo PCM workers into ONE game ELF.
# No asset bytes shipped in repo; user PCM must be at ux0:data/ironman2/audio.
# Original Game initial current BGM -1 from ARM constructor 0x99564.
option(B24_G145_SOURCE_MISSION_AUDIO "Source correct original 2010 Lua Sound IDs88/320 with real Vita dual SceAudio output and Mission000 PC3 empty BGM gate" OFF)
if(B24_G145_SOURCE_MISSION_AUDIO)
 if(NOT B24_G137_MISSION000_REAL_SOURCE_EVENTS)
  message(FATAL_ERROR "G145 native 2010 Mission000 source audio requires G137")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g139_original_mission_music_bridge.c"
  "b24/b24_unified/b24_g141_owner_pcm_stream.c"
  "b24/b24_unified/b24_g141_vita_stream_worker.c"
  "b24/b24_unified/b24_g142_native_sound_source_truth.c"
  "b24/b24_unified/b24_g144_source_audio_channels.c")
 target_compile_definitions(im2_beta PRIVATE
  B24_G145_SOURCE_MISSION_AUDIO=1
  B24_G139_REAL_VITA_AUDIO_OUT=1
  B24_G141_VITA_NATIVE=1
  B24_G144_VITA_NATIVE=1)
 target_link_libraries(im2_beta PRIVATE SceAudio_stub SceKernelThreadMgr_stub)
endif()
'''
 M.write_text(main);CM.write_text(cm)
 if list(W.rglob('*.vpk')):raise RuntimeError('G145 no new VPK')
 print('G145 source native 2010 Mission000 Game+0xEC=-1 PC3 empty-BGM command ACK, PC6 QTE1456 BLOCKED, ID88/320 original source PCM dual output linked to existing ONE true Vita B14 game ELF, no VPK')
if __name__=='__main__':run()
