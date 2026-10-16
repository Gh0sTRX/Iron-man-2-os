#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../b24_gpu_g68_collision.h"
int main(int argc,char **argv){
 assert(argc==2);
 B24C1OriginalCollision c={0};
 assert(b24_g70_g68_collision_load(&c,argv[1]));
 assert(c.count==1910);
 unsigned checked=0;
 for(unsigned i=0;i<c.count;i++){
  const B24C1OriginalCollisionFace *f=&c.faces[i];
  if(f->wall)continue;
  float x=(f->xyz[0]+f->xyz[3]+f->xyz[6])/3.f;
  float y=(f->xyz[1]+f->xyz[4]+f->xyz[7])/3.f;
  float z=(f->xyz[2]+f->xyz[5]+f->xyz[8])/3.f;
  float result=999999.f;
  int found=b24_g74_near_original_floor(&c,x,y,z,&result);
  if(found){
   assert(isfinite(result));
   assert(result>=z-.5001f&&result<=z+.4501f);
   checked++;
   /* Absolutely never snap actor's feet to unrelated tall roof. */
   float distant=0;
   assert(!b24_g74_near_original_floor(&c,x,y,z+3000.f,&distant));
  }
 }
 assert(checked>10u);
 float out=500.f;
 assert(!b24_g74_near_original_floor(&c,10000.f,10000.f,0.f,&out));
 assert(out==500.f);
 b24_c1_original_collision_free(&c);
 printf("PASS G74 %u genuine authored nearby floor triangle probes with exact barycentric 0.5m bounds, no far roof teleport\n",checked);
 return 0;
}
