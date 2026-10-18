#include "b24_g229_ground_trajectory_window.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef enum {FOLLOW=0,STATIC_CAM,STUCK_B14,COLLISION,GPU_ERROR,NO_INPUT,REVERSAL} Scenario;
static B24G229WindowVerdict simulate(Scenario kind){
 B24G229WalkWindow w={0};
 B24G227GroundProbe q={0};
 float world=1.0f;
 for(uint32_t i=0;i<B24_G229_WINDOW_FRAMES;i++){
  const float step=(kind==STUCK_B14||kind==NO_INPUT)?0.f:
                   (kind==REVERSAL && i>=60u?-.05f:.05f);
  q=(B24G227GroundProbe){0};q.recorded=1;q.frame_num=i;
  q.stick_y=(kind==NO_INPUT)?0.f:1.f;
  q.original_G8_clip_loaded=1;
  q.old_world_y=world;
  q.proposed_world_y=world+step;
  q.resolved_world_y=(kind==COLLISION)?world:world+step;
  world=q.resolved_world_y;
  q.gpu_actor_world_y=world+((kind==GPU_ERROR)?.3f:0.f);
  q.camera_target_y=(kind==STATIC_CAM)?-3.f:world-4.f;
  if(i+1u<B24_G229_WINDOW_FRAMES)
    assert(!b24_g229_window_push(&w,&q,i*17u));
  else assert(b24_g229_window_push(&w,&q,i*17u));
 }
 assert(w.samples==120u);
 assert(w.last_tick_ms-w.first_tick_ms==119u*17u);
 return b24_g229_window_classify(&w);
}
int main(void){
 assert(simulate(FOLLOW)==B24_G229_WORLD_AND_CAMERA_TRANSLATE_TOGETHER);
 assert(simulate(STATIC_CAM)==B24_G229_WORLD_MOVES_CAMERA_RELATIVE_OFFSET_CHANGES);
 assert(simulate(STUCK_B14)==B24_G229_B14_NO_MOTION);
 assert(simulate(COLLISION)==B24_G229_COLLISION_REJECTS_MOTION);
 assert(simulate(GPU_ERROR)==B24_G229_GPU_ROOT_DIVERGES_FROM_WORLD);
 assert(simulate(NO_INPUT)==B24_G229_INSUFFICIENT_STICK_INPUT);
 assert(simulate(REVERSAL)==B24_G229_WORLD_PATH_NET_SMALL_TURNS);
 B24G229WalkWindow w={0};
 B24G227GroundProbe q={0};q.recorded=1;q.stick_y=1.f;
 q.frame_num=10u;
 assert(!b24_g229_window_push(&w,&q,100u));
 q.frame_num=12u; /* Gap -> reset; no fake multi-frame tracking */
 assert(!b24_g229_window_push(&w,&q,110u));assert(w.samples==1u);
 q.frame_num=13u;
 assert(!b24_g229_window_push(&w,&q,500u));assert(w.samples==1u);
 q.frame_num=14u;q.flying=1;
 assert(!b24_g229_window_push(&w,&q,120u));assert(w.samples==0u);
 q.flying=0;q.frame_num=15u;
 assert(!b24_g229_window_push(&w,&q,130u));assert(w.samples==1u);
 q.recorded=0;
 assert(!b24_g229_window_push(&w,&q,140u));assert(w.samples==0u);
 q.recorded=1;q.frame_num=0u;q.old_world_y=0.f;
 assert(!b24_g229_window_push(&w,&q,150u));
 q.frame_num=1u;q.gpu_actor_world_y=NAN;
 assert(!b24_g229_window_push(&w,&q,160u));assert(w.samples==0u);
 assert(!strcmp(b24_g229_window_verdict_name(B24_G229_GPU_ROOT_DIVERGES_FROM_WORLD),
                "GPU_RENDER_ROOT_DISAGREES_WITH_WORLD"));
 printf("G229 HOST PASS: 7 original-path synthetic scenarios, discontinuity/flight/pause/NaN resets; READ-ONLY; no VPK.\n");
 return 0;
}
