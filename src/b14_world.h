#ifndef B14_WORLD_H
#define B14_WORLD_H
#include <stdint.h>
typedef struct {
    float x,y,z,heading,orbit,pitch,cam_x,cam_y,cam_z;
    float target_z, speed, cooldown, beam_time, head_height, camera_distance, wave_timer;
    float screen_x,screen_y,screen_radius;
    int flying,rush,hits,shots,completed,visible,flight_stage,total_hits,waves;
 float authored_move_vx, authored_move_vy; /* G75 one B14 owner */
 /* B14_WORLD_HEIGHT_SUPPORT: accepted support and fixed takeoff datum.
  * No second integrator; no inferred original mission spawn/flight rules. */
 float ground_z, flight_base_z;
 int ground_supported;
} B14World;
void b14_world_init(B14World *w);
void b14_world_tick(B14World *w,float dt,float strafe,float forward,float yaw,float pitch,float vertical);
void b14_world_project(const B14World *w,float x,float y,float z,float *sx,float *sy,float *scale);
void b14_world_target(B14World *w);
int b14_world_fire(B14World *w);
void b15_world_spawn(B14World *w);
#define B14_WORLD_HEIGHT_SUPPORT 1
void b14_world_toggle_flight(B14World *w);
void b14_world_accept_ground_support(B14World *w,int found,float support_z);
#endif
