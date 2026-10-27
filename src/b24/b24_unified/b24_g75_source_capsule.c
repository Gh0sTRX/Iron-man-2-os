#include "b24_g75_source_capsule.h"
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
#include "b24_g277_real_c1l1_ground_reject_reasons.h"
/* G277_GROUND_REJECTION_BREAKDOWN observational only */
static B24G277CollisionReasons g277_last={0};
B24G277CollisionReasons b24_g277_last_collision_reasons(void){return g277_last;}
#endif
#include "b24_gpu_g68_collision.h"
#include "b24_g156_exact_vertical_triangle_contact.h"
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
#include "b24_g159_real_source_road.h"
/* G159_SOURCE_ROAD_CANDIDATE uses actual original 2010 atlas12 triangles.
   SOURCE-authentic vertices, EXPERIMENTAL PORT ground policy only. */
static B24G159Road g159_source_road={0};
static int g159_attempted_road_load=0;
#endif
#ifdef B24_G108_SOURCE_VISUAL_WALLS
#include "b24_g108_visible_original_wall_grid.h"
/* G108_SUPPLEMENT_AUTHORED_RENDER_GEOMETRY */
static B24G108Grid g108_source_steep_walls={0};
static int g108_attempted_load=0;
#endif
#include <math.h>
#include <stddef.h>
#include <stdint.h>
/* All authored world coordinates are Z-up source C1L1.
 * No guessed geometry, no other engine objects/ground-height constants. */
static float fmax2(float a,float b){return a>b?a:b;}
static int finite3(float x,float y,float z){
 return isfinite(x)&&isfinite(y)&&isfinite(z)&&
  fabsf(x)<100000.f&&fabsf(y)<100000.f&&fabsf(z)<100000.f;
}
static int wall_clear(const B24C1OriginalCollision *world,
 float x,float y,float feet,float r,float height){
#ifdef B24_G108_SOURCE_VISUAL_WALLS
 /* G128: the old G75 constant rectangle was only the beta camera viewport.
  * It clipped real 2010 source C1L1 buildings outside central X/Y, despite
  * their triangles being loaded. Derive conservative WORLD bounds from
  * actual original G66 city source once the G108 indexed scene is ready. */
 if(g108_source_steep_walls.ready){
  if(!b24_g108_grid_source_bounds_allow(&g108_source_steep_walls,x,y,r))
   return 0;
 }else if(x<-325.f+r||x>331.f-r||y<-352.f+r||y>255.f-r)
  return 0;
#else
 if(x<-325.f+r||x>331.f-r||y<-352.f+r||y>255.f-r)return 0;
#endif
 for(uint32_t i=0;i<world->count;i++){
  const B24C1OriginalCollisionFace *f=&world->faces[i];
  if(!f->wall||f->maxz<feet||f->minz>feet+height||
      x<f->minx-r||x>f->maxx+r||
      y<f->miny-r||y>f->maxy+r)continue;
  /* G156 CONTINUOUS TRUE SOURCE WALL: no missed between-slice
   * contact; exact Z-clipped authored triangle vs upright XY capsule.
   * Source face is already marked wall by existing original native
   * G68 triangle orientation policy. No new solidity inferred. */
  if(b24_g156_exact_vertical_triangle_contact(
       f->xyz,x,y,feet,r,height))return 0;
 }
#ifdef B24_G108_SOURCE_VISUAL_WALLS
 /* Real 2010 render-source walls supplement original G68 1,910-source
  * authored collider inside the SAME G75 swept-capsule test. Never
  * duplicate movement, update the world, or fabricate a contact event. */
 if(!b24_g108_grid_clear(&g108_source_steep_walls,x,y,feet,r,height))
  return 0;
#endif
 return 1;
}
static int triangle_z(const B24C1OriginalCollisionFace *f,
 float x,float y,float *z){
 if(f->wall||x<f->minx-.0001f||x>f->maxx+.0001f||
    y<f->miny-.0001f||y>f->maxy+.0001f)return 0;
 const float *p=f->xyz;
 float u=p[3]-p[0],v=p[4]-p[1],w=p[6]-p[0],q=p[7]-p[1];
 float det=u*q-v*w;
 if(fabsf(det)<1e-8f)return 0;
 float dx=x-p[0],dy=y-p[1];
 float a=(dx*q-dy*w)/det;
 float b=(u*dy-v*dx)/det;
 if(a<-.0002f||b<-.0002f||a+b>1.0002f)return 0;
 *z=p[2]+a*(p[5]-p[2])+b*(p[8]-p[2]);
 return isfinite(*z);
}
int b24_g75_floor_crossed(const B24C1OriginalCollision *world,
 float x,float y,float z_before,float z_after,float *floor_z){
 if(!world||!world->ready||!floor_z||!finite3(x,y,z_before)||
    !isfinite(z_after)||z_after>z_before+.05f)return 0;
 int found=0;float best=-100000.f;
 for(uint32_t i=0;i<world->count;i++){
  const B24C1OriginalCollisionFace *f=&world->faces[i];
  if(f->wall||f->minz>z_before+.08f||f->maxz<z_after-.08f)continue;
  float support;
  if(!triangle_z(f,x,y,&support))continue;
  if(support<=z_before+.08f&&support>=z_after-.08f&&
     (!found||support>best)){found=1;best=support;}
 }
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
 /* Source road MAY be higher than the original G66C collision proxy.
  * Existing genuine native G66C faces always remain loaded unchanged. */
 float source_road_z=0.f;
 if(b24_g159_road_crossed(&g159_source_road,x,y,z_before,z_after,
                          &source_road_z) &&
    (!found||source_road_z>best)){
  found=1;best=source_road_z;
 }
#endif
 if(found)*floor_z=best;
 return found;
}
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
static int g159_authoritative_first_native_then_source_road(
 const B24C1OriginalCollision *world,float x,float y,float z,float *h){
 /* Never override a genuine G66C source support at this foot height. */
 if(b24_g74_near_original_floor(world,x,y,z,h))return 1;
 return b24_g159_road_near(&g159_source_road,x,y,z,h);
}
#else
#define g159_authoritative_first_native_then_source_road b24_g74_near_original_floor
#endif
/* B14_WORLD_HEIGHT_SUPPORT: same native-first/optional-road authority as
 * reconciliation, read-only. Do not snap to a different scene layer. */
int b24_g75_support_at(const B24C1OriginalCollision *world,
 float x,float y,float feet_z,float *support_z){
 if(!world||!world->ready||!support_z||!finite3(x,y,feet_z))return 0;
 float h=0.f;
 if(!g159_authoritative_first_native_then_source_road(world,x,y,feet_z,&h)
     ||fabsf(h-feet_z)>.0001f)return 0;
 *support_z=h;
 return 1;
}
int b24_g75_capsule_reconcile(const B24C1OriginalCollision *world,
 float x0,float y0,float z0,float x1,float y1,float z1,
 int grounded,float radius,float height,float *ox,float *oy,float *oz){
 if(!world||!world->ready||!ox||!oy||!oz||
   !finite3(x0,y0,z0)||!finite3(x1,y1,z1)||
   !isfinite(radius)||radius<.12f||radius>.9f||
   !isfinite(height)||height<1.f||height>3.5f)return 0;
#ifdef B24_G108_SOURCE_VISUAL_WALLS
 /* Load once from the SAME authored original G66 city asset that the
  * existing VitaGL GPU has already loaded. First capsule call only.
  * If source asset cannot load, preserve *baseline* 1,910 faces; do not
  * invent a fake fallback map or crash the entire gameplay main. */
 if(!g108_attempted_load){
  g108_attempted_load=1;
  (void)b24_g108_grid_load(&g108_source_steep_walls,
       "app0:assets/G66_city.g66m",world);
 }
#endif
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
 /* Load the genuine road source once, same G66 GPU already loaded.
  * On missing/corrupt assets, preserve G75 native 1910 behavior.
  * No guessed constant Z and no second world movement tick. */
 if(!g159_attempted_road_load){
  g159_attempted_road_load=1;
  (void)b24_g159_road_open(&g159_source_road,
       "app0:assets/G66_city.g66m");
 }
#endif
 /* G67's sub-22cm wall and floor tests adapted to old B14 as a POST-tick
  * source collision resolver. Game still calls only ONE B14 motion tick. */
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
 g277_last=(B24G277CollisionReasons){0};
#endif
 float dx=x1-x0,dy=y1-y0,dz=z1-z0;
 /* G134_LIMIT_LONG_FRAME_DISPLACEMENT: G75 once limited the number
  * of sweep queries to 80 but did NOT limit displacement, making every
  * substep larger than .22 units on a long stall/rush/hitch. A thin real
  * source wall (x=10.6) can be passed between two 1.25-unit samples.
  * One game tick, 80 MAX steps. If a long frame reports huge movement,
  * accept at most 80*.22 SOURCE units this frame (conservative fail
  * safe), rather than teleport through city geometry. No altered source
  * collision polygon, no fake hit, no second B14 physics tick. */
 const float dmax=fmax2(fmax2(fabsf(dx),fabsf(dy)),fabsf(dz));
 if(dmax>80.f*.22f){
  const float keep=(80.f*.22f)/dmax;
  dx*=keep;dy*=keep;dz*=keep;
 }
 int steps=(int)ceilf(fmax2(fmax2(fabsf(dx),fabsf(dy)),fabsf(dz))/.22f);
 if(steps<1)steps=1;
 if(steps>80)steps=80; /* float rounding guard, not an acceleration */
 float x=x0,y=y0,z=z0;
 const float stepx=dx/steps,stepy=dy/steps,stepz=dz/steps;
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
 g277_last.sweep_substeps=(uint32_t)steps;
#endif
 for(int k=0;k<steps;k++){
  float nextz=z+stepz;
  float supporting=0.f;
  /* Catch a rooftop that lies BETWEEN old/new foot on a descending step.
   * No teleport upwards to a roof above the actor. */
  if(stepz<0&&b24_g75_floor_crossed(world,x,y,z,nextz,&supporting))
    nextz=fmax2(nextz,supporting);
  float tx=x+stepx,ty=y+stepy,accepted=0.f;
  for(int candidate=0;candidate<3;candidate++){
   const float nx=candidate==2?x:tx;
   const float ny=candidate==1?y:ty;
   if(!wall_clear(world,nx,ny,nextz,radius,height)){
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
    ++g277_last.candidate_wall_reject;
#endif
    continue;
   }
   if(grounded){
     float h=0.f;
     /* Ground cannot pass through tall ledges. The G67 original
      * guard only allows ±0.45m source-authored adjacent surface step. */
     if(!g159_authoritative_first_native_then_source_road(world,nx,ny,z,&h)){
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
      ++g277_last.candidate_no_source_support;
#endif
      continue;
     }
     if(h<z-.35f||h>z+.45f){
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
      ++g277_last.candidate_unsupported_step_height;
#endif
      continue;
     }
     nextz=h;
   }
   x=nx;y=ny;
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
   ++g277_last.candidate_accepted;
#endif
   accepted=1.f;break;
  }
  /* Airborne Z can still change while blocked against a wall; but never
   * drift grounded character through an unverified support surface. */
  if(!grounded&&wall_clear(world,x,y,nextz,radius,height))z=nextz;
  else if(grounded&&accepted>0.f)z=nextz;
  else if(grounded&&wall_clear(world,x,y,nextz,radius,height)){
   /* In G9 landing transition, B14 sets flying=false BEFORE the actor
    * reaches the rooftop. Allow vertical descent when currently floating
    * above every authored support, and STOP at the first actually crossed
    * original roof/ground. Do not leave suit frozen mid-air. */
   float original_support;
   if(!g159_authoritative_first_native_then_source_road(world,x,y,z,&original_support))
     z=nextz;
   else if(stepz<0.f && z>original_support+.0001f){
     /* A NEAR floor is not contact. Old G75 stopped descent in the
      * .35-.50 gap between the step guard and near-floor search.
      * Keep descending at the existing bounded rate; never pass through
      * that actual surface, move upwards to a roof, or delete a wall. */
     z=fmax2(nextz,original_support);
   }
  }
 }
 *ox=x;*oy=y;*oz=z;
 return 1;
}
