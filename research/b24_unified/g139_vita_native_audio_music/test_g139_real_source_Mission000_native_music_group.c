#include "b24_g139_original_mission_music_bridge.h"
#include <assert.h>
#include <stdio.h>
typedef struct {int open_calls,vol_calls,close_calls,allow_open,allow_volume,last_l,last_r;} FakePort;
static int t_open(void *ctx,int frames,int hz){
 FakePort *c=(FakePort*)ctx;c->open_calls++;
 assert(frames==512&&hz==48000);
 return c->allow_open?3:-1;
}
static int t_volume(void *ctx,int port,int left,int right){
 FakePort *c=(FakePort*)ctx;c->vol_calls++;
 assert(port==3);c->last_l=left;c->last_r=right;
 return c->allow_volume;
}
static int t_close(void *ctx,int port){
 FakePort *c=(FakePort*)ctx;assert(port==3);
 c->close_calls++;return 1;
}
/* Generated original owner G27 2010 Lua event callback list, not fake. */
int main(void){
 B24G137Mission000 quest={0};
 assert(b24_g137_mission000_init(&quest));
 FakePort state={0};B24G139Music sound={0};
 B24G139AudioBackend b={&state,t_open,t_volume,t_close};
 assert(!b24_g139_music_init(&sound,b));
 assert(!b24_g139_music_pause(&sound));
 assert(quest.cursor==0);
 /* Audio not opened -> original source event PC3 must fail closed. */
 state.allow_open=1;
 assert(b24_g139_music_init(&sound,b));
 B24G137Stage status=b24_g137_mission000_dispatch_verified_prefix(
  &quest,b24_g139_original_Mission000_audio_dispatch,&sound);
 assert(status==B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 assert(quest.next_source_lua_pc==3);
 assert(quest.cursor==1&&quest.actually_dispatched_count==1);
 assert(!quest.requested_MarkV_hidden&&!quest.requested_input14_disabled);
 assert(!quest.requested_tutorial_339);
 assert(!b24_g137_mission000_is_gameplay_released(&quest));
 /* failed physical port-volume call DOES NOT advance PC3 */
 assert(state.vol_calls==1&&sound.pause_call_count==0);
 state.allow_volume=1;
 status=b24_g137_mission000_dispatch_verified_prefix(
  &quest,b24_g139_original_Mission000_audio_dispatch,&sound);
 assert(status==B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 assert(quest.next_source_lua_pc==6);
 assert(quest.cursor==2&&quest.actually_dispatched_count==2);
 assert(sound.output_open&&sound.music_paused);
 assert(sound.native_output_volume_applied&&sound.pause_call_count==1);
 assert(state.last_l==0&&state.last_r==0);
 assert(b24_g139_music_resume(&sound));
 assert(!sound.music_paused&&state.last_l==32768&&state.last_r==32768);
 assert(!sound.original_2010_sound_ID88_track_mapped);
 assert(!b24_g137_mission000_is_gameplay_released(&quest));
 b24_g139_music_close(&sound);
 assert(state.close_calls==1);
 puts("G139 PASS original 2010 Lua PC1 MissionPause PC3 PauseMusic dispatch with verified opened audio port and successful output control, blocks actual native unbound QTE Show1456 at PC6; no fake original SoundManager/music88/voice320 or game release, no VPK");
 return 0;
}
