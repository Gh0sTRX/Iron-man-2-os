#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static unsigned dirs(const B24C1OriginalCollision *city,float x,float y,float z) {
 static const float d[8][2]={{1,0},{-1,0},{0,1},{0,-1},
 {0.70710678f,0.70710678f},{-0.70710678f,0.70710678f},
 {0.70710678f,-0.70710678f},{-0.70710678f,-0.70710678f}};
 unsigned count=0;
 for(unsigned i=0;i<8;i++){
  float xx=x+d[i][0]*.08f,yy=y+d[i][1]*.08f,zz=z;
  assert(b24_g75_capsule_reconcile(city,x,y,z,xx,yy,z,1,.35f,2.24f,&xx,&yy,&zz));
  const int ok=hypotf(xx-x,yy-y)>.001f;
  count+=(unsigned)ok;
  printf("WALK_EXIT original_C1L1 start=(%.4f,%.4f,%.4f) dir=%u accept=%d resolved=(%.4f,%.4f,%.4f)\n",x,y,z,i,ok,xx,yy,zz);
 }
 return count;
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision c={0};
 assert(b24_g70_g68_collision_load(&c,argv[1])&&c.ready&&c.count==1910u&&c.wall_count==1690u);
 unsigned a=dirs(&c,0,0,0);
 unsigned b=dirs(&c,0,.9802f,.0725f);
 unsigned d=dirs(&c,-1.319f,-6.747f,.0725f);
 unsigned e=dirs(&c,-1.319f,-6.747f,2.82955f);
 printf("WALK_EXIT SUMMARY actual_2010_G66C: default=%u/8 first_wall_contact=%u/8 MC_low=%u/8 MC_mid=%u/8\n",a,b,d,e);
 assert(a==8u);
 assert(d==0u);
 assert(e==8u);
 b24_c1_original_collision_free(&c);
 return 0;
}
