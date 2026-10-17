#include "b24_g137_source_mission000_intro.h"
#include <string.h>
/* List b24_g137_source_lua_events is generated from the actual 2010
 * G27 71 native Lua CALL-site metadata, NOT manually invented. */
int b24_g137_mission000_init(B24G137Mission000 *m){
 if(!m||!b24_g137_source_lua_event_count||
    b24_g137_source_lua_event_count>72u)return 0;
 memset(m,0,sizeof(*m));
 uint16_t last=0;
 int haspause=0,hasinput=0,hasMCidle=0,hasMCHide=0;
 for(uint32_t j=0;j<b24_g137_source_lua_event_count;j++){
  const B24G137Event *e=&b24_g137_source_lua_events[j];
  if(!e->original_lua_pc||e->original_lua_pc>=73 ||
     e->original_lua_pc<=last||!e->original_args_reliable){
    m->phase=B24_G137_BAD_SOURCE;return 0;
  }
  last=e->original_lua_pc;
  if(e->original_lua_pc==1&&e->opcode==B24_G137_CALL_MISSION_PAUSE)
   haspause=1;
  if(e->original_lua_pc==34&&e->opcode==B24_G137_CALL_SETSTATE&&
     e->source_arg0==1062&&e->source_arg1_string&&
     strcmp(e->source_arg1_string,"idle")==0)hasMCidle=1;
  if(e->original_lua_pc==43&&e->opcode==B24_G137_CALL_HIDE&&
     e->source_arg0==1062)hasMCHide=1;
  if(e->original_lua_pc==50&&e->opcode==B24_G137_CALL_SETINPUT&&
     e->source_arg0==14&&e->original_arg1_boolean==0)hasinput=1;
 }
 if(!(haspause&&hasinput&&hasMCidle&&hasMCHide)){
  m->phase=B24_G137_BAD_SOURCE;return 0;
 }
 m->phase=B24_G137_READY;
 m->next_source_lua_pc=b24_g137_source_lua_events[0].original_lua_pc;
 return 1;
}
B24G137Stage b24_g137_mission000_dispatch_verified_prefix(
 B24G137Mission000 *m,B24G137SceneHandler native_scene_binding,void *context){
 if(!m||m->phase==B24_G137_BAD_SOURCE)return B24_G137_BAD_SOURCE;
 if(m->phase==B24_G137_UNINITIALIZED)return B24_G137_UNINITIALIZED;
 if(m->phase==B24_G137_WAITING_2010_LUA_BRANCH_PC73)return m->phase;
 if(!native_scene_binding){
  m->phase=B24_G137_BLOCKED_NATIVE_SCENE_BINDING;
  m->unresolved_scene_event=1;
  return m->phase;
 }
 while(m->cursor<b24_g137_source_lua_event_count){
  const B24G137Event *e=&b24_g137_source_lua_events[m->cursor];
  /* Never claim original script progressed if native QTE/actor/Deco
   * handler has not acknowledged actually applying that authored action.
   * Retriable: record same authentic Lua PC until original binding ready. */
  if(e->opcode==B24_G137_CALL_UNKNOWN||
     !native_scene_binding(context,e)){
   m->phase=B24_G137_BLOCKED_NATIVE_SCENE_BINDING;
   m->unresolved_scene_event=1;
   m->next_source_lua_pc=e->original_lua_pc;
   return m->phase;
  }
  if(e->opcode==B24_G137_CALL_MISSION_PAUSE)
   m->requested_mission_pause=1;
  if(e->opcode==B24_G137_CALL_SETSTATE&&e->source_arg0==1062)
   m->requested_MarkV_idle=1;
  if(e->opcode==B24_G137_CALL_HIDE&&e->source_arg0==1062)
   m->requested_MarkV_hidden=1;
  if(e->opcode==B24_G137_CALL_SETINPUT&&
     e->source_arg0==14&&!e->original_arg1_boolean)
   m->requested_input14_disabled=1;
  m->cursor++;
  m->actually_dispatched_count++;
  m->unresolved_scene_event=0;
 }
 /* Authentic Lua first EQ at PC73: here we MUST STOP.
  * No generic fake time-based auto QTE completion or gameplay resume.
  * G135's PC914/927 calls belong after real Lua branches. */
 m->phase=B24_G137_WAITING_2010_LUA_BRANCH_PC73;
 m->next_source_lua_pc=73;
 return m->phase;
}
int b24_g137_mission000_is_gameplay_released(
 const B24G137Mission000 *m){
 /* No false original MissionResume until real source conditional VM
  * and Scene API are operational. */
 (void)m;return 0;
}
