#ifndef B16_ACTION_H
#define B16_ACTION_H
#include "b13_motion.h"
#include "b14_pose.h"
#include "b14_world.h"
#include <stdint.h>
/* Separate original-IPA-based animation layer; War Machine clips explicitly retargeted. */
typedef struct {
  B13Clip air_idle,ground_relaxed,glide;
  B13Clip beam[6]; /* Ground beam1/2/3, air beam1/2/3 */
  unsigned char *arm_mask;
  uint32_t nverts;
  uint16_t palm_l,palm_r;
  unsigned attack_started;
  int attack_clip,attack_active,hand;
} B16Action;
int b16_action_load(B16Action *a,int armor,const IM2Model *model);
void b16_action_release(B16Action *a);
const B13Clip *b16_idle_override(const B16Action *a,B14Mode mode,int armor);
void b16_attack_begin(B16Action *a,unsigned now,int flying,int hand,int variant);
void b16_apply_attack(B16Action *a,IM2Model *model,unsigned now);

enum {B16_REPULSOR,B16_UNIBEAM,B16_MISSILE,B16_MELEE,B16_WEAPON_COUNT};
/* Explicit prototype actor binding; never original NPC/mission HP. */
typedef struct {float center[3],radius,hp;unsigned hits;int present;} B16TestTarget;
typedef struct {
  B16TestTarget *test_target;
  float test_ray_origin[3],test_ray_direction[3],test_impact[3];int test_ray_valid,test_occluded,test_hit_this_shot;
  int mode,shots,total_hits,combo_step,active_missile;
  float energy,cooldown,hitpoints[3],missile_x,missile_y,missile_z,missile_t;
  unsigned wave;
  float hit_flash;
} B16Combat;
void b16_combat_init(B16Combat *c);
void b16_combat_tick(B16Combat *c,B14World *w,float dt);
void b16_combat_mode(B16Combat *c,int direction);
/* World-space ray/sphere hit (not original 2010 weapon code). */
int b16_ray_sphere(const float origin[3],const float direction[3],const float sphere[3],float radius,float *distance);
int b16_combat_fire(B16Combat *c,B14World *w,const float muzzle[3]);
void b16_model_palm(const IM2Model *m,const B14World *w,unsigned vertex,float point[3]);
#endif
