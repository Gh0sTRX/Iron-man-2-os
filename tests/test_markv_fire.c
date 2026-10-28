/* Reproduce the actual Mark V accepted-shot route on consecutive G8 frames.
 * Synthetic stream structure or optional original streams; no new hit rules. */
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const char *suffix[]={"aim_ground_move_f","aim_ground_move_b","aim_ground_move_f_att","aim_float_move_f","aim_float_move_f_att"};
static void fixture(const char *name){
 char path[180];snprintf(path,sizeof(path),"suitcase_ironman_%s.im2v",name);
 FILE *f=fopen(path,"wb");assert(f);const uint32_t h[]={0x56324d49,629,5,20,200};
 assert(fwrite(h,1,20,f)==20);
 for(unsigned t=0;t<5;t++)for(unsigned i=0;i<629;i++){
  const float xyz[]={(float)i*.001f,(float)t*.01f,0.f};assert(fwrite(xyz,1,12,f)==12);
 }assert(!fclose(f));
}
static void frame(B24G8LiveOriginalMotion *a,float *v,const char *root,B24MotionStage mode,float direction,uint32_t now,const char *route){
 int ok=b24_g8_motion_tick_g84(a,root,v,12,629,4,mode,0,direction,now,route);
 if(!ok)fprintf(stderr,"Mark V selected=%s active=%d shot=%d at=%u\n",a->selected,a->active,a->whole_body_repulsor_active,now);
 assert(ok&&a->active&&!a->missing&&a->stream.file&&a->nv==629);
}
int main(int argc,char **argv){
 assert(argc==1||argc==2);const char *root=argc==2?argv[1]:".";
 if(argc==1)for(unsigned i=0;i<5;i++)fixture(suffix[i]);
 float v[629*3]={0};B24G8LiveOriginalMotion a={0};
 const char *forward="ironman_ironman_aim_ground_move_f",*back="ironman_ironman_aim_ground_move_b";
 frame(&a,v,root,B24M_WALK,1,1000,forward);b24_g8_motion_repulsor_trigger(&a,1001);
 frame(&a,v,root,B24M_WALK,1,1016,forward);
 assert(a.whole_body_repulsor_active&&!strcmp(a.selected,"suitcase_ironman_aim_ground_move_f_att"));
 const uint32_t began=a.started_ms,duration=a.stream.duration_ms;const unsigned transitions=a.transitions;
 frame(&a,v,root,B24M_WALK,1,1032,forward);
 frame(&a,v,root,B24M_WALK,-1,1048,back);
 assert(a.whole_body_repulsor_active&&a.started_ms==began&&a.transitions==transitions);
 frame(&a,v,root,B24M_WALK,-1,began+duration-1,back);
 frame(&a,v,root,B24M_WALK,-1,began+duration,back);
 assert(!a.repulsor_pending&&!strcmp(a.selected,"suitcase_ironman_aim_ground_move_b"));
 const char *hover="ironman_ironman_aim_float_move_f";
 frame(&a,v,root,B24M_DRIFT,1,4000,hover);b24_g8_motion_repulsor_trigger(&a,4001);
 frame(&a,v,root,B24M_DRIFT,1,4016,hover);frame(&a,v,root,B24M_DRIFT,1,4032,hover);
 assert(!strcmp(a.selected,"suitcase_ironman_aim_float_move_f_att")&&a.whole_body_repulsor_active);
 frame(&a,v,root,B24M_WALK,1,4048,forward);assert(!a.repulsor_pending&&!a.whole_body_repulsor_active);
 b24_g8_motion_release(&a);
 if(argc==1)for(unsigned i=0;i<5;i++){
  char path[180];snprintf(path,sizeof(path),"suitcase_ironman_%s.im2v",suffix[i]);assert(!remove(path));
 }
 puts("PASS actual Mark V G8 shot: consecutive frames, direction pin, exact end, hover shot, domain cancellation");return 0;
}
