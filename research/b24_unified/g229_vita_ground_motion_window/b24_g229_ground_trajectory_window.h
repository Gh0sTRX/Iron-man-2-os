/* G229 read-only, 120 SUCCESSIVE rendered ground frames. NOT a movement fix.
 * C1L1 is Z-up; horizontal coordinates are world X/Y.
 * Camera fields in G227 snapshot contain POSITION, not a look-at target.
 * Thresholds are diagnostic heuristics, NOT recovered original iOS values.
 */
#ifndef B24_G229_GROUND_TRAJECTORY_WINDOW_H
#define B24_G229_GROUND_TRAJECTORY_WINDOW_H
#include "b24_g227_vita_ground_world_render_probe.h"
#include <math.h>
#include <stdint.h>
#include <string.h>
#define B24_G229_WINDOW_FRAMES 120u

typedef enum {
 B24_G229_INCOMPLETE=0,
 B24_G229_INSUFFICIENT_STICK_INPUT,
 B24_G229_GPU_ROOT_DIVERGES_FROM_WORLD,
 B24_G229_B14_NO_MOTION,
 B24_G229_COLLISION_REJECTS_MOTION,
 B24_G229_WORLD_PATH_SMALL_INCONCLUSIVE,
 B24_G229_WORLD_PATH_NET_SMALL_TURNS,
 B24_G229_WORLD_AND_CAMERA_TRANSLATE_TOGETHER,
 B24_G229_WORLD_MOVES_CAMERA_RELATIVE_OFFSET_CHANGES
} B24G229WindowVerdict;

typedef struct {
 uint32_t samples,active_stick_frames,b14_idle_frames,collision_reject_frames;
 uint32_t root_mismatch_frames,missing_original_clip_frames;
 uint32_t previous_frame,first_tick_ms,last_tick_ms;
 float first_world_x,first_world_y,last_world_x,last_world_y;
 /* G256: Real source C1L1 Z-up height of same single rendered world root. */
 float first_world_z,last_world_z,min_world_z,max_world_z;
 float first_camera_x,first_camera_y,last_camera_x,last_camera_y;
 double b14_path_xy,resolved_path_xy,max_gpu_root_error;
} B24G229WalkWindow;

static inline void b24_g229_window_reset(B24G229WalkWindow *w) {
 if(w)memset(w,0,sizeof(*w));
}
static inline int b24_g229_window_push(B24G229WalkWindow *w,
                                      const B24G227GroundProbe *q,
                                      uint32_t tick_ms){
 if(!w)return 0;
 /* A pause, flying, nonfinite coordinates, and discontinuous rendered
  * frame numbers must NEVER be stitched into one fake ground path. */
 if(!q||!q->recorded||q->flying||
    b24_g227_qa_classify(q)==B24_G227_NONFINITE_RUNTIME_STATE){
  b24_g229_window_reset(w);return 0;
 }
 if(w->samples && (q->frame_num!=w->previous_frame+1u ||
                   (uint32_t)(tick_ms-w->last_tick_ms)>250u))
  b24_g229_window_reset(w);
 if(!w->samples){
  w->first_tick_ms=tick_ms;
  w->first_world_x=q->old_world_x;
  w->first_world_y=q->old_world_y;
  w->first_world_z=q->resolved_world_z;
  w->min_world_z=q->resolved_world_z;
  w->max_world_z=q->resolved_world_z;
  w->first_camera_x=q->camera_target_x;
  w->first_camera_y=q->camera_target_y;
 }
 w->previous_frame=q->frame_num;
 w->last_tick_ms=tick_ms;
 w->last_world_x=q->resolved_world_x;
 w->last_world_y=q->resolved_world_y;
 w->last_world_z=q->resolved_world_z;
 if(q->resolved_world_z<w->min_world_z)w->min_world_z=q->resolved_world_z;
 if(q->resolved_world_z>w->max_world_z)w->max_world_z=q->resolved_world_z;
 w->last_camera_x=q->camera_target_x;
 w->last_camera_y=q->camera_target_y;
 w->samples++;
 if(!q->original_G8_clip_loaded||q->original_G8_source_clip_missing)
  w->missing_original_clip_frames++;
 if(hypotf(q->stick_x,q->stick_y)>=.18f){
  const double proposed=hypot((double)q->proposed_world_x-q->old_world_x,
                              (double)q->proposed_world_y-q->old_world_y);
  const double resolved=hypot((double)q->resolved_world_x-q->old_world_x,
                              (double)q->resolved_world_y-q->old_world_y);
  /* The rendered pose root has the same XYZ reference as resolved
   * world. G168's native-bind offset belongs to the mesh matrix, not
   * this pose; a Z-only mismatch must count in the 120-frame evidence. */
  const double root_error=hypot(
    hypot((double)q->gpu_actor_world_x-q->resolved_world_x,
          (double)q->gpu_actor_world_y-q->resolved_world_y),
    (double)q->gpu_actor_world_z-q->resolved_world_z);
  w->active_stick_frames++;
  w->b14_path_xy+=proposed;
  w->resolved_path_xy+=resolved;
  if(proposed<.0001)w->b14_idle_frames++;
  if(proposed>=.0001 && resolved<.0001)w->collision_reject_frames++;
  if(root_error>.005)w->root_mismatch_frames++;
  if(root_error>w->max_gpu_root_error)w->max_gpu_root_error=root_error;
 }
 return w->samples==B24_G229_WINDOW_FRAMES;
}
static inline B24G229WindowVerdict b24_g229_window_classify(
 const B24G229WalkWindow *w){
 if(!w||w->samples!=B24_G229_WINDOW_FRAMES)return B24_G229_INCOMPLETE;
 if(w->active_stick_frames<80u)return B24_G229_INSUFFICIENT_STICK_INPUT;
 if(w->root_mismatch_frames>=3u)return B24_G229_GPU_ROOT_DIVERGES_FROM_WORLD;
 if(w->b14_idle_frames>=80u)return B24_G229_B14_NO_MOTION;
 if(w->collision_reject_frames>=80u)return B24_G229_COLLISION_REJECTS_MOTION;
 if(w->resolved_path_xy<.04)return B24_G229_WORLD_PATH_SMALL_INCONCLUSIVE;
 const double wx=(double)w->last_world_x-w->first_world_x;
 const double wy=(double)w->last_world_y-w->first_world_y;
 const double cx=(double)w->last_camera_x-w->first_camera_x;
 const double cy=(double)w->last_camera_y-w->first_camera_y;
 if(hypot(wx,wy)<.15)return B24_G229_WORLD_PATH_NET_SMALL_TURNS;
 const double net_world=hypot(wx,wy);
 const double net_camera=hypot(cx,cy);
 const double relative_tolerance=fmin(.25,.03+.15*net_world);
 if(net_camera>=.5*net_world &&
    hypot(wx-cx,wy-cy)<=relative_tolerance)
  return B24_G229_WORLD_AND_CAMERA_TRANSLATE_TOGETHER;
 return B24_G229_WORLD_MOVES_CAMERA_RELATIVE_OFFSET_CHANGES;
}
static inline const char *b24_g229_window_verdict_name(B24G229WindowVerdict v){
 switch(v){
 case B24_G229_INCOMPLETE:return "INCOMPLETE_120_RENDERED_GROUND_FRAMES";
 case B24_G229_INSUFFICIENT_STICK_INPUT:return "STICK_INSUFFICIENT_FOR_CAUSAL_INFERENCE";
 case B24_G229_GPU_ROOT_DIVERGES_FROM_WORLD:return "GPU_RENDER_ROOT_DISAGREES_WITH_WORLD";
 case B24_G229_B14_NO_MOTION:return "B14_NO_GROUND_TRANSLATION";
 case B24_G229_COLLISION_REJECTS_MOTION:return "COLLISION_REJECTS_GROUND_MOTION";
 case B24_G229_WORLD_PATH_SMALL_INCONCLUSIVE:return "WORLD_PATH_SMALL_INCONCLUSIVE";
 case B24_G229_WORLD_PATH_NET_SMALL_TURNS:return "WORLD_MOVED_BUT_NET_SMALL_OR_REVERSED";
 case B24_G229_WORLD_AND_CAMERA_TRANSLATE_TOGETHER:return "WORLD_AND_CAMERA_POSITIONS_TRANSLATE_TOGETHER";
 case B24_G229_WORLD_MOVES_CAMERA_RELATIVE_OFFSET_CHANGES:return "WORLD_MOVES_CAMERA_OFFSET_CHANGED_CHECK_VIEW";
 default:return "INVALID_G229_VERDICT";
 }
}
#endif
