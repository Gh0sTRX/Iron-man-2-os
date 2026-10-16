#include "b24_gpu_g68_collision.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int good(float v){return isfinite(v)&&fabsf(v)<100000.f;}
int b24_g70_g68_collision_load(B24C1OriginalCollision *out,const char *path){
 if(!out||!path)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 char magic[4];uint32_t version=0,count=0;
 if(fread(magic,1,4,f)!=4||memcmp(magic,"G66C",4)||
    fread(&version,4,1,f)!=1||fread(&count,4,1,f)!=1||
    version!=1u||count!=1910u){
  fclose(f);return 0;
 }
 B24C1OriginalCollision tmp={0};
 tmp.faces=calloc(count,sizeof(*tmp.faces));
 if(!tmp.faces){fclose(f);return 0;}
 tmp.count=count;
 for(uint32_t i=0;i<count;i++){
  B24C1OriginalCollisionFace *a=&tmp.faces[i];
  if(fread(a->xyz,4,9,f)!=9){
    fclose(f);b24_c1_original_collision_free(&tmp);return 0;
  }
  for(int j=0;j<9;j++)if(!good(a->xyz[j])){
    fclose(f);b24_c1_original_collision_free(&tmp);return 0;
  }
  a->source=0u; /* G66C has no C1WC model-group tag; not a sourced class. */
  a->minx=a->maxx=a->xyz[0];a->miny=a->maxy=a->xyz[1];
  a->minz=a->maxz=a->xyz[2];
  for(int j=1;j<3;j++){
   const float x=a->xyz[3*j],y=a->xyz[3*j+1],z=a->xyz[3*j+2];
   a->minx=fminf(x,a->minx);a->maxx=fmaxf(x,a->maxx);
   a->miny=fminf(y,a->miny);a->maxy=fmaxf(y,a->maxy);
   a->minz=fminf(z,a->minz);a->maxz=fmaxf(z,a->maxz);
  }
  const float *v=a->xyz;
  float x=v[3]-v[0],y=v[4]-v[1],z=v[5]-v[2];
  float u=v[6]-v[0],t=v[7]-v[1],w=v[8]-v[2];
  float nx=y*w-z*t,ny=z*u-x*w,nz=x*t-y*u;
  const float n=nx*nx+ny*ny+nz*nz;
  if(!isfinite(n)||n<1.e-8f){
    fclose(f);b24_c1_original_collision_free(&tmp);return 0;
  }
  /* Identical steep-face cutoff .58 as G68 source triangle collision. */
  a->wall=(uint8_t)(nz*nz<.3364f*n&&(a->maxz-a->minz)>.1f);
  tmp.wall_count+=a->wall;
 }
 int end=fgetc(f);fclose(f);
 if(end!=EOF||tmp.wall_count<100u||tmp.wall_count>count){
   b24_c1_original_collision_free(&tmp);return 0;
 }
 tmp.ready=1;
 b24_c1_original_collision_free(out);
 *out=tmp;return 1;
}

/* G74 query: real 2010 source nonwall triangles, exact XY barycentric Z.
 * Never recover distant roofs below/above the actor. Port of the tested G67
 * source_floor principle into G9's sole B14 controller (not G67 player loop).
 * Broadphase first, double-winding barycentric compatible. */
int b24_g74_near_original_floor(const B24C1OriginalCollision *c,
 float x,float y,float feet_z,float *floor_z){
 if(!c||!c->ready||!floor_z||
    !good(x)||!good(y)||!good(feet_z))return 0;
 float best=-100000.f;
 int found=0;
 for(uint32_t i=0;i<c->count;i++){
  const B24C1OriginalCollisionFace *t=&c->faces[i];
  if(t->wall||x<t->minx-.0001f||x>t->maxx+.0001f||
     y<t->miny-.0001f||y>t->maxy+.0001f||
     t->minz>feet_z+.45f||t->maxz<feet_z-.5f)continue;
  const float *p=t->xyz;
  float bx=p[3]-p[0],by=p[4]-p[1];
  float cx=p[6]-p[0],cy=p[7]-p[1];
  float det=bx*cy-by*cx;
  if(fabsf(det)<1e-7f)continue;
  float dx=x-p[0],dy=y-p[1];
  float u=(dx*cy-dy*cx)/det;
  float v=(bx*dy-by*dx)/det;
  if(u<-.0002f||v<-.0002f||u+v>1.0002f)continue;
  float h=p[2]+u*(p[5]-p[2])+v*(p[8]-p[2]);
  if(!good(h)||h>feet_z+.45f||h<feet_z-.5f)continue;
  if(!found||h>best){best=h;found=1;}
 }
 if(found)*floor_z=best;
 return found;
}
