#include "im2_test_opponent.h"
#include "im2_game_camera.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static B24C1OriginalCollision city;static B24C1OriginalCollisionFace face;
static void floor_init(void){
 const float points[]={-100,-100,0,100,-100,0,0,100,0};memcpy(face.xyz,points,sizeof(points));
 face.minx=face.miny=-100;face.maxx=face.maxy=100;face.minz=face.maxz=0;
 city.ready=1;city.faces=&face;city.count=1;
}
static void bind(B16Combat *c,Im2TestOpponent *s){
 b16_combat_init(c);c->test_target=&s->target;c->test_ray_valid=1;
 c->test_ray_origin[2]=1;c->test_ray_direction[1]=1;
}
static void spawn(Im2TestOpponent *s){assert(im2_test_opponent_spawn(s,&city,0,0,0,0,1000));assert(s->spawned&&s->target.present&&s->target.hp==100);}
int main(int argc,char **argv){
 if(argc==2){
  assert(b24_g70_g68_collision_load(&city,argv[1]));float x=0,y=0,z=0;
  assert(b24_g75_capsule_reconcile(&city,0,0,0,0,0,0,1,.35f,2.24f,&x,&y,&z));
  Im2TestOpponent actor={0};
  assert(im2_test_opponent_spawn(&actor,&city,0,0,0,0,1000));float ground=0;
  assert(b24_g75_support_at(&city,actor.x,actor.y,actor.z,&ground));
  assert(b24_g75_body_clear_at(&city,actor.x,actor.y,actor.z,.35f,2.24f));
  const float viewer[]={0,0,1};
  assert(!im2_test_segment_blocked(&city,viewer,actor.target.center));
  printf("PASS test opponent source-supported placement from current diagnostic origin: %.4f %.4f %.4f (NOT native spawn)\n",actor.x,actor.y,actor.z);
  b24_c1_original_collision_free(&city);return 0;
 }
 assert(argc==1);
 floor_init();Im2TestOpponent s={0};spawn(&s);B16Combat c;bind(&c,&s);B14World world; b14_world_init(&world);
 const float origin[]={0,0,1};assert(b16_combat_fire(&c,&world,origin)==1);
 assert(s.target.hp==65&&s.target.hits==1&&world.hits==0&&!world.completed&&c.test_hit_this_shot);
 assert(fabsf(c.test_impact[1]-4.3f)<.001f);
 c.cooldown=0;c.test_ray_direction[0]=1;c.test_ray_direction[1]=0;
 assert(b16_combat_fire(&c,&world,origin)==0&&s.target.hp==65);
 c.cooldown=0;c.test_ray_direction[0]=0;c.test_ray_direction[1]=1;c.test_occluded=1;
 assert(b16_combat_fire(&c,&world,origin)==0&&s.target.hp==65);
 c.cooldown=0;c.test_occluded=0;c.mode=B16_UNIBEAM;c.energy=49;
 assert(b16_combat_fire(&c,&world,origin)==-2&&s.target.hp==65);
 c.energy=100;assert(b16_combat_fire(&c,&world,origin)==1&&s.target.hp==0);
 im2_test_opponent_tick(&s,0,4,0,2200,0);assert(s.phase==IM2_TEST_DOWN&&s.player_hp==100);
 const float down_heading=s.heading;im2_test_opponent_tick(&s,5,0,0,2300,0);assert(s.heading==down_heading);
 spawn(&s);bind(&c,&s);c.mode=B16_MISSILE;
 assert(b16_combat_fire(&c,&world,origin)==1&&c.active_missile&&c.energy==75);
 for(unsigned i=0;i<20&&c.active_missile;i++)b16_combat_tick(&c,&world,.1f);
 assert(!c.active_missile&&s.target.hp==0&&world.hits==0&&!world.completed);
 spawn(&s);bind(&c,&s);c.mode=B16_MISSILE;
 assert(b16_combat_fire(&c,&world,origin)==1);c.test_occluded=1;b16_combat_tick(&c,&world,.1f);
 assert(!c.active_missile&&s.target.hp==100);
 bind(&c,&s);c.mode=B16_MELEE;
 assert(b16_combat_fire(&c,&world,origin)==-4&&s.target.hp==100);
 const float close[]={0,4,1};assert(b16_combat_fire(&c,&world,close)==1&&s.target.hp==55);
 im2_test_opponent_tick(&s,0,4,0,1200,0);assert(s.phase==IM2_TEST_HURT);
 im2_test_opponent_animation_done(&s,1500);
 im2_test_opponent_tick(&s,0,4,0,2200,0);assert(s.phase==IM2_TEST_ATTACK&&s.player_hp==90);
 Im2TestOpponent saved=s;im2_test_opponent_tick(&s,0,4,0,9999,1);assert(!memcmp(&s,&saved,sizeof(s)));
 im2_test_opponent_animation_done(&s,2500);im2_test_opponent_tick(&s,0,4,0,3000,0);assert(s.player_hp==90);
 s.player_occluded=1;im2_test_opponent_tick(&s,0,4,0,3400,0);assert(s.player_hp==90);
 s.player_occluded=0;im2_test_opponent_tick(&s,0,4,0,3400,0);assert(s.player_hp==80);
 B24C1OriginalCollisionFace wall={0};const float points[]={-2,2,-1,2,2,-1,0,2,4};memcpy(wall.xyz,points,sizeof(points));
 B24C1OriginalCollision obstruction={0};obstruction.ready=1;obstruction.count=1;obstruction.faces=&wall;
 const float target[]={0,5,1},miss[]={5,5,1};assert(im2_test_segment_blocked(&obstruction,origin,target));
 assert(!im2_test_segment_blocked(&obstruction,miss,target));
 /* Current GPU camera centre, not legacy sphere coordinates278/110. */
 for(unsigned k=0;k<4;k++){
  IM2Camera input={0};input.orbit=(float)k*.7f;input.pitch=.12f;input.cam_z=1;input.camera_distance=4.35f;
  B24Unified g={0};g.camera_base.shoulder_to_chase=(float)k/3.f;
  B24GpuCamera camera;B24GpuCameraMatrices mat;assert(im2_game_camera(&input,&g,&camera,&mat));
  B24GpuVec3 p={camera.eye.x+(camera.target.x-camera.eye.x)*3,
    camera.eye.y+(camera.target.y-camera.eye.y)*3,camera.eye.z+(camera.target.z-camera.eye.z)*3};
  float x,y,z;assert(b24_gpu_world_to_screen(&mat,p,480,272,&x,&y,&z));
  assert(fabsf(x-240)<.01f&&fabsf(y-136)<.01f);
 }
 /* No external target: retain the old isolated prototype sphere behavior. */
 B16Combat legacy;B14World old_world;b16_combat_init(&legacy);b14_world_init(&old_world);legacy.mode=B16_MELEE;
 const float old_origin[]={0,6,1};assert(b16_combat_fire(&legacy,&old_world,old_origin)==1);
 assert(legacy.hitpoints[0]==55&&old_world.hits==0);
 for(unsigned i=0;i<4;i++)b16_combat_tick(&legacy,&old_world,.12f);
 assert(b16_combat_fire(&legacy,&old_world,old_origin)==1&&old_world.hits==1);
 puts("PASS explicit Mark IV test opponent: prototype repulsor/beam/missile/melee, LOS, pause, retaliation, reset, no mission mutation; GPU reticle alignment");return 0;
}
