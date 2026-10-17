/* G174: REAL authored 2010 WM 1292-vertex Aim_M grounded clips stream
 * through the same G83 selector and one G8 IM2V animator.
 * Uses source 2010 animations already staged in work/animations from G9,
 * not synthetic clips. Source selection QA ONLY: M/native weapon meaning,
 * original missile/gatling event and actual animation trigger are UNKNOWN.
 * No second movement engine, damage, shot, model rescale or VPK. */
#include "b24_g83_unified_movement_aim.h"
#include "b24_g8_live_original_motion.h"
#include "b24_g172_wm_ground_m_source.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float x,y,z,u,v;} G174Vertex;
static void setdir(B24G83Input *in,unsigned dir){
 in->axis_x=0.f;in->axis_y=0.f;
 if(dir==1)in->axis_y=1.f;
 if(dir==2)in->axis_y=-1.f;
 if(dir==3)in->axis_x=-1.f;
 if(dir==4)in->axis_x=1.f;
}
int main(int argc,char **argv){
 if(argc!=2){
  fprintf(stderr,"Usage: G174_TRUE_WM_STREAM work/animations\n");
  return 2;
 }
 const size_t nv=1292u;
 G174Vertex *verts=calloc(nv,sizeof(*verts));
 assert(verts);
 B24G8LiveOriginalMotion animator={0};
 unsigned validated=0;
 for(unsigned attack=0;attack<2;attack++){
  for(unsigned dir=0;dir<5;dir++){
   const unsigned now=1000u+validated*100u;
   B24G83Input in={0};
   in.suit_index=B24G83_WARMACHINE;
   in.motion=B24G83_GROUND;
   in.aim=B24G83_AIM_M_UNCLASSIFIED;
   in.accepted_weapon_event=(int)attack; /* selector TEST ONLY, no shot */
   setdir(&in,dir);
   B24G83Selection result={0};
   assert(b24_g83_select_original_motion(&in,&result));
   const char *true_original=b24_g172_wm_m_ground_clip(dir,(int)attack);
   const uint32_t duration=b24_g172_wm_m_ground_duration(true_original);
   assert(true_original&&duration&&result.stem);
   assert(!strcmp(result.stem,true_original));
   assert(result.original_source_duration_ms==duration);
   assert(!result.input_semantics_verified_original_ios);
   assert(b24_g8_motion_tick_g84(&animator,argv[1],verts,
                                sizeof(*verts),nv,2,B24M_WALK,
                                in.axis_x,in.axis_y,now,result.stem));
   assert(animator.active&&!animator.missing&&animator.stream.file);
   assert(!strcmp(animator.selected,true_original));
   assert(animator.stream.duration_ms==duration);
   assert(!animator.repulsor_pending);
   assert(!animator.whole_body_repulsor_active);
   assert(animator.successful_frames==validated+1u);
   validated++;
   printf("G174 REAL original 2010 WM IM2V loaded suit=WM mode=GROUND_M name=%s duration=%ums clip_vertices=%u\n",
          true_original,duration,animator.stream.nv);
  }
 }
 assert(validated==10);
 b24_g8_motion_release(&animator);
 free(verts);
 puts("G174 PASS all 10 real original 2010 1292-vertex WarMachine Aim_M Ground IM2V source files selected by G172 G83 and streamed by existing G8. Weapon meaning/actual native input unproven; no VPK.");
 return 0;
}
