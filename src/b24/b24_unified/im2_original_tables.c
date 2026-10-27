#include "im2_original_tables.h"
#include "b24_g137_source_mission000_intro.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *b24g217_original_suit_source_names[4];
B24G217_SourceState b24g217_true_2010_owner_states[4][194];
B24G217_SourceEvent b24g217_source_attack_trail_events[224];
B24G137Event b24_g137_source_lua_events[72];
uint32_t b24_g137_source_lua_event_count;
static char *active_strings;
typedef struct {
 const char *names[4];
 B24G217_SourceState states[4][194];
 B24G217_SourceEvent events[224];
 B24G137Event lua[72];
 char *strings;
} Tables;
static uint16_t u16(const unsigned char *p){return (uint16_t)(p[0]|(unsigned)p[1]<<8);}
static uint32_t u32(const unsigned char *p){
 return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
static int32_t i32(const unsigned char *p){
 uint32_t n=u32(p);
 return n<=INT32_MAX?(int32_t)n:-1-(int32_t)(UINT32_MAX-n);
}
static const char *string_at(char *pool,size_t bytes,uint32_t offset){
 if(offset>=bytes)return NULL;
 const char *s=pool+offset;
 const char *end=memchr(s,0,bytes-offset);
 if(!end||end==s||(size_t)(end-s)>127)return NULL;
 for(const char *p=s;p<end;p++)if((unsigned char)*p<32u||(unsigned char)*p>126u)return NULL;
 return s;
}
int im2_original_tables_ready(void){return active_strings!=NULL;}
void im2_original_tables_close(void){
 free(active_strings);active_strings=NULL;
 memset(b24g217_original_suit_source_names,0,sizeof(b24g217_original_suit_source_names));
 memset(b24g217_true_2010_owner_states,0,sizeof(b24g217_true_2010_owner_states));
 memset(b24g217_source_attack_trail_events,0,sizeof(b24g217_source_attack_trail_events));
 memset(b24_g137_source_lua_events,0,sizeof(b24_g137_source_lua_events));
 b24_g137_source_lua_event_count=0;
}
int im2_original_tables_decode(const void *data,size_t size){
 if(active_strings||!data||size<32||size>262144)return 0;
 const unsigned char *p=data;
 if(memcmp(p,"IM2D",4)||u32(p+4)!=1||u32(p+8)!=4||u32(p+12)!=194||
    u32(p+16)!=224||u32(p+28)!=0)return 0;
 const uint32_t lua_count=u32(p+20),strings=u32(p+24);
 if(!lua_count||lua_count>72||!strings||strings>131072)return 0;
 const size_t fixed=32+4*4+4*194*24+224*20+(size_t)lua_count*24;
 if(size!=fixed+strings)return 0;
 Tables *t=calloc(1,sizeof(*t));
 if(!t)return 0;
 t->strings=malloc(strings);
 if(!t->strings){free(t);return 0;}
 memcpy(t->strings,p+fixed,strings);
 p+=32;
 int ok=1;
 for(unsigned j=0;j<4;j++,p+=4){
  t->names[j]=string_at(t->strings,strings,u32(p));
  if(!t->names[j])ok=0;
 }
 for(unsigned j=0;j<4*194;j++,p+=24){
  B24G217_SourceState *s=&t->states[j/194][j%194];
  s->original_source_state_name=string_at(t->strings,strings,u32(p));
  s->original_AttackType_or_UNKNOWN=u32(p+4);
  s->original_next_state_or_UNKNOWN=u32(p+8);
  s->original_state_type_or_UNKNOWN=u32(p+12);s->original_loop_or_UNKNOWN=u32(p+16);
  s->native_source_state_index=u16(p+20);s->original_state_track_count=u16(p+22);
  if(!s->original_source_state_name||s->native_source_state_index!=j%194)ok=0;
 }
 for(unsigned j=0;j<224;j++,p+=20){
  B24G217_SourceEvent *e=&t->events[j];
  e->native_original_track_name=string_at(t->strings,strings,u32(p));
  e->raw_original_2010_start=u32(p+4);e->raw_original_2010_duration=u32(p+8);
  e->raw_original_2010_third_field_UNCLASSIFIED=u32(p+12);
  e->native_suit_group_index=u16(p+16);e->native_original_state_index=u16(p+18);
  if(!e->native_original_track_name||e->native_suit_group_index>=4||e->native_original_state_index>=194)ok=0;
 }
 uint16_t previous=0;
 for(unsigned j=0;j<lua_count;j++,p+=24){
  B24G137Event *e=&t->lua[j];
  e->original_lua_pc=u16(p);e->opcode=u16(p+2);
  e->source_arg0=i32(p+4);e->source_arg1=i32(p+8);e->source_arg2=i32(p+12);
  const uint32_t offset=u32(p+16);
  e->source_arg1_string=offset==UINT32_MAX?NULL:string_at(t->strings,strings,offset);
  e->original_arg1_boolean=p[20];e->original_args_reliable=p[21];
  if(!e->original_lua_pc||e->original_lua_pc>=73||e->original_lua_pc<=previous||
     e->opcode<1||e->opcode>15||e->original_arg1_boolean>1||e->original_args_reliable!=1||
     u16(p+22)||(offset!=UINT32_MAX&&!e->source_arg1_string))ok=0;
  previous=e->original_lua_pc;
 }
 if(!ok){free(t->strings);free(t);return 0;}
 memcpy(b24g217_original_suit_source_names,t->names,sizeof(t->names));
 memcpy(b24g217_true_2010_owner_states,t->states,sizeof(t->states));
 memcpy(b24g217_source_attack_trail_events,t->events,sizeof(t->events));
 memcpy(b24_g137_source_lua_events,t->lua,sizeof(t->lua));
 b24_g137_source_lua_event_count=lua_count;
 active_strings=t->strings;free(t);return 1;
}
int im2_original_tables_load(const char *path){
 if(!path||active_strings)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 int ok=fseek(f,0,SEEK_END)==0;
 long bytes=ok?ftell(f):-1;
 if(bytes<32||bytes>262144||fseek(f,0,SEEK_SET))ok=0;
 unsigned char *data=ok?malloc((size_t)bytes):NULL;
 if(!data)ok=0;
 if(ok&&fread(data,1,(size_t)bytes,f)!=(size_t)bytes)ok=0;
 if(fclose(f))ok=0;
 if(ok)ok=im2_original_tables_decode(data,(size_t)bytes);
 free(data);return ok;
}
