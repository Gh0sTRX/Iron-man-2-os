#include "b24_weapon_aim.h"
#include <math.h>
#include <stddef.h>
static B24V3 add(B24V3 a,B24V3 b){return (B24V3){a.x+b.x,a.y+b.y,a.z+b.z};}
static B24V3 mul(B24V3 a,float s){return (B24V3){a.x*s,a.y*s,a.z*s};}
static B24V3 sub(B24V3 a,B24V3 b){return (B24V3){a.x-b.x,a.y-b.y,a.z-b.z};}
static float dot(B24V3 a,B24V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static int norm(B24V3 v,B24V3 *dest){
    float n=dot(v,v);
    if(!isfinite(n)||n<1.e-9f)return 0;
    *dest=mul(v,1.f/sqrtf(n));return 1;
}
static int valid(B24V3 a){
    return isfinite(a.x)&&isfinite(a.y)&&isfinite(a.z)&&
        fabsf(a.x)<100000.f&&fabsf(a.y)<100000.f&&fabsf(a.z)<100000.f;
}
static B24V3 transform(B24PoseFrame f,B24V3 local){
    return add(f.origin,
        add(add(mul(f.axis_x,local.x),mul(f.axis_y,local.y)),mul(f.axis_z,local.z)));
}
B24ShotRay b24_weapon_aim_ray(const B24PoseFrame *p,
    const B24Socket *right,const B24Socket *chest,
    B24Weapon weapon,const B24V3 *target){
    B24ShotRay out={0};
    if(!p||!valid(p->origin)||!valid(p->world_forward)||
       !valid(p->axis_x)||!valid(p->axis_y)||!valid(p->axis_z))return out;
    const B24Socket *origin=NULL;
    if(weapon==B24_ATTACK_REPULSOR)origin=right;
    else if(weapon==B24_ATTACK_UNIBEAM)origin=chest;
    else return out; /* not a license to fire arbitrary missiles from a palm */
    if(!origin||!origin->rig_verified||!valid(origin->local_xyz))return out;
    B24V3 fwd;
    if(!norm(p->world_forward,&fwd))return out;
    out.origin=transform(*p,origin->local_xyz);
    if(!valid(out.origin))return (B24ShotRay){0};
    out.direction=fwd;
    if(target&&valid(*target)){
        B24V3 intended;
        if(norm(sub(*target,out.origin),&intended)&&dot(intended,fwd)>0.10f)
            out.direction=intended;
        /* Never fire backwards merely because free-look camera swung around */
    }
    out.valid=1;
    return out;
}
void b24_weapon_aim_step(B24AimState *s,B24Weapon weapon,
                         int held,int walking,float dt){
    if(!s)return;
    if(!isfinite(dt)||dt<0.f)dt=0.f;
    if(dt>.05f)dt=.05f;
    s->shot_pulse=0;
    if(s->last_weapon!=weapon){
        s->attack_timer=0.f;
        s->last_weapon=weapon;
    }
    /* Arm overlay weight is independent of walk/run/hover lower-body gait.
       A genuine upper-body skin-weight mask + original right-arm clip MUST
       consume this value; it is NOT already a displayed Vita animation. */
    float goal=weapon==B24_ATTACK_REPULSOR&&held?1.f:0.f;
    float change=dt*7.f;
    if(s->right_arm_aim_weight<goal)
        s->right_arm_aim_weight=fminf(goal,s->right_arm_aim_weight+change);
    else
        s->right_arm_aim_weight=fmaxf(goal,s->right_arm_aim_weight-change);
    (void)walking; /* preserve locomotion in independent animation channel */
    if(!held||weapon==B24_ATTACK_NONE||weapon==B24_ATTACK_MISSILE){
        s->attack_timer=0.f;return;
    }
    const float cooldown=weapon==B24_ATTACK_REPULSOR?.28f:1.1f;
    const float raise=weapon==B24_ATTACK_REPULSOR?.12f:.1f;
    s->attack_timer+=dt;
    if(s->attack_timer>=raise){
        s->shot_pulse=1;
        s->attack_timer=raise-cooldown;
    }
}
