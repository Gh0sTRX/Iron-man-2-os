#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

/* Actual ORIGINAL 2010 real G104 G66C source vs actual original city G66M
 * material-correct G158 road-source XY height, not mocked game surface.
 * G75 gameplay function is the same compiled native floor query used by
 * the single B14 owner in the existing G153-G156 Vita game.
 *
 * This test deliberately DOES NOT add the road surface as collision.
 * It proves whether the CURRENT port G75 original 1,910 source-only
 * floor evaluator can support a player foot at the rendered road Z.
 */
int main(int argc,char **argv){
 if(argc!=3){
  fprintf(stderr,"Usage: G158_true_G75_floor <original real G66C> <G158 original source XY fixture>\n");
  return 2;
 }
 FILE *f=fopen(argv[2],"r");
 if(!f)return 2;
 float x=0.f,y=0.f,road_source_z=0.f,native_source_z=0.f;
 const int n=fscanf(f,"%f %f %f %f",&x,&y,&road_source_z,&native_source_z);
 fclose(f);
 if(n!=4||!isfinite(x)||!isfinite(y)||!isfinite(road_source_z)||
    !isfinite(native_source_z))return 2;
 assert(road_source_z-native_source_z>2.f);
 B24C1OriginalCollision world={0};
 assert(b24_g70_g68_collision_load(&world,argv[1]));
 assert(world.ready&&world.count==1910u&&world.wall_count==1690u);

 float support=0.f;
 const int can_walk_at_visible_road_height=
      b24_g74_near_original_floor(&world,x,y,road_source_z,&support);
 /* This is the original B14/G75 port: original drawn road is not a
  * floor at the same height, NOT a claim that original iOS game is
  * internally broken or requires arbitrary new triangle colliders. */
 assert(!can_walk_at_visible_road_height);

 const int base_support=
      b24_g74_near_original_floor(&world,x,y,native_source_z,&support);
 assert(base_support&&fabsf(support-native_source_z)<.03f);
 printf("G158 ORIGINAL 2010 source road at XY=(%.2f,%.2f), rendered road Z=%.4f, "
        "current native G75 support only Z=%.4f, height delta=%.4f\n",
        x,y,road_source_z,support,road_source_z-support);
 puts("G158 VERIFIED current ONE B14/G75 Vita gameplay C source cannot mark actual 2010 road surface as grounded at source rendered height. AUTHORED COLLISION SOLIDITY / WORLD PARENT TRANSFORM STILL UNPROVEN. NO VPK.");
 b24_c1_original_collision_free(&world);
 return 0;
}
