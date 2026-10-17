#include "b24_g137_source_mission000_intro.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int good(void *context,const B24G137Event *e){
 unsigned *called=(unsigned*)context;
 if(!e||e->original_lua_pc>=73||!e->original_args_reliable)return 0;
 (*called)++;return 1;
}
typedef struct {unsigned applied;uint16_t stop_at_pc;} Controlled;
static int missing(void *context,const B24G137Event *e){
 Controlled *x=(Controlled*)context;
 if(e->original_lua_pc>=x->stop_at_pc)return 0;
 x->applied++;return 1;
}
int main(void){
 B24G137Mission000 m={0};
 assert(b24_g137_mission000_init(&m));
 assert(m.phase==B24_G137_READY);
 assert(m.cursor==0);
 /* Neither empty/null fake scene nor absent genuine QTE author binding
  * may automatically unlock 2010 native player flight/mission flow. */
 assert(b24_g137_mission000_dispatch_verified_prefix(&m,NULL,NULL)==
   B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 assert(m.actually_dispatched_count==0&&m.unresolved_scene_event==1);
 assert(!b24_g137_mission000_is_gameplay_released(&m));
 Controlled c={0,34};
 assert(b24_g137_mission000_dispatch_verified_prefix(&m,missing,&c)==
   B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 assert(m.next_source_lua_pc==34);
 assert(m.cursor==c.applied);
 assert(m.requested_mission_pause==1);
 assert(!m.requested_MarkV_idle);
 assert(!m.requested_MarkV_hidden);
 assert(!m.requested_input14_disabled);
 unsigned applied=0;
 assert(b24_g137_mission000_dispatch_verified_prefix(&m,good,&applied)==
   B24_G137_WAITING_2010_LUA_BRANCH_PC73);
 assert(m.actually_dispatched_count==b24_g137_source_lua_event_count);
 assert(m.cursor==b24_g137_source_lua_event_count);
 assert(m.next_source_lua_pc==73);
 assert(m.requested_mission_pause&&m.requested_MarkV_idle);
 assert(m.requested_MarkV_hidden&&m.requested_input14_disabled);
 assert(m.requested_tutorial_339&&m.requested_tutorial_confirmation_query);
 assert(b24_g137_source_lua_event_count==24);
 assert(!b24_g137_mission000_is_gameplay_released(&m));
 assert(c.applied+applied==b24_g137_source_lua_event_count);
 assert(b24_g137_mission000_dispatch_verified_prefix(&m,good,&applied)==
   B24_G137_WAITING_2010_LUA_BRANCH_PC73);
 printf("G137 PASS original 2010 typed Level1 Mission000 PC<73 scene start exact %u source events with authentic original IDs, retryable QTE pause, native actor input14 false, stops PC73 not fake later input2/6 MissionResume. NO VPK.\n",
  b24_g137_source_lua_event_count);
 return 0;
}
