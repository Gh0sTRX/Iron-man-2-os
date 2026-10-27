/* G303 real single G8/Vita source owner, synthetic two-pose IM2V bytes.
 * One accepted B16 shot may NOT mutate to a fresh attack when the stick
 * turns or when WM changes ground -> hover / hover -> flight -> rush.
 * MarkVI uses same guard. No fake 2010 attack semantics, VPK, or FX. */
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float x,y,z,u,v;} Vertex;
static void make_clip(const char *stem,uint32_t nv){
 char path[256];int n=snprintf(path,sizeof(path),"%s.im2v",stem);
 assert(n>0&&(size_t)n<sizeof(path));
 FILE *f=fopen(path,"wb");assert(f);
 const uint32_t header[5]={0x56324d49u,nv,5u,20u,200u};
 assert(fwrite(header,1,sizeof(header),f)==sizeof(header));
 for(uint32_t t=0;t<5;t++)for(uint32_t i=0;i<nv;i++){
   float v[3]={(float)t,(float)(i%13u)*.01f,(float)t*.01f};
   assert(fwrite(v,1,sizeof(v),f)==sizeof(v));
 }
 assert(fclose(f)==0);
}
static void rm(const char *stem){
 char path[256];int n=snprintf(path,sizeof(path),"%s.im2v",stem);
 assert(n>0&&(size_t)n<sizeof(path));
 assert(remove(path)==0);
}
static void tick(B24G8LiveOriginalMotion *a,Vertex *v,uint32_t nv,int suit,
                 B24MotionStage stage,float x,float y,uint32_t t,
                 const char *source,const char *expect){
 assert(b24_g8_motion_tick_g84(a,".",v,sizeof(*v),nv,suit,
                              stage,x,y,t,source));
 assert(a->active&&!a->missing&&a->stream.file);
 assert(!strcmp(a->selected,expect));
}
int main(void){
 const char *const wg_f="warmachine_warmachine_aim_ground_move_f";
 const char *const wg_b="warmachine_warmachine_aim_ground_move_b";
 const char *const wg_f_att="warmachine_warmachine_aim_ground_move_f_att";
 const char *const wg_b_att="warmachine_warmachine_aim_ground_move_b_att";
 const char *const wh_f="warmachine_warmachine_aim_float_move_f";
 const char *const wh_f_att="warmachine_warmachine_aim_float_move_f_att";
 const char *const wf="warmachine_warmachine_aim_fly_m";
 const char *const mg_f="ironman_ironman_aim_ground_move_f";
 const char *const mg_b="ironman_ironman_aim_ground_move_b";
 const char *const mg_f_att="ironman_ironman_aim_ground_move_f_att";
 const char *const mg_b_att="ironman_ironman_aim_ground_move_b_att";
 const char *const names[]={
   wg_f,wg_b,wg_f_att,wg_b_att,wh_f,wh_f_att,wf,
   mg_f,mg_b,mg_f_att,mg_b_att
 };
 for(size_t i=0;i<sizeof(names)/sizeof(names[0]);i++)
   make_clip(names[i],i<7u?1292u:802u);
 Vertex *v=calloc(1292u,sizeof(Vertex));assert(v);
 B24G8LiveOriginalMotion a={0};
 tick(&a,v,1292u,2,B24M_WALK,0.f,1.f,1000,wg_f,wg_f);
 b24_g8_motion_repulsor_trigger(&a,1001);
 tick(&a,v,1292u,2,B24M_WALK,0.f,1.f,1016,wg_f,wg_f_att);
 assert(a.repulsor_pending&&a.whole_body_repulsor_active);
 assert(a.repulsor_domain==1);
 uint32_t shot_start=a.started_ms;
 unsigned transitions=a.transitions;
 tick(&a,v,1292u,2,B24M_WALK,0.f,-1.f,1032,wg_b,wg_f_att);
 assert(a.started_ms==shot_start&&a.transitions==transitions);
 tick(&a,v,1292u,2,B24M_WALK,0.f,-1.f,1050,wg_b,wg_f_att);
 assert(a.started_ms==shot_start&&a.transitions==transitions);
 /* Still ONE old accepted ground shot; newly hovered WM must not fire. */
 tick(&a,v,1292u,2,B24M_DRIFT,0.f,1.f,1066,wh_f,wh_f);
 assert(!a.repulsor_pending&&!a.whole_body_repulsor_active);
 tick(&a,v,1292u,2,B24M_WALK,0.f,-1.f,1082,wg_b,wg_b);
 b24_g8_motion_repulsor_trigger(&a,1090);
 tick(&a,v,1292u,2,B24M_WALK,0.f,1.f,1098,wg_f,wg_f_att);
 tick(&a,v,1292u,2,B24M_WALK,0.f,-1.f,1289,wg_b,wg_f_att);
 tick(&a,v,1292u,2,B24M_WALK,0.f,-1.f,1290,wg_b,wg_b);
 assert(!a.repulsor_pending&&!a.whole_body_repulsor_active);
 /* A WM hover shot may not survive flight Stage2/Rush. */
 tick(&a,v,1292u,2,B24M_DRIFT,0.f,1.f,1330,wh_f,wh_f);
 b24_g8_motion_repulsor_trigger(&a,1331);
 tick(&a,v,1292u,2,B24M_DRIFT,0.f,1.f,1346,wh_f,wh_f_att);
 tick(&a,v,1292u,2,B24M_CRUISE,0.f,1.f,1362,wf,wf);
 assert(!a.repulsor_pending&&!a.whole_body_repulsor_active);
 tick(&a,v,1292u,2,B24M_RUSH,0.f,1.f,1378,wf,wf);
 assert(!a.repulsor_pending&&!a.whole_body_repulsor_active);
 b24_g8_motion_release(&a);
 /* MarkVI directional stick flip uses exactly the SAME source event
  * semantics and cannot restart a new _att stream. */
 tick(&a,v,802u,0,B24M_WALK,0.f,1.f,2000,mg_f,mg_f);
 b24_g8_motion_repulsor_trigger(&a,2001);
 tick(&a,v,802u,0,B24M_WALK,0.f,1.f,2016,mg_f,mg_f_att);
 transitions=a.transitions;shot_start=a.started_ms;
 tick(&a,v,802u,0,B24M_WALK,0.f,-1.f,2032,mg_b,mg_f_att);
 assert(a.started_ms==shot_start&&a.transitions==transitions);
 tick(&a,v,802u,0,B24M_WALK,0.f,-1.f,2216,mg_b,mg_b);
 assert(!a.repulsor_pending&&!a.whole_body_repulsor_active);
 b24_g8_motion_release(&a);
 free(v);
 for(size_t i=0;i<sizeof(names)/sizeof(names[0]);i++)rm(names[i]);
 puts("G303 PASS single real G8 source streamer: WM and MarkVI direction pin, ground/hover/flight/rush shot owner cancellation, exact synthetic 200ms source duration; NO VPK");
 return 0;
}
