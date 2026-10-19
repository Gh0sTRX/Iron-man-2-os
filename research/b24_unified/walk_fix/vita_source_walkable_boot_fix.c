#include "vita_source_walkable_boot_fix.h"
#include "b24_g75_source_capsule.h"
#include <math.h>
#include <float.h>
#include <string.h>
/* Exact height on original G66C nonwall barycentric face. Both authored
 * source triangles and their original coordinates remain unchanged. */
static int original_face_height(const B24C1OriginalCollisionFace *f,
 float x,float y,float *z){
 if(f->wall||x<f->minx-.0001f||x>f->maxx+.0001f||
   y<f->miny-.0001f||y>f->maxy+.0001f)return 0;
 const float *p=f->xyz;
 const float ux=p[3]-p[0],uy=p[4]-p[1];
 const float vx=p[6]-p[0],vy=p[7]-p[1];
 const float det=ux*vy-uy*vx;
 if(fabsf(det)<1.e-8f)return 0;
 const float dx=x-p[0],dy=y-p[1];
 const float a=(dx*vy-dy*vx)/det,b=(ux*dy-uy*dx)/det;
 if(a<-.0002f||b<-.0002f||a+b>1.0002f)return 0;
 *z=p[2]+a*(p[5]-p[2])+b*(p[8]-p[2]);
 return isfinite(*z);
}
static unsigned walkable_directions(const B24C1OriginalCollision *w,
 float x,float y,float z){
 static const float dirs[8][2]={
 {1,0},{-1,0},{0,1},{0,-1},
 {.707106781f,.707106781f},{-.707106781f,.707106781f},
 {.707106781f,-.707106781f},{-.707106781f,-.707106781f}};
 unsigned ok=0;
 for(unsigned i=0;i<8;i++){
  const float tx=x+.08f*dirs[i][0],ty=y+.08f*dirs[i][1];
  float rx=tx,ry=ty,rz=z;
  if(!b24_g75_capsule_reconcile(w,x,y,z,tx,ty,z,1,.35f,2.24f,
      &rx,&ry,&rz))return 0;
  if(hypotf(rx-x,ry-y)>.001f)++ok;
 }
 return ok;
}
int im2_vita_source_walkable_boot(const B24C1OriginalCollision *w,
 float preferred_x,float preferred_y,float preferred_z,
 Im2VitaGroundBootCandidate *out){
 if(!w||!w->ready||w->count!=1910u||!out||
   !isfinite(preferred_x)||!isfinite(preferred_y)||
   !isfinite(preferred_z))return 0;
 /* Probe the *existing* Vita B14 world XY first, and then the
  * genuine original 2010 MC authored LOCAL XY (-1.319,-6.747).
  * Original MC local XY is a reference, not authenticated runtime spawn.
  * No hardcoded fake floor Z. Every candidate comes from G66C triangle. */
 const float coords[2][2]={{preferred_x,preferred_y},{-1.319f,-6.747f}};
 int found=0;float best=FLT_MAX;
 Im2VitaGroundBootCandidate candidate={0};
 unsigned face_count=0;
 for(unsigned area=0;area<2;area++){
  const float x=coords[area][0],y=coords[area][1];
  for(uint32_t i=0;i<w->count;i++){
   float z;
   if(!original_face_height(&w->faces[i],x,y,&z))continue;
   ++face_count;
   if(z<-.01f||z>40.f)continue;
   float confirmed;
   if(!b24_g74_near_original_floor(w,x,y,z,&confirmed)||
     fabsf(confirmed-z)>.005f)continue;
   const unsigned n=walkable_directions(w,x,y,z);
   if(n<6u)continue;
   /* Prefer nearest currently selected Vita boot XY and least vertical
    * displacement; if there is a reachable native source floor at
    * the current XY never assume a 2010 iOS scene start elsewhere. */
   const float dx=x-preferred_x,dy=y-preferred_y;
   const float cost=dx*dx+dy*dy+.25f*fabsf(z-preferred_z);
   if(!found||cost<best){
    candidate=(Im2VitaGroundBootCandidate){x,y,z,n,0u};
    best=cost;found=1;
   }
  }
 }
 if(!found)return 0;
 candidate.source_floor_candidates=face_count;
 *out=candidate;
 return 1;
}
