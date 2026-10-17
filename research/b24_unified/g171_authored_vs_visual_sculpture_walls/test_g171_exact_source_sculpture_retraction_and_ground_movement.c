#include "b14_world.h"
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g108_visible_original_wall_grid.h"
#include "b24_g156_exact_vertical_triangle_contact.h"
#include <math.h>
#include <stdio.h>
#include <assert.h>

/* Exact real original 2010 G66C and G66M source, never fake test walls.
 * G170 native original wall collision at boot foot XY (0,1.1) = 0,
 * inferred G108 source sculpture group21/atlas21 = 2 before correction.
 * Revoke only that unfounded collider and prove grounded B14 starts
 * moving without disabling original wall contact elsewhere. */
int main(int argc,char**argv){
 if(argc!=3)return 2;
 B24C1OriginalCollision native={0};
 B24G108Grid visual={0};
 assert(b24_g70_g68_collision_load(&native,argv[2]));
 assert(native.count==1910u&&native.wall_count==1690u);
 assert(b24_g108_grid_load(&visual,argv[1],&native));
 assert(visual.count>5000u);
 for(uint32_t k=0;k<visual.count;k++){
  assert(visual.walls[k].source_batch!=21u);
 }
 /* Native original actor near source CLARA local transform still genuinely
  * intersects the genuine authored 2010 source G66C wall ID715.
  * Correction does NOT erase its collision or fabricate scene spawn. */
 const B24C1OriginalCollisionFace *f=&native.faces[715u];
 assert(f->wall);
 assert(b24_g156_exact_vertical_triangle_contact(f->xyz,
    -1.319f,-6.747f,.0725f,.35f,2.24f));
 assert(b24_g108_grid_clear(&visual,0.f,1.10f,.0725f,.35f,2.24f));

 B14World world={0};
 b14_world_init(&world);
 unsigned accepted=0;
 for(int k=0;k<120;k++){
  float oldx=world.x,oldy=world.y,oldz=world.z;
  b14_world_tick(&world,1.f/60.f,0.f,1.f,0.f,0.f,0.f);
  float x=world.x,y=world.y,z=world.z;
  assert(b24_g75_capsule_reconcile(&native,oldx,oldy,oldz,
     x,y,z,!world.flying,.35f,2.24f,&x,&y,&z));
  world.x=x;world.y=y;world.z=z;
  if(y>oldy+.001f)accepted++;
 }
 printf("G171 2010 source original strict authored sculpture candidate revoked, G66C authored wall count=%u, remaining non-sculpture visual candidate count=%u, actor first 120 grounded input accepted=%u frames moved to XY=(%.4f,%.4f) original 2010 floorZ=%.4f\n",
    native.count,visual.count,accepted,world.x,world.y,world.z);
 assert(world.y>1.12f&&accepted>15u);
 assert(fabsf(world.z-.0725f)<.5f);
 b24_g108_grid_close(&visual);
 b24_c1_original_collision_free(&native);
 puts("G171 source C11 pass: no invented sculpture wall, actual authored G66C unchanged, grounded B14 now passes former blocked visible decor while source world kept. Native original level1 spawn/solidness still unproven. NO VPK.");
 return 0;
}
