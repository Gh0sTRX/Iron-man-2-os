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
