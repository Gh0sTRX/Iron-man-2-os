#include "b24_g75_source_capsule.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
int main(void){
 B24C1OriginalCollision world={0};
 world.ready=1;
 float x=-10.f,y=0.f,z=0.f;
 /* NO scene geometry: the old G75 code would accept 100 units in 80
  * one-unit-plus leaps, breaking the intended <= 22cm source samples.
  * G134 must NOT allow a single-frame teleport or second world tick. */
 assert(b24_g75_capsule_reconcile(&world,0,0,0,100,0,0,
   0,.35f,2.24f,&x,&y,&z));
 assert(x>=17.5f&&x<=17.61f&&fabsf(y)<.01f&&fabsf(z)<.01f);
 B24C1OriginalCollisionFace wall={0};
 /* Thin original-format collider triangle at x=10.6 source units;
  * Y range [-50,+50], Z[-2,10], normal faces +/-X. */
 float p[9]={10.6f,-50.f,-2.f,10.6f,50.f,-2.f,10.6f,0.f,10.f};
 memcpy(wall.xyz,p,sizeof(p));
 wall.minx=wall.maxx=10.6f;
 wall.miny=-50.f;wall.maxy=50.f;
 wall.minz=-2.f;wall.maxz=10.f;
 wall.wall=1;
 world.faces=&wall;world.count=1;world.wall_count=1;
 assert(b24_g75_capsule_reconcile(&world,0,0,0,100,0,0,
   0,.35f,2.24f,&x,&y,&z));
 /* Old 80 leap heuristic would visit x=10 and 11.25, miss wall at
  * x=10.6, and eventually place character on the wrong side. */
 assert(x<10.6f-.35f+.04f);
 assert(x>=0.f);
 printf("G134 PASS true thin-wall capsule x=10.6 blocked original-format 2010 wall at x=%.4f instead of 100.0; no collision tunneling, no fake scene flags, no VPK.\n",x);
 return 0;
}
