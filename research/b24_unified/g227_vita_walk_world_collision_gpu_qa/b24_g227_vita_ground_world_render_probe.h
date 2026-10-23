/* G227 -- diagnostic ONLY, no B14 root-motion rewrite.
 * Original iOS source G213B proves Move_Walk(2), Move_Run(3), but real
 * Vita user saw animation playing in place. G171 host proves isolated
 * B14 + native authored 2010 G66C collision can move.
 * G226 proves code source root B14 -> camera.player_xyz ->
 * b24_gpu_runtime.frame_pose -> glMultMatrixf(root).
 *
 * Runtime value logging identifies INPUT vs B14 vs COLLISION vs
 * moving chase-camera illusion instead of masking the bug with
 * arbitrary speed, teleportation or extra physics owner.
 *
 * This API MUST NOT mutate world, animation, weapon, scene, camera.
 * Read-only, no VPK and no claim of hardware validation.
 */
#ifndef B24_G227_VITA_GROUND_WORLD_RENDER_PROBE_H
#define B24_G227_VITA_GROUND_WORLD_RENDER_PROBE_H
#include <math.h>
#include <stdint.h>
#include <stddef.h>
typedef enum {
 B24_G227_NOT_SAMPLED = 0,
 B24_G227_FLIGHT_NOT_GROUND = 1,
 B24_G227_NO_VALID_MOVEMENT_INPUT = 2,
 B24_G227_B14_TICK_DID_NOT_MOVE = 3,
 B24_G227_COLLISION_REJECTED_B14_DELTA = 4,
 B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED = 5,
 B24_G227_GPU_ROOT_TRANSFORM_MISMATCH = 6,
 B24_G227_NONFINITE_RUNTIME_STATE = 7
} B24G227WalkVerdict;
typedef struct {
 float stick_x,stick_y;
 float old_world_x,old_world_y;
 float proposed_world_x,proposed_world_y;
 /* G256: original C1L1 Z-up stage height; source only, no physics changes. */
 float proposed_world_z;
 float resolved_world_x,resolved_world_y;
 float resolved_world_z;
 float gpu_actor_world_x,gpu_actor_world_y;
 float gpu_actor_world_z;
 /* Legacy field stores camera.cam_x/y = camera POSITION, not aim target.
  * One-frame camera distance cannot diagnose third-person following. */
 float camera_target_x,camera_target_y;
 uint32_t frame_num;
 uint8_t original_G8_clip_loaded;
 uint8_t original_G8_source_clip_missing;
 uint8_t flying;
 uint8_t recorded;
} B24G227GroundProbe;
static inline B24G227WalkVerdict b24_g227_qa_classify(
 const B24G227GroundProbe *q){
 if(!q||!q->recorded)return B24_G227_NOT_SAMPLED;
 const float v[]={q->stick_x,q->stick_y,q->old_world_x,q->old_world_y,
   q->proposed_world_x,q->proposed_world_y,q->proposed_world_z,
   q->resolved_world_x,q->resolved_world_y,q->resolved_world_z,
   q->gpu_actor_world_x,q->gpu_actor_world_y,q->gpu_actor_world_z,
   q->camera_target_x,q->camera_target_y};
 for(size_t i=0;i<sizeof(v)/sizeof(v[0]);i++)
  if(!isfinite(v[i]))return B24_G227_NONFINITE_RUNTIME_STATE;
 if(q->flying)return B24_G227_FLIGHT_NOT_GROUND;
 if(hypotf(q->stick_x,q->stick_y)<.18f)
  return B24_G227_NO_VALID_MOVEMENT_INPUT;
 const float b14_d=hypotf(q->proposed_world_x-q->old_world_x,
                         q->proposed_world_y-q->old_world_y);
 const float solved_d=hypotf(q->resolved_world_x-q->old_world_x,
                            q->resolved_world_y-q->old_world_y);
 /* Small movement is FRAME-rate-dependent; a single frame is a clue
  * only, not an assertion of a physically stuck Vita controller.
  * Capture repeated values in real Vita hardware before diagnosis. */
 if(b14_d<.0001f)return B24_G227_B14_TICK_DID_NOT_MOVE;
 if(solved_d<.0001f)
  return B24_G227_COLLISION_REJECTED_B14_DELTA;
 /* frame_pose is copied from camera.player XYZ before the renderer's
  * native-bind mesh offset. All three root coordinates must agree with
  * the resolved world; an incorrect Z layer must not appear synced. */
 const float root_err=hypotf(
   hypotf(q->gpu_actor_world_x-q->resolved_world_x,
          q->gpu_actor_world_y-q->resolved_world_y),
   q->gpu_actor_world_z-q->resolved_world_z);
 /* Third-person CAMERA POSITION is supposed to be metres away.
  * In one frame, only world <-> GPU root agreement can be measured.
  * A time series, not this snapshot, is needed to infer camera tracking. */
 if(root_err>.005f)return B24_G227_GPU_ROOT_TRANSFORM_MISMATCH;
 return B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED;
}
static inline const char *b24_g227_walk_verdict_name(
  B24G227WalkVerdict verdict){
 switch(verdict){
  case B24_G227_NOT_SAMPLED:return "NO_SAMPLE_PAUSE_OR_LOADING";
  case B24_G227_FLIGHT_NOT_GROUND:return "FLIGHT_NOT_GROUND";
  case B24_G227_NO_VALID_MOVEMENT_INPUT:return "STICK_INPUT_UNDER_DEADZONE";
  case B24_G227_B14_TICK_DID_NOT_MOVE:return "B14_NO_DELTA_AFTER_TICK";
  case B24_G227_COLLISION_REJECTED_B14_DELTA:return "C1L1_COLLISION_REJECTED";
  case B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED:return "WORLD_MOVES_GPU_ROOT_SYNCED_CAMERA_UNDETERMINED";
  case B24_G227_GPU_ROOT_TRANSFORM_MISMATCH:return "GPU_ACTOR_ROOT_DIFFERS_FROM_COLLISION_RESOLVED_WORLD";
  case B24_G227_NONFINITE_RUNTIME_STATE:return "INVALID_NONFINITE_STATE";
  default:return "INVALID_DIAGNOSTIC_VERDICT";
 }
}
#endif
