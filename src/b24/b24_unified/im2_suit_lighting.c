#include "im2_suit_lighting.h"
#include "b24_g75_original_sun_lighting_candidate.h"
#include <math.h>
#include <string.h>
int im2_suit_lighting_colors(const B24GpuSuitSource *s,const float root[16],
                            float *normals,unsigned char *rgba,size_t capacity){
 if(!s||!root||!normals||!rgba||!s->vertices||!s->triangles||
    !s->nv||s->nv>16000||!s->nt||s->nt>24000||capacity<s->nv)return 0;
 for(unsigned k=0;k<16;k++)if(!isfinite(root[k]))return 0;
 for(unsigned i=0;i<s->nv;i++){
  const B24GpuSuitVertex *v=s->vertices+i;
  if(!isfinite(v->x)||!isfinite(v->y)||!isfinite(v->z))return 0;
 }
 for(unsigned i=0;i<s->nt;i++){
  const B24GpuSuitTriangle *t=s->triangles+i;
  if(t->i0>=s->nv||t->i1>=s->nv||t->i2>=s->nv)return 0;
 }
 memset(normals,0,s->nv*3*sizeof(float));
 for(unsigned i=0;i<s->nt;i++){
  const B24GpuSuitTriangle *t=s->triangles+i;
  const B24GpuSuitVertex *a=s->vertices+t->i0,*b=s->vertices+t->i1,*c=s->vertices+t->i2;
  const float ux=b->x-a->x,uy=b->y-a->y,uz=b->z-a->z;
  const float vx=c->x-a->x,vy=c->y-a->y,vz=c->z-a->z;
  const float normal[]={uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx};
  if(!isfinite(normal[0])||!isfinite(normal[1])||!isfinite(normal[2]))continue;
  const unsigned indices[]={t->i0,t->i1,t->i2};
  for(unsigned j=0;j<3;j++)for(unsigned k=0;k<3;k++)normals[indices[j]*3+k]+=normal[k];
 }
 for(unsigned i=0;i<s->nv;i++){
  const B24GpuSuitVertex *v=s->vertices+i;const float *n=normals+i*3;
  const B24G75Vec world={root[0]*v->x+root[4]*v->y+root[8]*v->z+root[12],
    root[1]*v->x+root[5]*v->y+root[9]*v->z+root[13],root[2]*v->x+root[6]*v->y+root[10]*v->z+root[14]};
  const B24G75Vec normal={root[0]*n[0]+root[4]*n[1]+root[8]*n[2],
    root[1]*n[0]+root[5]*n[1]+root[9]*n[2],root[2]*n[0]+root[6]*n[1]+root[10]*n[2]};
  const float factor=fminf(1.f,fmaxf(0.f,b24_g75_light_factor(world,normal)));
  const unsigned char value=(unsigned char)(factor*255.f+.5f);
  rgba[i*4]=rgba[i*4+1]=rgba[i*4+2]=value;rgba[i*4+3]=255;
 }
 return 1;
}
