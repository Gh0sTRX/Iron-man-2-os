/* G251 source-original 2010 16 typed SpawnPoint CLASS=71 node transforms
 * vs ORIGINAL C1L1 1910 G66C collision and one current Vita B14/G75 chain.
 * SOURCE CANDIDATES only: spawn nodes are not confirmed player start
 * nor are authored transform Z values guaranteed character foot height.
 * Uses real 2010 owner-generated G250 header; never fabricates positions.
 * Do not patch game runtime positions, contact geometry or Vita VPK.
 */
#include "b14_world.h"
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g250_source_authentic_16_spawn_candidates.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

enum{FRAMES=60};
typedef struct{uint32_t proposals,accepted,blocked;double dist;} Window;
static Window run(const B24C1OriginalCollision *world,
                  const G250SourceSpawnCandidate *src,int flying,
                  float stick_x,float stick_y){
 B14World p;
 b14_world_init(&p);
 p.x=src->x;p.y=src->y;p.z=src->z;
 p.target_z=src->z;p.cam_x=src->x;p.cam_y=src->y;
 p.cam_z=src->z+p.head_height;
 p.flying=flying;p.flight_stage=flying?2:0;
 Window w={0};
 for(int i=0;i<FRAMES;i++){
  const float ox=p.x,oy=p.y,oz=p.z;
  b14_world_tick(&p,1.f/60.f,stick_x,stick_y,0.f,0.f,0.f);
  const float proposed=hypotf(p.x-ox,p.y-oy);
  float x=p.x,y=p.y,z=p.z;
  assert(b24_g75_capsule_reconcile(world,ox,oy,oz,
    p.x,p.y,p.z,!p.flying,.35f,2.24f,&x,&y,&z));
  assert(isfinite(x)&&isfinite(y)&&isfinite(z));
  const float accepted=hypotf(x-ox,y-oy);
  w.proposals+=(proposed>.0001f);
  w.accepted+=(accepted>.0001f);
  w.blocked+=(proposed>.0001f&&accepted<.0001f);
  w.dist+=accepted;
  p.x=x;p.y=y;p.z=z;
 }
 return w;
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision geo={0};
 assert(b24_g70_g68_collision_load(&geo,argv[1]));
 assert(geo.ready&&geo.count==1910u&&geo.wall_count==1690u);
 const float dir[8][2]={{0,1},{0,-1},{1,0},{-1,0},
  {.70710678f,.70710678f},{-.70710678f,.70710678f},
  {.70710678f,-.70710678f},{-.70710678f,-.70710678f}};
 unsigned total=0,groundDirections=0,flightDirections=0;
 unsigned allGroundBlocked=0;
 for(unsigned k=0;k<16;k++){
  const G250SourceSpawnCandidate *source=&g250_source_spawns[k];
  assert(source->original_native_node_id>0);
  char expected[32];
  snprintf(expected,sizeof(expected),"SpawnPoint%03u",k);
  assert(!strcmp(expected,source->name));
  float original_floor=0.f;
  const int authoredSupport=b24_g74_near_original_floor(
   &geo,source->x,source->y,source->z,&original_floor);
  unsigned movedGround=0,movedFlight=0,proposedGround=0;
  unsigned grounded_rejections=0;
  for(unsigned d=0;d<8;d++){
   const Window gr=run(&geo,source,0,dir[d][0],dir[d][1]);
   const Window fl=run(&geo,source,1,dir[d][0],dir[d][1]);
   if(gr.proposals)proposedGround++;
   if(gr.accepted)groundDirections++,movedGround++;
   if(fl.accepted)flightDirections++,movedFlight++;
   grounded_rejections+=gr.blocked;
   total+=2;
  }
  allGroundBlocked+=movedGround==0;
  printf("G251 ORIGINAL SPAWN C1L1 source_node=%s class=71 nodeID=%d tagged_position=(%.3f,%.3f,%.3f) original_G66C_floor_near_raw_node_Z=%d source_native_Z=%.3f ground_accepted_directions=%u/8 flight_accepted_directions=%u/8 B14_proposed_directions=%u/8 collision_rejected_frames=%u player_spawn_PROVEN=NO raw_Z_is_actor_feet_PROVEN=NO\n",
    source->name,source->original_native_node_id,
    source->x,source->y,source->z,
    authoredSupport,original_floor,movedGround,movedFlight,
    proposedGround,grounded_rejections);
 }
 assert(total==256u);
 printf("G251 REAL C1L1 source summary: original_typed_SpawnPoint_nodes=16 2010_native_G66C_triangles=%u native_wall_faces=%u 8directions*16*2modes*60frames=15360 total_ground_direction_accepts=%u/128 flight=%u/128 ground_all_8_blocked_spawn_nodes=%u/16; PHYSICAL_VITA=NOT_RUN; NODE_IS_PLAYER_SPAWN=UNKNOWN; VPK=NO\n",
  geo.count,geo.wall_count,groundDirections,flightDirections,allGroundBlocked);
 b24_c1_original_collision_free(&geo);
 return 0;
}
