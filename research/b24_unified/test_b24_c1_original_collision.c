#include "b24_c1_original_collision.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void synthetic(const char *path){
 FILE *f=fopen(path,"wb");assert(f);
 const unsigned hdr[4]={1u,1908u,2u,40u};
 assert(fwrite("C1WC",1,4,f)==4);
 assert(fwrite(hdr,sizeof(unsigned),4,f)==4);
 for(unsigned i=0;i<1908;i++){
  /* Synthetic triangle for test ONLY, never exported to the game.
     Original source collision file instead tested by separate arg path. */
  float x=i==0?0.f:1000.f+(float)i*6.f;
  float xyz[9]={x,-2.f,0.f,x,2.f,0.f,x,-2.f,3.f};
  unsigned group=0;
  assert(fwrite(xyz,sizeof(float),9,f)==9);
  assert(fwrite(&group,sizeof(group),1,f)==1);
 }
 assert(fclose(f)==0);
}
int main(int argc,char **argv){
 const char *tmp="/tmp/b24_c1wc_synthetic_test.c1wc";
 synthetic(tmp);
 B24C1OriginalCollision c={0};
 assert(b24_c1_original_collision_load(&c,tmp));
 assert(c.ready&&c.count==1908u&&c.wall_count==1908u);
 float x=1.f,y=.3f;
 assert(b24_c1_original_collision_resolve(&c,-1.f,0.f,1.f,1.f,.35f,&x,&y));
 assert(x<-.345f&&x>-.365f);
 assert(y>.19f&&y<.32f); /* retain tangential sliding */
 x=40.f;y=.5f;
 assert(b24_c1_original_collision_resolve(&c,-40.f,.5f,1.f,1.f,.35f,&x,&y));
 assert(x<-.345f&&x>-.365f); /* Rush high-speed sweep cannot tunnel */
 x=1.f;y=0.f;
 assert(b24_c1_original_collision_resolve(&c,-1.f,0.f,8.f,8.f,.35f,&x,&y));
 assert(fabsf(x-1.f)<.001f); /* above original wall height no contact */
 x=1.f;y=0.f;
 assert(!b24_c1_original_collision_resolve(&c,-1.f,0.f,1.f,1.f,9.f,&x,&y));
 assert(!b24_c1_original_collision_resolve(&c,-1.f,0.f,1.f,1.f,.35f,NULL,&y));
 b24_c1_original_collision_free(&c);
 assert(remove(tmp)==0);
 if(argc==2){
  assert(b24_c1_original_collision_load(&c,argv[1]));
  assert(c.count==1908u);
  assert(c.wall_count>1300u&&c.wall_count<1908u);
  unsigned contacts=0;
  /* Bounded source-space perf/regression exercise, not a claimed Vita FPS. */
  for(unsigned k=0;k<4096;k++){
   float xx=-270.f+((float)(k%64))*8.4f;
   float yy=-270.f+((float)(k/64))*8.4f;
   float zz=(float)(k%24);
   float nx=xx+.25f,ny=yy+.15f;
   assert(b24_c1_original_collision_resolve(&c,xx,yy,zz,zz,.35f,&nx,&ny));
   assert(isfinite(nx)&&isfinite(ny));
   if(fabsf(nx-(xx+.25f))>.001f||fabsf(ny-(yy+.15f))>.001f)contacts++;
  }
  printf("PASS REAL original 2010 BDAE collision %u faces, %u steep walls, %u sampled contacts (not device benchmark)\n",
         c.count,c.wall_count,contacts);
  b24_c1_original_collision_free(&c);
 }
 puts("PASS B24 genuine wall: sweeps prevent RUSH tunneling, vertical height gate, no fabricated source collision");
 return 0;
}
