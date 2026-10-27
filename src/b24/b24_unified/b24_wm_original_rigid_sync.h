#ifndef B24_WM_ORIGINAL_RIGID_SYNC_H
#define B24_WM_ORIGINAL_RIGID_SYNC_H
#include "b24_wm_2010_gun_stream.h"
#include "b24_wm_original_marker_g8_world.h"
#include <stdint.h>
/* Read exactly SAME source animation and time as G8 IM2V's body pose.
   Cached missing IM2K names are NONFATAL: the 59 original G8 gameplay
   remains unchanged and no fictitious weapon emissions are produced.
   This is source-only diagnostics, not confirmed original muzzle identity. */
typedef struct {
 B24WM2010GunStream rigid;
 char selected_body_asset[128];
 float world_tip[3],world_axis[3];
 int candidate_pose_valid,source_missing;
 unsigned opens,missing_names,samples;
} B24WMRigidSync;
int b24_wm_rigid_sync_tick(B24WMRigidSync *sync,const char *asset_root,
                          const char *selected_original_body_asset,
                          uint32_t body_frames,uint32_t body_duration_ms,
                          uint32_t body_clip_started_ms,uint32_t now_ms,
                          int is_wm_and_source_body_active,
                          const B24WMG8ActorPose *actor);
void b24_wm_rigid_sync_release(B24WMRigidSync *sync);
#endif
