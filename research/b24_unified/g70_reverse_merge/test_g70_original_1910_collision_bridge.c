#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include "../b24_gpu_g68_collision.h"
int main(int argc,char **argv){
 assert(argc==2);
 B24C1OriginalCollision col={0};
 assert(b24_g70_g68_collision_load(&col,argv[1]));
 assert(col.ready&&col.count==1910u&&col.wall_count>100u);
 float x=-52.3f+0.05f,y=-264.6f;
 assert(b24_c1_original_collision_resolve(&col,
    -52.3f,-264.6f,.0725f,.0725f,.35f,&x,&y));
 assert(isfinite(x)&&isfinite(y));
 b24_c1_original_collision_free(&col);
 puts("PASS G70 reused original G9 CPU wall solver on exact G68 1910 native source triangles; user-device gameplay yet untested");
 return 0;
}
