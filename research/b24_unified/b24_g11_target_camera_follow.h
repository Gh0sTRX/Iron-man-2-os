#ifndef B24_G11_TARGET_CAMERA_FOLLOW_H
#define B24_G11_TARGET_CAMERA_FOLLOW_H
/* Target-centric chase camera for permanently invincible G10 practice actor.
   Only modifies existing B14 orbit, not player yaw, world movement,
   target health, or a second camera simulation. */
typedef struct {
 float player_x,player_y,actor_x,actor_y,dt,orbit;
 int lock_held,melee_active,manual_camera_input,world_flying;
} B24G11CameraFocusInput;
typedef struct {float orbit,zoom_reduction;int focusing;} B24G11CameraFocus;
int b24_g11_target_camera_follow(const B24G11CameraFocusInput *i,
                                  B24G11CameraFocus *out);
#endif
