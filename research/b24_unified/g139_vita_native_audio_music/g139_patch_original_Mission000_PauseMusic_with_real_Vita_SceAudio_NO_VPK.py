#!/usr/bin/env python3
"""G139 after G137: REAL PS Vita SceAudioOut BGM port opening and volume
pause command in the ONE actual B24 game main; expose original 2010 Lua
Mission000 PC3 only after sound output call returned success.
2010 original SoundManager inner mixer/track pause still not decoded.
No native original .www tracks ID88/voice320 loaded or invented.
No AUTO completion of QTE1456 PC6/IsTutConfirmed PC72.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3];W=R/'work'
M=W/'src/main.c';CM=W/'CMakeLists.txt';DST=W/'b24/b24_unified'
HERE=Path(__file__).resolve().parent
def one(s,old,new):
 count=s.count(old)
 if count!=1:raise ValueError('G139 original G137 one main source anchor changed '+str(count)+' '+repr(old[:110]))
 return s.replace(old,new,1)
def patch():
 if not M.is_file() or not CM.is_file():
  raise FileNotFoundError('G139 requires G137 source-authentic merged ONE Vita game first')
 code=M.read_text();cm=CM.read_text()
 assert code.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert code.count('b24_unified_tick(&b24_game,&b24_obs);')==1
 assert code.count('g137_real_scene_MissionPause_only')==2
 assert 'B24_G137_MISSION000_REAL_SOURCE_EVENTS' in cm
 assert 'B24_G136_SOURCE_B14_WORLD_BOUNDS' in cm
 if 'B24_G139_REAL_VITA_AUDIO_OUT' in cm:raise ValueError('G139 duplicate port')
 for filename in ('b24_g139_original_mission_music_bridge.h',
                  'b24_g139_original_mission_music_bridge.c'):
  shutil.copyfile(HERE/filename,DST/filename)
 old='''#include "../b24/b24_unified/b24_g137_source_mission000_intro.h"'''
 new=old+'''
#include "../b24/b24_unified/b24_g139_original_mission_music_bridge.h"'''
 code=one(code,old,new)
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
/* G139 actual Vita SceAudioOut BGM output port, source Lua PC3 pause:
 * only acknowledge original PauseMusic if BGM open AND SetVolume succeeded.
 * Music track ID88 and dialogue 320 are not loaded yet. */
static B24G139Music g139_real_vita_music;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 return b24_g139_original_Mission000_audio_dispatch(ctx,e);
}'''
 code=one(code,old,new)
 old='''          if(b24_g137_mission000_init(&g137_real_source_Mission000))
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);'''
 new='''          if(b24_g137_mission000_init(&g137_real_source_Mission000)){
            (void)b24_g139_music_init(&g139_real_vita_music,
                   b24_g139_native_vita_audio_backend());
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,
               &g139_real_vita_music);
          }'''
 code=one(code,old,new)
 old='''        /* PauseMusic at PC3 and QTE ID1456 Show at PC6 lack a bound
         * native scene/audio API: retain first unsupported source PC and
         * do not fabricate camera/Deco visibility, MarkV flight rights,
         * PC914/927 UI unlock or MissionResume PC935. */'''
 new='''        /* G139 REAL SceAudio music output can acknowledge PC3 if
         * port opened and volume set; next ORIGINAL Show(1456) QTE at
         * PC6 is STILL unbound. Do not fake Deco/camera or tutorial
         * conditional PC73, original MarkV flight permission, UI2/6,
         * Music88 asset playback, voice320, MissionResume PC935. */'''
 code=one(code,old,new)
 cm+='''
# G139 native SceAudio BGM output and stateful PauseMusic PC3 source
# control to replace G137 plain unbound scene action. This is NOT
# iOS SoundManager actual PCM stream playback or original mix/pause ABI.
option(B24_G139_REAL_VITA_AUDIO_OUT "Open native PS Vita BGM audio port and gate original 2010 Mission000 PauseMusic PC3 on actual output state" OFF)
if(B24_G139_REAL_VITA_AUDIO_OUT)
 if(NOT B24_G137_MISSION000_REAL_SOURCE_EVENTS)
  message(FATAL_ERROR "G139 native original mission audio needs G137")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g139_original_mission_music_bridge.c")
 target_compile_definitions(im2_beta PRIVATE B24_G139_REAL_VITA_AUDIO_OUT=1)
 target_link_libraries(im2_beta PRIVATE SceAudio_stub)
endif()
'''
 M.write_text(code);CM.write_text(cm)
 assert not list(W.rglob('*.vpk'))
 print('G139 ONE true Vita game native source audio BGM output backend attached to owner 2010 Mission000 PC3, PC6 actual source QTE unbound and blocked. NO VPK.')
if __name__=='__main__':patch()
