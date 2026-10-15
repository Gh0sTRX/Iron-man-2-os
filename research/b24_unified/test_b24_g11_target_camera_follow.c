#include "b24_g11_target_camera_follow.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B24G11CameraFocusInput i={0,0,0,10,.016f,1.f,1,0,0,0};
 B24G11CameraFocus f={0};
 assert(b24_g11_target_camera_follow(&i,&f));
 assert(f.focusing&&f.zoom_reduction>.3f&&f.orbit<1.f);
 float prev=f.orbit;
 for(int k=0;k<120;k++){i.orbit=f.orbit;assert(b24_g11_target_camera_follow(&i,&f));}
 assert(fabsf(f.orbit)<.07f);
 i.orbit=prev;i.manual_camera_input=1;
 assert(b24_g11_target_camera_follow(&i,&f)&&f.orbit==prev);
 i.lock_held=0;i.manual_camera_input=0;
 assert(b24_g11_target_camera_follow(&i,&f)&&!f.focusing&&f.zoom_reduction==0.f);
 i.melee_active=1;i.actor_y=3.f;
 assert(b24_g11_target_camera_follow(&i,&f)&&f.focusing);
 i.world_flying=1;
 assert(b24_g11_target_camera_follow(&i,&f)&&!f.focusing);
 i.world_flying=0;i.actor_y=99.f;
 assert(b24_g11_target_camera_follow(&i,&f)&&!f.focusing);
 i.orbit=NAN;assert(!b24_g11_target_camera_follow(&i,&f));
 puts("PASS G11 camera locked practice actor smoothly in orbit with manual"
      " right-stick override, combat near zoom, no rush/flight focus,"
      " no inventing actor/weapon/HP");
 return 0;
}
