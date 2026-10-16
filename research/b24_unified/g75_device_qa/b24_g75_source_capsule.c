#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include <math.h>
#include <stddef.h>
#include <stdint.h>
/* All authored world coordinates are Z-up source C1L1.
 * No guessed geometry, no other engine objects/ground-height constants. */
typedef struct{float x,y;} V;
static float fmin2(float a,float b){return a<b?a:b;}
static float fmax2(float a,float b){return a>b?a:b;}
static float clip(float x,float a,float b){return fmin2(fmax2(x,a),b);}
static int finite3(float x,float y,float z){
 return isfinite(x)&&isfinite(y)&&isfinite(z)&&
  fabsf(x)<100000.f&&fabsf(y)<100000.f&&fabsf(z)<100000.f;
}
static float dist_seg2(V p,V a,V b){
 float dx=b.x-a.x,dy=b.y-a.y,dd=dx*dx+dy*dy;
 float t=dd>1e-9f?clip(((p.x-a.x)*dx+(p.y-a.y)*dy)/dd,0.f,1.f):0.f;
 dx=p.x-(a.x+t*dx);dy=p.y-(a.y+t*dy);
 return dx*dx+dy*dy;
}
static int slice(const B24C1OriginalCollisionFace *f,float z,V *aa,V *bb){
 V points[6];int count=0;
 for(int k=0;k<3;k++){
  int n=(k+1)%3;
  float a=f->xyz[k*3+2],b=f->xyz[n*3+2];
  V p={f->xyz[k*3],f->xyz[k*3+1]};
  if(fabsf(a-z)<1e-5f){
   int duplicate=0;
   for(int i=0;i<count;i++)if(dist_seg2(p,points[i],points[i])<1e-8f)duplicate=1;
   if(!duplicate)points[count++]=p;
  }
  if((a<z&&b>z)||(a>z&&b<z)){
   float t=(z-a)/(b-a);
   V q={p.x+t*(f->xyz[n*3]-p.x),
        p.y+t*(f->xyz[n*3+1]-p.y)};
   int duplicate=0;
   for(int i=0;i<count;i++)if(dist_seg2(q,points[i],points[i])<1e-8f)duplicate=1;
   if(!duplicate)points[count++]=q;
  }
 }
 if(count<2)return 0;
 float maxlen=-1.f;
 for(int i=0;i<count;i++)for(int j=i+1;j<count;j++){
  float dx=points[i].x-points[j].x,dy=points[i].y-points[j].y;
  float dd=dx*dx+dy*dy;
  if(dd>maxlen){maxlen=dd;*aa=points[i];*bb=points[j];}
 }
 return maxlen>1e-10f;
}
static int wall_clear(const B24C1OriginalCollision *world,
 float x,float y,float feet,float r,float height){
 if(x<-325.f+r||x>331.f-r||y<-352.f+r||y>255.f-r)return 0;
 for(uint32_t i=0;i<world->count;i++){
  const B24C1OriginalCollisionFace *f=&world->faces[i];
  if(!f->wall||f->maxz<feet||f->minz>feet+height||
      x<f->minx-r||x>f->maxx+r||
      y<f->miny-r||y>f->maxy+r)continue;
  float lo=fmax2(f->minz,feet+.005f);
  float hi=fmin2(f->maxz,feet+height-.005f);
  if(hi<lo)continue;
  float planes[3]={lo,.5f*(lo+hi),hi};
  for(int k=0;k<3;k++){
   V a,b;
   if(slice(f,planes[k],&a,&b) &&
      dist_seg2((V){x,y},a,b)<r*r)return 0;
  }
 }
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
 if(found)*floor_z=best;
 return found;
}
int b24_g75_capsule_reconcile(const B24C1OriginalCollision *world,
 float x0,float y0,float z0,float x1,float y1,float z1,
 int grounded,float radius,float height,float *ox,float *oy,float *oz){
 if(!world||!world->ready||!ox||!oy||!oz||
   !finite3(x0,y0,z0)||!finite3(x1,y1,z1)||
   !isfinite(radius)||radius<.12f||radius>.9f||
   !isfinite(height)||height<1.f||height>3.5f)return 0;
 /* G67's sub-22cm wall and floor tests adapted to old B14 as a POST-tick
  * source collision resolver. Game still calls only ONE B14 motion tick. */
 float dx=x1-x0,dy=y1-y0,dz=z1-z0;
 int steps=(int)ceilf(fmax2(fmax2(fabsf(dx),fabsf(dy)),fabsf(dz))/.22f);
 if(steps<1)steps=1;if(steps>80)steps=80;
 float x=x0,y=y0,z=z0;
 const float stepx=dx/steps,stepy=dy/steps,stepz=dz/steps;
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
   if(!wall_clear(world,nx,ny,nextz,radius,height))continue;
   if(grounded){
     float h=0.f;
     /* Ground cannot pass through tall ledges. The G67 original
      * guard only allows ±0.45m source-authored adjacent surface step. */
     if(!b24_g74_near_original_floor(world,nx,ny,z,&h))continue;
     if(h<z-.35f||h>z+.45f)continue;
     nextz=h;
   }
   x=nx;y=ny;
   accepted=1.f;break;
  }
  /* Airborne Z can still change while blocked against a wall; but never
   * drift grounded character through an unverified support surface. */
  if(!grounded&&wall_clear(world,x,y,nextz,radius,height))z=nextz;
  else if(grounded&&accepted>0.f)z=nextz;
 }
 *ox=x;*oy=y;*oz=z;
 return 1;
}
