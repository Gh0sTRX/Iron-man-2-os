#include "b24_weapon_aim.h"
#include <math.h>
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
static float dot(B24V3 a,B24V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
int main(void){
 B24PoseFrame p={{5.f,6.f,2.f},{1,0,0},{0,1,0},{0,0,1},{0,1,0}};
 B24Socket right={{.7f,.3f,1.2f},1},chest={{0,.2f,1.4f},1};
 B24V3 target={5.f,18.f,3.4f},frontcamera={5.f,-100.f,3.f};
 B24ShotRay r=b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_REPULSOR,&target);
 assert(r.valid && fabsf(r.origin.x-5.7f)<1.e-5f);
 assert(r.direction.y>.98f && dot(r.direction,p.world_forward)>.98f);
 B24ShotRay u=b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_UNIBEAM,&target);
 assert(u.valid && fabsf(u.origin.x-5.f)<1.e-5f);
 assert(fabsf(u.origin.z-3.4f)<1.e-5f && u.direction.y>.98f);
 /* Camera looking at actor from front must NOT reverse chest shot. */
 B24ShotRay backwards=b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_UNIBEAM,&frontcamera);
 assert(backwards.valid && dot(backwards.direction,p.world_forward)>.98f);
 /* Right/left hand MUST NOT alternate or inherit Unibeam emitter. */
 right.rig_verified=0;
 assert(!b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_REPULSOR,&target).valid);
 assert(b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_UNIBEAM,&target).valid);
 right.rig_verified=1;
 /* When body turns 180deg, both muzzle and actor facing rotate together. */
 p.axis_x=(B24V3){-1,0,0};p.axis_y=(B24V3){0,-1,0};
 p.world_forward=(B24V3){0,-1,0};
 r=b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_REPULSOR,NULL);
 assert(r.valid && r.origin.x<5.f && r.direction.y<-.99f);
 u=b24_weapon_aim_ray(&p,&right,&chest,B24_ATTACK_UNIBEAM,NULL);
 assert(u.valid && u.direction.y<-.99f);
 B24AimState s={0};
 int pulses=0;
 for(int k=0;k<120;k++){
     b24_weapon_aim_step(&s,B24_ATTACK_REPULSOR,1,1,1.f/60.f);
     assert(s.right_arm_aim_weight>=0 && s.right_arm_aim_weight<=1.f);
     pulses+=s.shot_pulse;
 }
 assert(s.right_arm_aim_weight>.99f && pulses>=5);
 b24_weapon_aim_step(&s,B24_ATTACK_UNIBEAM,0,0,1.f/60.f);
 assert(s.shot_pulse==0);
 for(int i=0;i<60;i++)b24_weapon_aim_step(&s,B24_ATTACK_UNIBEAM,1,0,1.f/60.f);
 assert(s.right_arm_aim_weight<.01f); /* no repulsor arm layer on chest beam */
 uint32_t rand=0x24c1u;
 for(int i=0;i<20000;i++){
   rand=rand*1664525u+1013904223u;
   int mode=(int)(rand&3u),fire=(rand>>8)&1u;
   float dt=(rand>>12)&1u?1.f/60.f:.033f;
   b24_weapon_aim_step(&s,(B24Weapon)mode,fire,rand&16u,dt);
   assert(isfinite(s.right_arm_aim_weight)&&isfinite(s.attack_timer));
   assert(s.right_arm_aim_weight>=0&&s.right_arm_aim_weight<=1);
 }
 puts("PASS B24 Z-up weapon attachment: RIGHT PALM, CHEST Unibeam, camera-front anti-backwards, independent walk overlay, 20k host fuzz");
}
