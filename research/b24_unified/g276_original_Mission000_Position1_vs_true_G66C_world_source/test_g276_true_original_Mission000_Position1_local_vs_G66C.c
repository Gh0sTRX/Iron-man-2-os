/* G276 genuine original 2010 scene movement-goal candidate vs real
 * G66C 1910 collision authored triangles. Local coordinates as *hypothesis*,
 * NOT the original iOS boot player root/world XYZ. Source-only C11.
 * Does not modify Vita ground, camera, input, collision or shader.
 */
#include "b24_g275_original_2010_scripted_movement_goal_source.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g75_source_capsule.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef struct {
 unsigned tested,proposed,accepted,rejected,has_floor;
 float nearest_floor;
} G276Probe;
static G276Probe analyze(const B24C1OriginalCollision *city,
                         const float point[3],int grounded) {
 G276Probe result={0};
 const float dir[8][2]={
  {1,0},{-1,0},{0,1},{0,-1},
  {.707106781f,.707106781f},{-.707106781f,.707106781f},
  {.707106781f,-.707106781f},{-.707106781f,-.707106781f}};
 float support=0.f;
 if(b24_g74_near_original_floor(city,point[0],point[1],point[2],&support)){
  result.has_floor=1;result.nearest_floor=support;
 }
 for(unsigned i=0;i<8;i++){
  const float targetx=point[0]+dir[i][0]*.08f;
  const float targety=point[1]+dir[i][1]*.08f;
  float x=targetx,y=targety,z=point[2];
  assert(b24_g75_capsule_reconcile(city,
    point[0],point[1],point[2],targetx,targety,point[2],
    grounded,.35f,2.24f,&x,&y,&z));
  assert(isfinite(x)&&isfinite(y)&&isfinite(z));
  ++result.tested;
  result.proposed+=hypotf(targetx-point[0],targety-point[1])>.001f;
  if(hypotf(x-point[0],y-point[1])>.001f)++result.accepted;
  else ++result.rejected;
 }
 return result;
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 const IM2G275OriginalGoal *s=&im2_g275_original_mission000_move_source;
 assert(s->source_actor_id==1062&&s->source_target_id==1892);
 assert(s->original_lua_duration_arg==3000&&s->original_source_PositionDummy_Num==0);
 assert(s->native_selected_component_count==1&&s->original_first_child_id==1893);
 assert(fabsf(s->first_authored_local_x-(-.493f))<1.e-4f);
 assert(fabsf(s->first_authored_local_y-(-28.062f))<1.e-4f);
 assert(fabsf(s->first_authored_local_z-3.705f)<1.e-4f);
 B24C1OriginalCollision city={0};
 assert(b24_g70_g68_collision_load(&city,argv[1]));
 assert(city.ready&&city.count==1910u&&city.wall_count==1690u);
 const float points[][3]={
  {s->first_authored_local_x,s->first_authored_local_y,s->first_authored_local_z},
  {-1.319f,-6.747f,25.054001f}, /* MC original authored local, not boot feet */
  {-1.319f,-6.747f,.0725f}, /* original G249 low support diagnostic, not boot */
  {-1.319f,-6.747f,2.82955f} /* original G249 mid support diagnostic, not boot */
 };
 const char *labels[]={
  "2010_SOURCED_MISSION_POSITION1_LOCAL_NOT_GAME_WORLD",
  "2010_SOURCED_MC_LOCAL_TRANSFORM_NOT_GAME_BOOT",
  "G249_ORIGINAL_C1L1_MC_LOW_GROUND_HYPOTHESIS",
  "G249_ORIGINAL_C1L1_MC_MID_GROUND_HYPOTHESIS"
 };
 for(unsigned i=0;i<4;i++) {
  const G276Probe gr=analyze(&city,points[i],1);
  const G276Probe air=analyze(&city,points[i],0);
  assert(gr.tested==8u&&air.tested==8u);
  assert(gr.proposed==8u&&air.proposed==8u);
  assert(gr.accepted<=8u&&air.accepted<=8u);
  printf("G276 actual_2010_C1L1_G66C %s source_local=(%.3f,%.3f,%.3f) original_nearby_floor=%u source_floor_z_if_found=%.4f grounded_allowed=%u/8 airborne_allowed=%u/8 original_real_world_actor_boot_proven=NO\\n",
   labels[i],points[i][0],points[i][1],points[i][2],
   gr.has_floor,gr.nearest_floor,gr.accepted,air.accepted);
 }
 assert(hypotf(s->first_authored_local_x-(-1.319f),
               s->first_authored_local_y-(-6.747f))>20.f);
 puts("G276 PASS original 2010 scripted goal source is DISTINCT from MC authored local spawn, tested against actual G66C 1910 faces, player foot/world Z still UNKNOWN; hardware Vita NOT TESTED, NO NEW VPK");
 b24_c1_original_collision_free(&city);
 return 0;
}
