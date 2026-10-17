#include "b24_g108_visible_original_wall_grid.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"usage: G108 <real native G66M source> <real G66C source>\\n");return 2;}
 B24C1OriginalCollision native={0};
 B24G108Grid g={0};
 assert(b24_g70_g68_collision_load(&native,argv[2]));
 assert(native.count==1910u&&native.wall_count==1690u);
 assert(b24_g108_grid_load(&g,argv[1],&native));
 assert(g.ready&&g.count>1000&&g.count<18001);
 assert(g.cell_index_count>=g.count);
 /* G128 regression: original 2010 level1 SOURCE world is much wider than
  * the arbitrary old central -336..336/-360..264 collision grid. Verify
  * the rebuilt grid covers the full measured original G66 rendered scene.
  * The source rectangle does NOT certify gameplay mission flight rights. */
 assert(g.source_maxx>g.source_minx&&g.source_maxy>g.source_miny);
 assert(g.source_minx>=-2048.f&&g.source_maxx<=1024.f);
 assert(g.source_miny>=-2048.f&&g.source_maxy<=1024.f);
 assert(b24_g108_grid_source_bounds_allow(&g,
     .5f*(g.source_minx+g.source_maxx),
     .5f*(g.source_miny+g.source_maxy),.35f));
 assert(!b24_g108_grid_source_bounds_allow(&g,g.source_minx-.5f,
     .5f*(g.source_miny+g.source_maxy),.35f));
 unsigned outside_previous_beta_viewport=0;
 for(uint32_t i=0;i<g.count;i++){
  const B24G108Wall *w=&g.walls[i];
  const float xx=(w->p[0]+w->p[3]+w->p[6])/3.f;
  const float yy=(w->p[1]+w->p[4]+w->p[7])/3.f;
  if(xx< -336.f||xx>336.f||yy< -360.f||yy>264.f)
    outside_previous_beta_viewport++;
 }
 printf("G128 ORIGINAL 2010 source city measured AABB x:[%.3f,%.3f] y:[%.3f,%.3f], %u original opaque steep triangles previously LOST beyond hardcoded B14/G108 beta viewport\\n",
   g.source_minx,g.source_maxx,g.source_miny,g.source_maxy,
   outside_previous_beta_viewport);
 uint32_t hits=0,clear=0;
 /* Probe source-REAL triangle interiors, not invented stress vertices. */
 for(uint32_t i=0;i<g.count;i++){
  const B24G108Wall *w=&g.walls[i];
  const float x=(w->p[0]+w->p[3]+w->p[6])/3.f;
  const float y=(w->p[1]+w->p[4]+w->p[7])/3.f;
  const float z=(w->p[2]+w->p[5]+w->p[8])/3.f;
  if(!b24_g108_grid_clear(&g,x,y,z-1.f,.35f,2.24f))hits++;
  else clear++;
 }
 assert(hits>g.count/5);
 assert(b24_g108_grid_clear(&g,10000.f,10000.f,0.f,.35f,2.24f));
 assert(!b24_g108_grid_clear(&g,NAN,0.f,0.f,.35f,2.24f));
 float x=0,y=0,z=0;
 assert(b24_g108_grid_probe(&g,&x,&y,&z));
 assert(isfinite(x)&&isfinite(y)&&isfinite(z));
 /* Original G68/G75 dynamic source FPS: 5000 swept-local wall queries are
  * capped to tiny per-cell candidate lists, not every authored 22k face.
  * No assertion on hardware FPS from CPU-host elapsed time. */
 volatile unsigned checksum=0;
 const clock_t start=clock();
 for(unsigned i=0;i<5000;i++){
  const float dx=x+(float)(i%47u)*.08f;
  const float dy=y+(float)((i*17u)%53u)*.09f;
  checksum+=b24_g108_grid_clear(&g,dx,dy,z,.35f,2.24f)!=0;
 }
 const double elapsed=(double)(clock()-start)/CLOCKS_PER_SEC;
 printf("PASS G108 ORIGINAL 2010 22441 visual triangles + 1910 native sourced colliders: %u supplemental opaque steep candidate triangles; %u own-source interiors blocking, %u clear, %u grid index refs; 5000 source grid queries CPU %.3f sec, checksum %u. ZERO VPK / NO fake original iOS material permission.\\n",
 g.count,hits,clear,g.cell_index_count,elapsed,checksum);
 b24_g108_grid_close(&g);
 b24_c1_original_collision_free(&native);
 assert(!g.ready&&!g.walls);
 return 0;
}
