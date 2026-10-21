/* G302 actual G8 Vita game streamer source regression, synthetic IM2V bytes.
 * Check BOTH MarkVI<->WarMachine suit switches during pending B16 repulsor:
 * a shot cannot leak to a new suit without that suit's accepted shot.
 * Also check WM hover -> Stage2 -> RUSH candidate pose routing.
 * Source/host only; no genuine 2010 iOS input claim or PS Vita footage. */
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float x,y,z,u,v;} V;
static void stream(const char *name,unsigned nv){
 char path[256];
 int n=snprintf(path,sizeof(path),"%s.im2v",name);
 assert(n>0&&(size_t)n<sizeof(path));
 FILE *f=fopen(path,"wb");assert(f);
 const uint32_t hdr[5]={0x56324d49u,nv,5u,20u,200u}; /* IM2V little endian */
 assert(fwrite(hdr,1,sizeof(hdr),f)==sizeof(hdr));
 for(unsigned frame=0;frame<5;frame++)for(unsigned i=0;i<nv;i++){
   const float v[3]={.01f*(float)i,.1f*(float)frame,1.f};
   assert(fwrite(v,1,sizeof(v),f)==sizeof(v));
 }
 assert(fclose(f)==0);
}
static void erase(const char *name){
 char path[256];snprintf(path,sizeof(path),"%s.im2v",name);
 assert(remove(path)==0);
}
int main(void){
 const char *const m_idle="ironman_ironman_aim_float_move_l";
 const char *const m_fire="ironman_ironman_aim_float_move_l_att";
 const char *const w_idle="warmachine_warmachine_aim_float_move_l";
 const char *const w_fire="warmachine_warmachine_aim_float_move_l_att";
 const char *const w_fly="warmachine_warmachine_aim_fly_m";
 const char *names[]={m_idle,m_fire,w_idle,w_fire,w_fly};
 stream(m_idle,802u);stream(m_fire,802u);
 stream(w_idle,1292u);stream(w_fire,1292u);stream(w_fly,1292u);
 V *m=calloc(802u,sizeof(V)),*wm=calloc(1292u,sizeof(V));
 assert(m&&wm);
 B24G8LiveOriginalMotion a={0};
 assert(b24_g8_motion_tick(&a,".",m,sizeof(V),802u,0,
                           B24M_DRIFT,-1.f,0.f,1000u));
 assert(!strcmp(a.selected,m_idle)&&a.suit_index==0&&a.active);
 b24_g8_motion_repulsor_trigger(&a,1001u);
 assert(b24_g8_motion_tick(&a,".",m,sizeof(V),802u,0,
                           B24M_DRIFT,-1.f,0.f,1016u));
 assert(!strcmp(a.selected,m_fire)&&a.repulsor_pending);
 assert(b24_g8_motion_whole_body_fire(&a));
 /* Without G302 this selected WM _att even though WM never shot. */
 assert(b24_g8_motion_tick(&a,".",wm,sizeof(V),1292u,2,
                           B24M_DRIFT,-1.f,0.f,1032u));
 assert(a.active&&!a.missing&&a.suit_index==2);
 assert(!strcmp(a.selected,w_idle));
 assert(!a.repulsor_pending&&!b24_g8_motion_whole_body_fire(&a));
 b24_g8_motion_repulsor_trigger(&a,1040u);
 assert(b24_g8_motion_tick(&a,".",wm,sizeof(V),1292u,2,
                           B24M_DRIFT,-1.f,0.f,1048u));
 assert(!strcmp(a.selected,w_fire)&&a.repulsor_pending);
 assert(b24_g8_motion_whole_body_fire(&a));
 /* Inverse: WM pending attack must not become unsolicited MarkVI _att. */
 assert(b24_g8_motion_tick(&a,".",m,sizeof(V),802u,0,
                           B24M_DRIFT,-1.f,0.f,1064u));
 assert(a.active&&a.suit_index==0&&!strcmp(a.selected,m_idle));
 assert(!a.repulsor_pending&&!b24_g8_motion_whole_body_fire(&a));
 /* No new fire, same WM native source used as experimental Stage2/Rush
  * fallback, not a claimed dedicated original 2010 WM rush animation. */
 assert(b24_g8_motion_tick(&a,".",wm,sizeof(V),1292u,2,
                           B24M_CRUISE,-1.f,0.f,1080u));
 assert(a.active&&!strcmp(a.selected,w_fly)&&!a.repulsor_pending);
 assert(b24_g8_motion_tick(&a,".",wm,sizeof(V),1292u,2,
                           B24M_RUSH,-1.f,0.f,1096u));
 /* G8 legacy WM Rush may have no authored clip; this is separately
  * filled by G165/G84 experimental candidate source on final Vita game.
  * Only verify it cannot hallucinate an accepted repulsor. */
 assert(!a.repulsor_pending&&!b24_g8_motion_whole_body_fire(&a));
 b24_g8_motion_release(&a);
 assert(!a.stream.file);
 for(size_t i=0;i<sizeof(names)/sizeof(names[0]);i++)erase(names[i]);
 free(m);free(wm);
 puts("G302 PASS genuine G8 streamer source, synthetic IM2V: MarkVI to WM and inverse attack edge reset, no phantom WM repulsor, Stage2/Rush no gun state, no VPK");
 return 0;
}
