#ifndef B24_WEAPON_AIM_H
#define B24_WEAPON_AIM_H
/* Z-up B17-compatible, frame-of-pose source of truth (not guessed camera orbit).
 * This module does NOT synthesize the original 2010 .anim keyframes.
 * Runtime must supply real original skeletal socket transforms.
 */
typedef struct {float x,y,z;} B24V3;
typedef struct {
    B24V3 origin,axis_x,axis_y,axis_z; /* model-local => B17 Z-up WORLD */
    B24V3 world_forward;              /* genuine skinned torso aim/facing */
} B24PoseFrame;
typedef struct {B24V3 local_xyz;int rig_verified;} B24Socket;
typedef struct {B24V3 origin,direction;int valid;} B24ShotRay;
typedef enum {B24_ATTACK_NONE=0,B24_ATTACK_REPULSOR=1,
              B24_ATTACK_UNIBEAM=2,B24_ATTACK_MISSILE=3} B24Weapon;
typedef struct {
    B24Weapon last_weapon;
    float right_arm_aim_weight;
    float attack_timer;
    int shot_pulse;
} B24AimState;
B24ShotRay b24_weapon_aim_ray(const B24PoseFrame *pose,
    const B24Socket *right_palm,const B24Socket *chest_reactor,
    B24Weapon weapon,const B24V3 *target_world);
void b24_weapon_aim_step(B24AimState *s,B24Weapon weapon,
                        int fire_held,int walking,float dt);
#endif
