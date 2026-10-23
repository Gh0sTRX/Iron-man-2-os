#include "b24_g227_vita_ground_world_render_probe.h"
#include <assert.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
int main(void){
 B24G227GroundProbe q={0};
 assert(b24_g227_qa_classify(&q)==B24_G227_NOT_SAMPLED);
 q.recorded=1;q.stick_y=1.f;
 q.old_world_x=0.f;q.old_world_y=1.1f;
 q.proposed_world_x=0.f;q.proposed_world_y=1.15f;
 q.resolved_world_x=0.f;q.resolved_world_y=1.15f;
 q.gpu_actor_world_x=0.f;q.gpu_actor_world_y=1.15f;
 q.camera_target_x=0.f;q.camera_target_y=1.15f;
 assert(b24_g227_qa_classify(&q)==B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED);
 assert(!strcmp(b24_g227_walk_verdict_name(b24_g227_qa_classify(&q)),
                 "WORLD_MOVES_GPU_ROOT_SYNCED_CAMERA_UNDETERMINED"));
 q.camera_target_y=-.5f; /* correct camera offset is not a root error */
 assert(b24_g227_qa_classify(&q)==B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED);
 q.gpu_actor_world_y=1.10f;
 assert(b24_g227_qa_classify(&q)==B24_G227_GPU_ROOT_TRANSFORM_MISMATCH);
 q.gpu_actor_world_y=1.15f;
 /* GPU frame_pose copies camera.player XYZ, which copies resolved B14
  * world XYZ. G168's bind-foot adjustment happens later in the model
  * matrix and must not excuse an unequal GPU root Z. Synthetic only. */
 q.resolved_world_z=.0725f;q.gpu_actor_world_z=2.82955f;
 assert(b24_g227_qa_classify(&q)==B24_G227_GPU_ROOT_TRANSFORM_MISMATCH);
 q.gpu_actor_world_z=q.resolved_world_z-.02f;
 assert(b24_g227_qa_classify(&q)==B24_G227_GPU_ROOT_TRANSFORM_MISMATCH);
 q.gpu_actor_world_z=q.resolved_world_z+.004f;
 assert(b24_g227_qa_classify(&q)==B24_G227_WORLD_MOVING_GPU_ROOT_SYNCED);
 q.gpu_actor_world_z=q.resolved_world_z;
 q.camera_target_y=1.15f;
 q.resolved_world_y=1.1f;q.gpu_actor_world_y=1.1f;
 assert(b24_g227_qa_classify(&q)==B24_G227_COLLISION_REJECTED_B14_DELTA);
 q.proposed_world_y=1.1f;
 assert(b24_g227_qa_classify(&q)==B24_G227_B14_TICK_DID_NOT_MOVE);
 q.stick_y=0.f;
 assert(b24_g227_qa_classify(&q)==B24_G227_NO_VALID_MOVEMENT_INPUT);
 q.stick_y=1.f;q.proposed_world_y=1.15f;q.resolved_world_y=1.15f;
 q.gpu_actor_world_y=1.15f;q.flying=1;
 assert(b24_g227_qa_classify(&q)==B24_G227_FLIGHT_NOT_GROUND);
 q.flying=0;q.gpu_actor_world_x=NAN;
 assert(b24_g227_qa_classify(&q)==B24_G227_NONFINITE_RUNTIME_STATE);
 q.gpu_actor_world_x=0.f;q.recorded=0;
 assert(b24_g227_qa_classify(&q)==B24_G227_NOT_SAMPLED);
 puts("G227 PASS: source runtime telemetry separates analog/B14/collision/GPU XYZ root mismatch including original-floor-height Z-only discrepancies; no camera-lag inference or Vita ground bug fix, NO VPK.");
 return 0;
}
