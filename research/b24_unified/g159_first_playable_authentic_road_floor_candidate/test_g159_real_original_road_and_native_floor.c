#include "b24_g159_real_source_road.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(int argc,char **argv){
 if(argc!=3)return 2;
 B24G159Road road={0};
 B24C1OriginalCollision native={0};
 assert(b24_g159_road_open(&road,argv[1]));
 assert(road.ready&&road.count>1u);
 assert(!b24_g159_road_open(&road,argv[1]));
 assert(b24_g70_g68_collision_load(&native,argv[2]));
 assert(native.count==1910u&&native.wall_count==1690u);
 /* Original source-identified G66M atlas12=c1l1_road.tga,
    original G66C native nonwall: real G158 source coordinate sample. */
 const float x=-160.f,y=-160.f;
 float z=-999.f;
 assert(b24_g159_road_near(&road,x,y,2.6937f,&z));
 assert(fabsf(z-2.6937f)<.005f);
 float n=-999.f;
 assert(!b24_g74_near_original_floor(&native,x,y,2.6937f,&n));
 assert(b24_g74_near_original_floor(&native,x,y,.0725f,&n));
 assert(fabsf(n-.0725f)<.005f);
 /* Source road MUST NOT replace genuine native source support at low Z. */
 assert(!b24_g159_road_near(&road,x,y,.0725f,&z));
 /* Real original source roadway is only supported near its genuine height,
    no global height offset or world-wide fabricated flat floor. */
 assert(!b24_g159_road_near(&road,10000.f,10000.f,2.6937f,&z));
 assert(!b24_g159_road_near(&road,x,y,20.f,&z));
 assert(b24_g159_road_crossed(&road,x,y,4.f,2.2f,&z));
 assert(fabsf(z-2.6937f)<.005f);
 assert(!b24_g159_road_crossed(&road,x,y,2.5f,1.f,&z));
 assert(!b24_g159_road_crossed(&road,x,y,20.f,19.f,&z));
 assert(!b24_g159_road_near(&road,NAN,y,2.6937f,&z));
 printf("G159 original PVR road-only source: %u authentic G66M triangles, XY -160/-160 real road height %.4f; source native support %.4f; no synthetic floor, no all-world Z translation.\n",road.count,z,n);
 b24_g159_road_close(&road);
 b24_c1_original_collision_free(&native);
 assert(!road.ready&&!road.faces&&!native.ready);
 puts("G159 PASS actual 2010 source road-level opt-in native-first G75 candidate, preserved lower support, source Z-crossing and outside-no-floor. NOT native iOS confirmed solidity. NO VPK.");
 return 0;
}