#include "b24_gpu_g68_collision.h"
#include "b24_g108_visible_original_wall_grid.h"
#include "b24_g156_exact_vertical_triangle_contact.h"
#include <assert.h>
#include <stdio.h>
#include <math.h>
/* Original G161 B14 starts x=0,y=0,z=0. G167 120-frame ground
 * accepted only up to y≈0.98. Determine which EXACT 2010 G66C wall
 * vs 2010 G66M derived OPAQUE visual candidate prevents x/y movement,
 * without disabling an authentic collider or relocating actor randomly.
 * No invented source first mission spawn or new VPK.
 */
static void audit(const B24C1OriginalCollision *w,const B24G108Grid *g,
                  float x,float y,float foot){
 int native=0,visual=0,shown=0;
 float source_native_floor=-99.f;
 int near=b24_g74_near_original_floor(w,x,y,foot,&source_native_floor);
 for(uint32_t i=0;i<w->count;i++){
  const B24C1OriginalCollisionFace *f=&w->faces[i];
  if(!f->wall||f->maxz<foot||f->minz>foot+2.24f||
     x<f->minx-.35f||x>f->maxx+.35f||
     y<f->miny-.35f||y>f->maxy+.35f)continue;
  if(!b24_g156_exact_vertical_triangle_contact(
      f->xyz,x,y,foot,.35f,2.24f))continue;
  native++;
  if(shown++<4)
   printf("G170 AUTHORED G66C native wall collision id=%u source_xyz_a=(%.4f,%.4f,%.4f) zspan=(%.4f..%.4f), xspan=(%.4f..%.4f) yspan=(%.4f..%.4f)\n",
     i,f->xyz[0],f->xyz[1],f->xyz[2],
     f->minz,f->maxz,f->minx,f->maxx,f->miny,f->maxy);
 }
 shown=0;
 for(uint32_t i=0;i<g->count;i++){
  const B24G108Wall *f=&g->walls[i];
  if(f->maxz<foot||f->minz>foot+2.24f||
     x<f->minx-.35f||x>f->maxx+.35f||
     y<f->miny-.35f||y>f->maxy+.35f)continue;
  if(!b24_g156_exact_vertical_triangle_contact(
      f->p,x,y,foot,.35f,2.24f))continue;
  visual++;
  if(shown++<4)
   printf("G170 VISIBLE G66M supplemental CANDIDATE id=%u source_draw_batch=%u xyz_a=(%.4f,%.4f,%.4f), zspan=(%.4f..%.4f)\n",
     i,f->source_batch,f->p[0],f->p[1],f->p[2],
     f->minz,f->maxz);
 }
 printf("G170 VERIFIED 2010 source XY=(%.4f,%.4f) feetZ=%.4f original native grounded floor=%d support=%.4f, native wall contacts=%d, visible-opaque INFERRED wall candidate contacts=%d\n",
   x,y,foot,near,source_native_floor,native,visual);
}
int main(int argc,char**argv){
 if(argc!=3)return 2;
 B24C1OriginalCollision w={0};B24G108Grid g={0};
 assert(b24_g70_g68_collision_load(&w,argv[2]));
 assert(w.count==1910u&&w.wall_count==1690u);
 assert(b24_g108_grid_load(&g,argv[1],&w));
 assert(g.count>=7000u);
 audit(&w,&g,0.f,0.f,.0725f);
 audit(&w,&g,0.f,.8845f,.0725f);
 audit(&w,&g,0.f,.9802f,.0725f);
 audit(&w,&g,0.f,1.1f,.0725f);
 audit(&w,&g,-1.319f,-6.747f,.0725f);
 audit(&w,&g,-160.f,-160.f,2.6937f);
 b24_g108_grid_close(&g);
 b24_c1_original_collision_free(&w);
 puts("G170 authentic G66C WALL and source-visible G66M candidate classification (NOT native solidity proof). Does not change B14/G75 physics or original 2010 startup. NO VPK.");
 return 0;
}
