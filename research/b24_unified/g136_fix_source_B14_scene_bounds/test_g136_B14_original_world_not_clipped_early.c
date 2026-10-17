#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "b14_world.h"
int main(void){
 B14World w={0};
 b14_world_init(&w);
 /* Real 2010 original Stark Expo G66 scene extends x to +649.194
  * and y to +586.695; old beta B14 silently cut x at 330 y at 254
  * even if G75 genuine city collider cleared the candidate. */
 w.x=500.f;w.y=500.f;
 b14_world_tick(&w,.016f,0.f,0.f,0.f,0.f,0.f);
 assert(w.x>490.f&&w.x<510.f);
 assert(w.y>490.f&&w.y<510.f);
 /* Outside source mesh must fail closed and clamp inside the measured
  * scene; authored original mission volume not inferred by this test. */
 w.x=2000.f;w.y=2000.f;
 b14_world_tick(&w,.016f,0.f,0.f,0.f,0.f,0.f);
 assert(w.x>648.f&&w.x<650.f);
 assert(w.y>585.f&&w.y<588.f);
 w.x=-2000.f;w.y=-2000.f;
 b14_world_tick(&w,.016f,0.f,0.f,0.f,0.f,0.f);
 assert(w.x>-762.f&&w.x<-759.f);
 assert(w.y>-774.f&&w.y<-771.f);
 puts("G136B PASS one original 2010 G66M full world B14 physics movement x500/y500 no longer silently clipped to old 330/254, exact scene measured bounds; no VPK");
 return 0;
}
