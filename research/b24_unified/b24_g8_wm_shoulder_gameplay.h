#ifndef B24_G8_WM_SHOULDER_GAMEPLAY_H
#define B24_G8_WM_SHOULDER_GAMEPLAY_H
#include <stddef.h>

/* Iron Man 2 FILM orientation, verified independently: LEFT rocket pod,
   RIGHT articulated M134-type gatling. Coordinates supplied by real suit
   model socket provider; these are not discovered BRES sockets yet. */
typedef struct {float x,y,z;} B24WMVec3;
typedef struct {
 int id;
 B24WMVec3 center;
 int alive,visible,occluded;
} B24WMTarget;
typedef enum {
 B24WM_EVENT_NONE=0,
 B24WM_EVENT_MISSILE_LAUNCH_LEFT,
 B24WM_EVENT_MISSILE_EXHAUST_LEFT,
 B24WM_EVENT_GATLING_SHOT_RIGHT,
 B24WM_EVENT_GATLING_SPARK_RIGHT
} B24WMEventKind;
typedef struct {
 B24WMEventKind kind;
 int target_id;
 B24WMVec3 origin,direction;
 float damage;
} B24WMEvent;
typedef struct {
 float skill_active_seconds;          /* prototype requested: 20s */
 float skill_cooldown_seconds;        /* 20s after active phase */
 float gatling_interval_seconds;      /* adjustable fire cadence */
 float gatling_range;                 /* game world units */
 float missile_cooldown_seconds;
} B24WMConfig;
typedef struct {
 B24WMConfig config;
 float active_left,cooldown_left,shot_left,missile_left;
 int last_target_id;
 unsigned fired_gatling,fired_missiles,locks;
} B24WMShoulder;
typedef struct {
 int war_machine_selected;
 int real_enemies_loaded; /* 0 -> NO phantom targets, NO invisible damage */
 int trigger_skill_edge,trigger_missile_edge;
 B24WMVec3 muzzle_left_rocket,muzzle_right_gatling;
 B24WMVec3 rocket_aim_direction; /* from source-verified player targeting */
 const B24WMTarget *targets;
 size_t target_count;
 float dt;
} B24WMInput;
typedef struct {
 B24WMEvent events[8];
 unsigned event_count;
 int active,ready,locked_target_id;
 float active_left,cooldown_left;
} B24WMOutput;
void b24_wm_default_config(B24WMConfig *cfg);
int b24_wm_init(B24WMShoulder *a,const B24WMConfig *cfg);
int b24_wm_tick(B24WMShoulder *a,const B24WMInput *in,B24WMOutput *out);
#endif
