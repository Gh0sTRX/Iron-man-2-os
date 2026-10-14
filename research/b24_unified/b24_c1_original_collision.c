#include "b24_c1_original_collision.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Little endian target verified on Vita ARM; source format is 40 bytes/tri. */
static int valid(float x){return isfinite(x)&&fabsf(x)<100000.f;}
static float clampf(float x,float a,float b){return x<a?a:x>b?b:x;}
void b24_c1_original_collision_free(B24C1OriginalCollision *c){
 if(!c)return;
 free(c->faces);memset(c,0,sizeof(*c));
}
int b24_c1_original_collision_load(B24C1OriginalCollision *c,const char *path){
 if(!c||!path)return 0;
 FILE *f=fopen(path,"rb");
 if(!f)return 0;
 unsigned char header[20];
 uint32_t n=0;
 B24C1OriginalCollision tmp={0};
 if(fread(header,1,sizeof(header),f)!=sizeof(header)||memcmp(header,"C1WC",4)){
  fclose(f);return 0;
 }
 uint32_t vals[4];memcpy(vals,header+4,sizeof(vals));
 if(vals[0]!=1u||vals[1]!=1908u||vals[2]!=2u||vals[3]!=40u){
  fclose(f);return 0;
 }
 n=vals[1];
 tmp.faces=calloc(n,sizeof(*tmp.faces));
 if(!tmp.faces){fclose(f);return 0;}
 tmp.count=n;
 for(uint32_t i=0;i<n;i++){
  B24C1OriginalCollisionFace *o=&tmp.faces[i];
  if(fread(o->xyz,sizeof(float),9,f)!=9 ||
     fread(&o->source,sizeof(uint32_t),1,f)!=1 || o->source>1u){
   fclose(f);b24_c1_original_collision_free(&tmp);return 0;
  }
  for(unsigned j=0;j<9;j++)if(!valid(o->xyz[j])){
   fclose(f);b24_c1_original_collision_free(&tmp);return 0;
  }
  o->minx=o->maxx=o->xyz[0];o->miny=o->maxy=o->xyz[1];
  o->minz=o->maxz=o->xyz[2];
  for(unsigned k=1;k<3;k++){
   o->minx=fminf(o->minx,o->xyz[3*k]);
   o->maxx=fmaxf(o->maxx,o->xyz[3*k]);
   o->miny=fminf(o->miny,o->xyz[3*k+1]);
   o->maxy=fmaxf(o->maxy,o->xyz[3*k+1]);
   o->minz=fminf(o->minz,o->xyz[3*k+2]);
   o->maxz=fmaxf(o->maxz,o->xyz[3*k+2]);
  }
  const float *v=o->xyz;
  float ax=v[3]-v[0],ay=v[4]-v[1],az=v[5]-v[2];
  float bx=v[6]-v[0],by=v[7]-v[1],bz=v[8]-v[2];
  float nx=ay*bz-az*by,ny=az*bx-ax*bz,nz=ax*by-ay*bx;
  float norm=nx*nx+ny*ny+nz*nz;
  if(!isfinite(norm)||norm<1.e-8f){
   fclose(f);b24_c1_original_collision_free(&tmp);return 0;
  }
  /* Original steep wall source: drop floors/roofs from lateral blocker. */
  o->wall=(uint8_t)((nz*nz<.3364f*norm)&&(o->maxz-o->minz>.1f));
  tmp.wall_count+=(uint32_t)o->wall;
 }
 int tail=fgetc(f);
 fclose(f);
 if(tail!=EOF||tmp.wall_count<100u||tmp.wall_count>n){
  b24_c1_original_collision_free(&tmp);return 0;
 }
 tmp.ready=1;
 b24_c1_original_collision_free(c);
 *c=tmp;return 1;
}
typedef struct {float x,y;} Vec2;
static float cross2(Vec2 a,Vec2 b){return a.x*b.y-a.y*b.x;}
static float dot2(Vec2 a,Vec2 b){return a.x*b.x+a.y*b.y;}
static Vec2 sub(Vec2 a,Vec2 b){Vec2 r={a.x-b.x,a.y-b.y};return r;}
static Vec2 add(Vec2 a,Vec2 b){Vec2 r={a.x+b.x,a.y+b.y};return r;}
static Vec2 scale(Vec2 a,float k){Vec2 r={a.x*k,a.y*k};return r;}
/* Horizontal original wall triangle slice at actor torso's Z.
   Original index order/winding retained. No arbitrary bounding boxes. */
static int slice(const B24C1OriginalCollisionFace *f,float z,Vec2 *a,Vec2 *b){
 Vec2 xy[3];float zz[3];int n=0;
 for(int i=0;i<3;i++){
  xy[i]=(Vec2){f->xyz[3*i],f->xyz[3*i+1]};
  zz[i]=f->xyz[3*i+2];
 }
 for(int i=0;i<3;i++){
  int j=(i+1)%3;
  float za=zz[i]-z,zb=zz[j]-z;
  if(fabsf(za)<1e-5f){
   Vec2 pt=xy[i];
   int dup=0;
   if(n>0&&dot2(sub(pt,*a),sub(pt,*a))<1e-6f)dup=1;
   if(n>1&&dot2(sub(pt,*b),sub(pt,*b))<1e-6f)dup=1;
   if(!dup){if(n==0)*a=pt;else if(n==1)*b=pt;n++;if(n>=2)return 1;}
  }
  if((za>0.f&&zb<0.f)||(za<0.f&&zb>0.f)){
   float t=za/(za-zb);
   Vec2 pt=add(xy[i],scale(sub(xy[j],xy[i]),t));
   int dup=0;
   if(n>0&&dot2(sub(pt,*a),sub(pt,*a))<1e-6f)dup=1;
   if(n>1&&dot2(sub(pt,*b),sub(pt,*b))<1e-6f)dup=1;
   if(!dup){if(n==0)*a=pt;else if(n==1)*b=pt;n++;if(n>=2)return 1;}
  }
 }
 return 0;
}
/* Collision is swept between B14 old/new positions, so a fast RUSH
   cannot tunnel straight through a wall. Finite-segment endpoint contacts
   are deferred; only segment interior contacts are authoritatively resolved.
   Stops/slides along the TRUE original triangle, never through a fake box. */
int b24_c1_original_collision_resolve(const B24C1OriginalCollision *c,
 float oldx,float oldy,float oldz,float nextz,float radius,
 float *nextx,float *nexty){
 if(!c||!c->ready||!nextx||!nexty||
    !valid(oldx)||!valid(oldy)||!valid(oldz)||!valid(nextz)||
    !valid(*nextx)||!valid(*nexty)||!isfinite(radius)||
    radius<.12f||radius>.9f)return 0;
 Vec2 old={oldx,oldy},pos={*nextx,*nexty};
 const float torso_z=nextz+.7f;
 float minx=fminf(old.x,pos.x)-radius,maxx=fmaxf(old.x,pos.x)+radius;
 float miny=fminf(old.y,pos.y)-radius,maxy=fmaxf(old.y,pos.y)+radius;
 /* 1908 original triangles; cheap AABB+Z broadphase first; 60fps is
    still device-unverified after adding collisions. No GPU calls here. */
 for(unsigned step=0;step<2;step++){
  int altered=0;
  for(uint32_t i=0;i<c->count;i++){
   const B24C1OriginalCollisionFace *f=&c->faces[i];
   if(!f->wall||torso_z<f->minz||torso_z>f->maxz||
      f->maxx<minx||f->minx>maxx||f->maxy<miny||f->miny>maxy)continue;
   Vec2 a,b;
   if(!slice(f,torso_z,&a,&b))continue;
   Vec2 seg=sub(b,a);
   float len=sqrtf(dot2(seg,seg));
   if(len<1e-5f)continue;
   Vec2 t=scale(seg,1.f/len),n={-t.y,t.x};
   float start=dot2(sub(old,a),n);
   float end=dot2(sub(pos,a),n);
   if(fabsf(start)<radius+.0001f)continue; /* already inside, do not teleport */
   float side=start>0.f?1.f:-1.f;
   if(side*end>=radius)continue;
   float denom=start-end;
   if(fabsf(denom)<1.e-5f)continue;
   float hit_t=(start-side*radius)/denom;
   if(hit_t<0.f||hit_t>1.f)continue;
   Vec2 move=sub(pos,old);
   Vec2 hit=add(old,scale(move,hit_t));
   float edge=dot2(sub(hit,a),t);
   if(edge<-.001f||edge>len+.001f)continue;
   /* Slide tangentially along wall for remaining movement. */
   float remaining=dot2(move,t)*(1.f-hit_t);
   float dest=clampf(edge+remaining,0.f,len);
   pos=add(add(a,scale(t,dest)),scale(n,side*(radius+.001f)));
   altered=1;
  }
  if(!altered)break;
 }
 *nextx=pos.x;*nexty=pos.y;
 return 1;
}
