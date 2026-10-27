/* G248: REAL reconstructed Vita gameplay SOURCE, host replay, NO VPK.
 * The same assembled B14 tick + C1L1 authored G66C triangles +
 * G159 genuine source-road candidate + G160 spatial index + G171 collider.
 * Test 8 inputs, 3 distinct source-level boot/location hypotheses,
 * ground AND flight, 120 frames with exact one simulation and collision
 * per frame. This is NOT a physical Vita test or original 2010 touch rules.
 */
#include "b14_world.h"
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g156_exact_vertical_triangle_contact.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

typedef struct {float x,y,z;const char *tag;} G248Point;
typedef struct {
 unsigned proposals,accepts,rejects;
 double proposed_path,accepted_path;
 float fx,fy,fz;
} G248Result;

static int finite3(float a,float b,float c){
 return isfinite(a)&&isfinite(b)&&isfinite(c);
}
static G248Result replay(const B24C1OriginalCollision *original,
                        G248Point p, int flying, float left_x,float left_y){
 B14World w;
 b14_world_init(&w);
 w.x=p.x;w.y=p.y;w.z=p.z;
 w.target_z=p.z;w.cam_x=p.x;w.cam_y=p.y;w.cam_z=p.z+w.head_height;
 w.flying=flying;
 if(flying)w.flight_stage=2;
 G248Result s={0};
 for(unsigned frame=0;frame<120;frame++){
  const float ox=w.x,oy=w.y,oz=w.z;
  b14_world_tick(&w,1.f/60.f,left_x,left_y,0.f,0.f,0.f);
  assert(finite3(w.x,w.y,w.z));
  const float proposed=hypotf(w.x-ox,w.y-oy);
  float ax=w.x,ay=w.y,az=w.z;
  assert(b24_g75_capsule_reconcile(original,ox,oy,oz,
      w.x,w.y,w.z,!w.flying,.35f,2.24f,&ax,&ay,&az));
  assert(finite3(ax,ay,az));
  const float accepted=hypotf(ax-ox,ay-oy);
  if(proposed>.0001f)s.proposals++;
  if(accepted>.0001f)s.accepts++;
  if(proposed>.0001f && accepted<.0001f)s.rejects++;
  s.proposed_path+=proposed;s.accepted_path+=accepted;
  w.x=ax;w.y=ay;w.z=az;
#ifdef B14_WORLD_HEIGHT_SUPPORT
  /* Match current main's post-reconciliation support acknowledgment. */
  float support=0.f;
  const int supported=!w.flying&&b24_g75_support_at(original,w.x,w.y,w.z,&support);
  b14_world_accept_ground_support(&w,supported,support);
#endif
 }
 s.fx=w.x;s.fy=w.y;s.fz=w.z;
 printf("G248 ORIGINAL-C1L1 B14+G75+G159+G171 source replay %s %s stick=(%.3f,%.3f) B14_proposed=%u G75_accepted=%u G75_rejected=%u path_B14=%.4f path_resolved=%.4f start=(%.3f,%.3f,%.3f) end=(%.3f,%.3f,%.3f)\n",
     p.tag,flying?"FLIGHT":"GROUND",left_x,left_y,
     s.proposals,s.accepts,s.rejects,s.proposed_path,s.accepted_path,
     p.x,p.y,p.z,w.x,w.y,w.z);
 return s;
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision city={0};
 assert(b24_g70_g68_collision_load(&city,argv[1]));
 assert(city.ready&&city.count==1910u&&city.wall_count==1690u);
 /* Keep the authored source wall: exact G171 native triangle, no deletion. */
 assert(city.faces[715u].wall);
 assert(b24_g156_exact_vertical_triangle_contact(city.faces[715u].xyz,
     -1.319f,-6.747f,.0725f,.35f,2.24f));
 puts("G249 ORIGINAL G66C wall face715 intersects MC local XY at low ground; actual mission spawn UNKNOWN");
 const G248Point positions[]={
  {0.f,0.f,0.f,"B14_HOME_SOURCE_BOOT_NOT_ORIGINAL_MISSION_SPAWN"},
  {-160.f,-160.f,2.6937f,"ORIGINAL_G66M_ROAD_SOURCE_TEST"},
  {-1.319f,-6.747f,.0725f,"MC_ORIGINAL_LOW_G66C_SUPPORT_NOT_RUNTIME_SPAWN"},
  {-1.319f,-6.747f,2.82955f,"MC_ORIGINAL_MID_G66C_SUPPORT_NOT_RUNTIME_SPAWN"},
  {-1.319f,-6.747f,6.673064f,"MC_ORIGINAL_HIGH_G66C_SUPPORT_NOT_RUNTIME_SPAWN"},
  {-1.319f,-6.747f,25.054f,"MC_AUTHORED_TRANSFORM_Z_NOT_RUNTIME_SPAWN"}
 };
 const float dir[8][2]={
  {0.f,1.f},{0.f,-1.f},{1.f,0.f},{-1.f,0.f},
  {.70710678f,.70710678f},{-.70710678f,.70710678f},
  {.70710678f,-.70710678f},{-.70710678f,-.70710678f}};
 unsigned total=0,moving_ground=0,moving_flight=0,reject_ground=0;
 for(size_t place=0;place<sizeof(positions)/sizeof(positions[0]);place++){
  for(size_t i=0;i<8;i++){
   for(int flying=0;flying<=1;flying++){
    const G248Result a=replay(&city,positions[place],flying,dir[i][0],dir[i][1]);
    assert(a.proposals<=120 && a.accepts<=120 && a.rejects<=120);
    assert(isfinite(a.proposed_path)&&isfinite(a.accepted_path));
    if(!flying){
     moving_ground+=a.accepts>0u;
     reject_ground+=a.rejects>0u;
    }else moving_flight+=a.accepts>0u;
    total++;
   }
  }
 }
 assert(total==96u);
 /* Our already source-verified first safe B14 boot move +Y MUST still
  * translate; a regression here is real and test MUST stop release. */
 const G248Result forward=replay(&city,positions[0],0,0.f,1.f);
 assert(forward.accepts>15u&&forward.fy>1.12f);
 printf("G249 EXTENDED ORIGINAL-SOURCE real_geometry=1910 wall715_MC_low_intersection=YES positive_ground_directions=%u/48 positive_flight_directions=%u/48 nonzero_ground_collision_rejections=%u/48; physical_Vita_test=NO; actual_2010_touch_ground_speed=UNKNOWN; NO_VPK\n",moving_ground,moving_flight,reject_ground);
 assert(moving_ground>=1u && moving_flight>=1u);
 b24_c1_original_collision_free(&city);
 return 0;
}
