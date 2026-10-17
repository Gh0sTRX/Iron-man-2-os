#!/usr/bin/env python3
"""G145: Link G139/G141/G142/G144 actual native ARM Vita PCM audio
modules into ONE existing G137 Level1 mission main, no second physics
tick, no VPK. Native 2010 Lua Music88 and Voice320 resolve to verified
original WAV-derived PCM filenames in distinct BGM/MAIN kernel streams.

Source original Mission000 PauseMusic at PC3 calls
Game::StopCrtBGM([Game+0xEC], 2000.f). Native Game ctor sets that field -1;
neither fake SceAudio output mute nor guessed intro track = successful
mission start. Preserve PC3 blocker until source state and original stop
semantics are proven; do not invent PC6 QTE or MissionResume.

G145 integration is fully opt-in, default OFF, but native Vita CI builds ON.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3]
W=R/"work"
D=W/"b24/b24_unified"
MAIN=W/"src/main.c"
CM=W/"CMakeLists.txt"
ROOT=Path(__file__).resolve().parents[1]
def one(s,a,z):
 n=s.count(a)
 if n!=1:raise ValueError(f"G145 source anchor occurrence {n}: {a[:120]!r}")
 return s.replace(a,z,1)
def run():
 if not MAIN.is_file() or not CM.is_file():
  raise FileNotFoundError("G145 needs G137 merged owner B24 real one-game Vita source")
 s=MAIN.read_text();cm=CM.read_text()
 assert s.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert s.count("b24_unified_tick(&b24_game,&b24_obs);")==1
 assert s.count("b24_g83_timeline_tick(")==1
 assert "B24_G137_MISSION000_REAL_SOURCE_EVENTS" in cm
 assert "B24_G136_SOURCE_B14_WORLD_BOUNDS" in cm
 if "B24_G145_REAL_ORIGINAL_AUDIO_CHANNELS" in cm:
  raise ValueError("G145 duplicate owner audio source bridge")
 mapping={
  "g139_vita_native_audio_music":["b24_g139_original_mission_music_bridge.c",
                                  "b24_g139_original_mission_music_bridge.h"],
  "g141_original_vita_pcm_stream":["b24_g141_owner_pcm_stream.c","b24_g141_owner_pcm_stream.h",
                                  "b24_g141_vita_stream_worker.c","b24_g141_vita_stream_worker.h"],
  "g142_original_2010_native_sound_id_semantics":["b24_g142_native_sound_source_truth.c",
                                                    "b24_g142_native_sound_source_truth.h"],
  "g144_original_level1_real_pcm_channels":["b24_g144_source_audio_channels.c",
                                             "b24_g144_source_audio_channels.h"]
 }
 for folder,names in mapping.items():
  for name in names:
   origin=ROOT/folder/name
   if not origin.is_file():raise FileNotFoundError(origin)
   content=origin.read_text()
   # The G142 source header was authored within the research directory;
   # the native target has all G137/G142 headers in one include directory.
   if name=="b24_g142_native_sound_source_truth.h":
    marker='#include "../g137_original_Mission000_native_boot/b24_g137_source_mission000_intro.h"'
    content=one(content,marker,'#include "b24_g137_source_mission000_intro.h"')
   (D/name).write_text(content)
 before='''#include "../b24/b24_unified/b24_g137_source_mission000_intro.h"'''
 after=before+'''
#include "../b24/b24_unified/b24_g142_native_sound_source_truth.h"
#include "../b24/b24_unified/b24_g144_source_audio_channels.h"'''
 s=one(s,before,after)
 before='''static B24G137Mission000 g137_real_source_Mission000;
static int g137_real_source_initialized=0;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 (void)ctx;
 /* Request is original source. No invented scene entity/QTE binding.
  * Actual mission task paused state tracked by dispatch state, not B14
  * gameplay global pause; original MissionPause != freeze entire game. */
 return e&&e->opcode==B24_G137_CALL_MISSION_PAUSE;
}'''
 after='''static B24G137Mission000 g137_real_source_Mission000;
static int g137_real_source_initialized=0;
static B24G144NativeAudio g145_true_source_Vita_channels;
static B24G142OwnerAudio g145_2010_iOS_audio_state;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 (void)ctx;
 if(!e)return 0;
 /* Actual native original mission Pause is recorded in the G137 journal,
  * not a fabricated entire game freeze. */
 if(e->original_lua_pc==1&&
     e->opcode==B24_G137_CALL_MISSION_PAUSE)return 1;
 /* Native iOS original sound IDs and stop semantics, not a fake
  * Vita BGM volume=0 -> PauseMusic success. Correct native owner track
  * starts at -1; PC3 remains blocked until source music/current-index
  * state + 2000.f stop/attenuation semantics are both verified. */
 return b24_g142_owner_source_music_call(&g145_2010_iOS_audio_state,e);
}'''
 s=one(s,before,after)
 before='''          if(b24_g137_mission000_init(&g137_real_source_Mission000))
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);'''
 after='''          if(b24_g137_mission000_init(&g137_real_source_Mission000)){
            b24_g144_source_audio_init(&g145_true_source_Vita_channels);
            /* Verified from original 2010 ARM Game ctor at VM 0x99564:
             * Game+0xEC CURRENT BGM is -1 until native source changes it. */
            g145_2010_iOS_audio_state.original_current_music_zero_based_id=-1;
            g145_2010_iOS_audio_state.original_current_music_id_from_actual_game_state_verified=0;
            g145_2010_iOS_audio_state.backend=
              b24_g144_source_audio_backend(&g145_true_source_Vita_channels);
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);
          }'''
 s=one(s,before,after)
 old='''        /* PauseMusic at PC3 and QTE ID1456 Show at PC6 lack a bound
         * native scene/audio API: retain first unsupported source PC and
         * do not fabricate camera/Deco visibility, MarkV flight rights,
         * PC914/927 UI unlock or MissionResume PC935. */'''
 new='''        /* G145 actual native dual SceAudio BGM + MAIN PCM channels
         * now linked into THIS real Vita game. Source-bound Music88 /
         * JARVIS Voice320 are available through G142 verified callbacks
         * when the REAL mission reaches PC62/PC70. The original Lua
         * PC3 StopCrtBGM(2000.f) source current track is -1 initially;
         * remain source-faithful and FAIL CLOSED, no guessed QTE1456,
         * PC72 tutorial confirmation or MissionResume PC935. */'''
 s=one(s,old,new)
 cm+='''
# G145 source-authentic user original 2010 v1.0.0 Level1 real audio:
# two concurrent Vita native audio outputs (BGM, MAIN) and source-ID
# Music88 + Voice320 WAV-derived 48kHz PCM, not embedded in VPK.
# Source original Lua PC3 2000.f StopCrtBGM is NOT a mute and remains
# blocked until actual current BGM/native fade semantics are implemented.
option(B24_G145_REAL_ORIGINAL_AUDIO_CHANNELS "Link original Level1 soundtrack/JARVIS real source PCM SceAudio into ONE Vita main (no playback until true mission calls), NO VPK" OFF)
if(B24_G145_REAL_ORIGINAL_AUDIO_CHANNELS)
 if(NOT B24_G137_MISSION000_REAL_SOURCE_EVENTS)
  message(FATAL_ERROR "G145 requires real original G137 Mission000 events")
 endif()
 target_compile_definitions(im2_beta PRIVATE
  B24_G145_REAL_ORIGINAL_AUDIO_CHANNELS=1
  B24_G139_REAL_VITA_AUDIO_OUT=1
  B24_G141_VITA_NATIVE=1
  B24_G144_VITA_NATIVE=1)
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g139_original_mission_music_bridge.c"
  "b24/b24_unified/b24_g141_owner_pcm_stream.c"
  "b24/b24_unified/b24_g141_vita_stream_worker.c"
  "b24/b24_unified/b24_g142_native_sound_source_truth.c"
  "b24/b24_unified/b24_g144_source_audio_channels.c")
 target_link_libraries(im2_beta PRIVATE
  SceAudio_stub
  SceKernelThreadMgr_stub)
endif()
'''
 MAIN.write_text(s);CM.write_text(cm)
 assert not list(W.rglob("*.vpk"))
 print("G145 true original SoundManager source ID88/Voice320 dual native Vita audio 5 modules linked to existing ONE B14 im2_beta main; PC3 remains original StopCrtBGM failclosed, no new VPK.")
if __name__=="__main__":run()
