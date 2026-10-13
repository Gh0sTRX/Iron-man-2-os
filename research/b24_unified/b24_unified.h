#ifndef B24_UNIFIED_GAMEPLAY_H
#define B24_UNIFIED_GAMEPLAY_H
#include "../b19/host_gameplay/b19_gameplay_core.h"
#include "../b21_controls/b21_control_lab.h"
#include "../b22_hud/b22_visor.h"
#include "../b23_missile_lock/b23_missile_lock.h"
#include "../b22_flight/im2_flight.h"
#include "../b22_camera/im2_camera.h"
#include "../b22_4_6/im2_thruster.h"
#include "../b22_4_6/im2_speed_fx.h"
#include "../b22_4_6/im2_melee_focus.h"

/* One explicit B17 Z-up -> B24 Y-up bridge; B17 owns authoritative player motion.
   Not a rival locomotion simulation. Other modules receive ONE shared stage. */
typedef struct {
    Im2Vec3 player_z_up;  /* x/right, y/forward, z/up from B17 */
    float heading_rad,orbit_rad,pitch_rad;
    float left_x,left_forward,right_x,right_y;
    uint32_t buttons; /* B21 IM2_BT_... */
    int suit_index,weapon_index,stage;
    int target_visible,target_alive,target_occluded,target_id;
    float target_distance,target_health_percent;
    int target_screen_x,target_screen_y;
    int target_world_valid;
    Im2Vec3 target_z_up;
    int melee_anim_active;
    float armor_percent,shield_percent,energy_percent,ammo;
    int wave,mission_won,player_health_known;
    int real_enemies_loaded; /* 0: DO NOT activate a hidden B19 mission */
    float dt;
} B24Observation;

typedef struct {
    Im2Controls controls;
    B23Lock missile;
    B22UI hud;
    Im2FlightConfig flight_cfg;
    Im2FlightState visual_root;
    Im2CameraConfig camera_cfg;
    Im2CameraState camera_base,camera_final;
    Im2SpeedFx speed_fx;
    Im2MeleeFocusState melee_focus;
    Im2ThrusterState thruster;
    Im2ThrusterSocket sockets[IM2_THRUSTER_SOCKETS];
    Im2ThrusterOutput thruster_out;
    B19Game mission;
    int last_stage;
} B24Unified;

/* The caller owns its original B17 simulation, collision and real rendering.
   All B24 subsystems consume the same observations in a single frame transaction. */
void b24_unified_init(B24Unified *g);
void b24_unified_set_sockets(B24Unified *g,
                   const Im2ThrusterSocket six[IM2_THRUSTER_SOCKETS]);
void b24_unified_tick(B24Unified *g,const B24Observation *obs);
void b24_unified_draw_overlay(B24Unified *g,uint32_t *pixels,int stride);
float b24_unified_chase_distance(const B24Unified *g);
int b24_unified_should_fire(const B24Unified *g);
int b24_unified_should_melee(const B24Unified *g);
int b24_unified_paused(const B24Unified *g);
#endif
