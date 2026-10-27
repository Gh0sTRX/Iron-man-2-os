#include "im2_original_tables.h"
#include "b24_g137_source_mission000_intro.h"
#include "b24_g218_live_authentic_2010_state_observer.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void put32(unsigned char *p,uint32_t n){
 for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(n>>(i*8));
}
int main(void){
 /* Explicitly SYNTHETIC table fixture, no original game rows. */
 const size_t fixed=32+16+776*24+224*20+24,size=fixed+8;
 unsigned char *data=calloc(1,size);assert(data);
 memcpy(data,"IM2D",4);put32(data+4,1);put32(data+8,4);put32(data+12,194);
 put32(data+16,224);put32(data+20,1);put32(data+24,8);
 memcpy(data+fixed,"fixture",8);
 for(unsigned i=0;i<776;i++){
  unsigned char *p=data+48+i*24;
  put32(p+4,UINT32_MAX);p[20]=(unsigned char)(i%194);
 }
 for(unsigned i=0;i<224;i++){
  unsigned char *p=data+48+776*24+i*20;
  put32(p+4,UINT32_MAX);p[16]=(unsigned char)(i%4);p[18]=(unsigned char)(i%194);
 }
 unsigned char *lua=data+fixed-24;
 lua[0]=1;lua[2]=1;put32(lua+4,UINT32_MAX);put32(lua+16,UINT32_MAX);lua[21]=1;
 assert(!im2_original_tables_ready());
 B24G218LiveObserver observer={0};
 observer.source_state_name_correspondence_ONLY="stale";
 assert(!b24_g218_observe_actually_loaded_G8_clip(&observer,0,"ironman_ironman_ground_idel",1,0));
 assert(observer.source_state_name_correspondence_ONLY==NULL);
 assert(observer.source_authored_AttackType_or_UNKNOWN==B24G217_UNKNOWN_U32);
 B24G137Mission000 mission={0};
 assert(!b24_g137_mission000_init(&mission));
 for(size_t n=0;n<size;n++)assert(!im2_original_tables_decode(data,n));
 assert(im2_original_tables_decode(data,size));
 assert(im2_original_tables_ready());
 assert(!strcmp(b24g217_true_2010_owner_states[3][193].original_source_state_name,"fixture"));
 assert(b24g217_true_2010_owner_states[3][193].original_AttackType_or_UNKNOWN==UINT32_MAX);
 assert(b24g217_source_attack_trail_events[223].raw_original_2010_start==UINT32_MAX);
 assert(b24_g137_source_lua_events[0].source_arg0==-1);
 assert(b24_g137_source_lua_events[0].source_arg1_string==NULL);
 assert(b24_g137_source_lua_event_count==1);
 assert(!im2_original_tables_decode(data,size)); /* no half reload / dangling pointers */
 im2_original_tables_close();
 const size_t mutations[]={0,4,8,12,16,20,24,28,48,48+20,
                          48+776*24+16,fixed-24,fixed-24+21,fixed-1,size-1};
 for(unsigned i=0;i<sizeof(mutations)/sizeof(mutations[0]);i++){
  size_t at=mutations[i];unsigned char saved=data[at];data[at]=255;
  assert(!im2_original_tables_decode(data,size));assert(!im2_original_tables_ready());
  assert(b24_g137_source_lua_event_count==0);
  data[at]=saved;
 }
 assert(!im2_original_tables_decode(NULL,size));
 assert(!im2_original_tables_load("/this/im2/asset/does/not/exist"));
 assert(im2_original_tables_decode(data,size));
 im2_original_tables_close();free(data);
 puts("PASS external table parser: truncation, bounds, signedness, missing data, atomic publication");
 return 0;
}
