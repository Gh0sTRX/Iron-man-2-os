#ifndef B24_G8_LIVE_ORIGINAL_MOTION_H
#define B24_G8_LIVE_ORIGINAL_MOTION_H
#include "b24_original_im2v_stream.h"
#include "b24_hover_pose_blend.h"
#include <stddef.h>
#include <stdint.h>

/* G8 SOURCE branch; only actual matching source Mark VI 802v and WM 1292v.
   Requires original derived streams staged separately; preserve G8 59 fallback.
   B14 already computed the single authoritative world pose/physics for frame.
   B16 right-arm repulsor overlay runs AFTER this base-body update.
   NO 2010 button timings / missile semantics claimed. */
typedef enum {
 B24M_IDLE=0,B24M_WALK,B24M_RUN,B24M_HOVER,
 B24M_DRIFT,B24M_CRUISE,B24M_RUSH,B24M_LAND
} B24MotionStage;
typedef struct {
 B24OriginalIM2VStream stream;
 B24HoverPoseBlend blend;
 float *source_xyz,*result_xyz,*snapshot_xyz;
 size_t nv;
 int suit_index,missing;
 char selected[128];
 uint32_t started_ms,previous_ms,repulsor_started_ms;
 int active,repulsor_pending,whole_body_repulsor_active;
 unsigned transitions,misses,successful_frames;
} B24G8LiveOriginalMotion;
void b24_g8_motion_release(B24G8LiveOriginalMotion *a);
/* Call ONCE on an accepted B16_REPULSOR fire event (never during missiles/
   unibeam), AFTER pose computation. The original source clip begins NEXT
   frame; if missing, B16 old right-palm blend still works as fallback. */
void b24_g8_motion_repulsor_trigger(B24G8LiveOriginalMotion *a,uint32_t now_ms);
int b24_g8_motion_whole_body_fire(const B24G8LiveOriginalMotion *a);
const char *b24_g8_motion_repulsor_clip(int suit_index,B24MotionStage stage,
                                        float left_x,float forward);
const char *b24_g8_motion_route(int suit_index,B24MotionStage stage,
                                float left_x,float forward);
int b24_g8_motion_tick(B24G8LiveOriginalMotion *a,const char *animation_dir,
                      void *vertices,size_t stride,size_t nv,int suit_index,
                      B24MotionStage stage,float left_x,float forward,
                      uint32_t now_ms);
/* Return 1 for safe success even when source file is absent: no change to
   existing B14/B16 pose. 0 means detected memory/numeric internal error. */
#endif
