#include "b24_g159_real_source_road.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* G159 REAL road-only original G66M geometry. Source batch 12 is 2010
 * c1l1_road.tga by exact decoded original RGBA byte identity.
 * It is intentionally NOT a source iOS physics-solidness proof. */
static int g159_good_float(float x){return isg159_good_float(x)&&fabsf(x)<100000.f;}
static int tri_z(const B24G159RoadFace *t,float x,float y,float *z){
 if(x<t->minx-.0001f||x>t->maxx+.0001f||
    y<t->miny-.0001f||y>t->maxy+.0001f)return 0;
 const float *p=t->p;
 const float ax=p[3]-p[0],ay=p[4]-p[1];
 const float bx=p[6]-p[0],by=p[7]-p[1];
 const float det=ax*by-ay*bx;
 if(fabsf(det)<1.e-8f)return 0;
 const float dx=x-p[0],dy=y-p[1];
 const float a=(dx*by-dy*bx)/det,b=(ax*dy-ay*dx)/det;
 if(a<-.0002f||b<-.0002f||a+b>1.0002f)return 0;
 *z=p[2]+a*(p[5]-p[2])+b*(p[8]-p[2]);
 return g159_good_float(*z);
}
void b24_g159_road_close(B24G159Road *r){
 if(!r)return;
 free(r->faces);
 memset(r,0,sizeof(*r));
}
int b24_g159_road_open(B24G159Road *r,const char *path){
 if(!r||r->ready||r->faces||!path)return 0;
 FILE *f=fopen(path,"rb");
 if(!f)return 0;
 char magic[4];uint32_t h[4],batch[32][4];B24G159Road tmp={0};
 if(fread(magic,1,4,f)!=4||memcmp(magic,"G66M",4)||
    fread(h,4,4,f)!=4||h[0]!=1||h[1]!=67323||
    h[2]!=32||h[3]!=31||
    fread(batch,16,32,f)!=32){fclose(f);return 0;}
 uint32_t total=0;
 for(unsigned i=0;i<32;i++){
  if(batch[i][0]!=total||!batch[i][1]||batch[i][1]%3||
     batch[i][1]>67323-total||
     (batch[i][2]!=UINT32_MAX&&batch[i][2]>=31)){
    fclose(f);return 0;
  }
  total+=batch[i][1];
 }
 if(total!=67323||batch[12][2]!=12u||
    batch[12][1]>12000u){fclose(f);return 0;}
 /* Up to 4,000 triangles only; bound one-time RAM and per-step CPU.
  * Preserve all original batch triangle source coordinates exactly. */
 const uint32_t capacity=batch[12][1]/3u;
 if(!capacity){fclose(f);return 0;}
 tmp.faces=calloc(capacity,sizeof(*tmp.faces));
 if(!tmp.faces){fclose(f);return 0;}
 if(fseek(f,532L+(long)batch[12][0]*24L,SEEK_SET)){
  fclose(f);b24_g159_road_close(&tmp);return 0;
 }
 for(uint32_t i=0;i<capacity;i++){
  B24G159RoadFace src={0};
  for(int k=0;k<3;k++){
   float vertex[5];unsigned char rgba[4];
   if(fread(vertex,4,5,f)!=5||fread(rgba,1,4,f)!=4){
    fclose(f);b24_g159_road_close(&tmp);return 0;
   }
   for(int j=0;j<3;j++){
    if(!g159_good_float(vertex[j])){
     fclose(f);b24_g159_road_close(&tmp);return 0;
    }
    src.p[3*k+j]=vertex[j];
   }
  }
  src.minx=src.maxx=src.p[0];
  src.miny=src.maxy=src.p[1];
  src.minz=src.maxz=src.p[2];
  for(unsigned k=1;k<3;k++){
   float x=src.p[3*k],y=src.p[3*k+1],z=src.p[3*k+2];
   if(x<src.minx)src.minx=x;
   if(x>src.maxx)src.maxx=x;
   if(y<src.miny)src.miny=y;
   if(y>src.maxy)src.maxy=y;
   if(z<src.minz)src.minz=z;
   if(z>src.maxz)src.maxz=z;
  }
  /* Original drawing material "road" is a *candidate*, only triangles
   * with real projected XY area can provide stable authored-Z support.
   * No artificial collision planes, boxes or heights are generated. */
  float a=src.p[3]-src.p[0],b=src.p[4]-src.p[1];
  float c=src.p[6]-src.p[0],d=src.p[7]-src.p[1];
  if(fabsf(a*d-b*c)<1.e-8f)continue;
  tmp.faces[tmp.count++]=src;
 }
 fclose(f);
 if(!tmp.count){b24_g159_road_close(&tmp);return 0;}
 tmp.ready=1;
 *r=tmp;
 return 1;
}
int b24_g159_road_near(const B24G159Road *r,float x,float y,
 float footz,float *support){
 if(!r||!r->ready||!support||!g159_good_float(x)||!g159_good_float(y)||
    !g159_good_float(footz))return 0;
 int found=0;float best=-100000.f;
 for(uint32_t i=0;i<r->count;i++){
  const B24G159RoadFace *f=&r->faces[i];
  if(f->minz>footz+.45f||f->maxz<footz-.5f)continue;
  float z;
  if(!tri_z(f,x,y,&z)||z>footz+.45f||z<footz-.5f)continue;
  if(!found||z>best){found=1;best=z;}
 }
 if(found)*support=best;
 return found;
}
int b24_g159_road_crossed(const B24G159Road *r,float x,float y,
 float oldz,float newz,float *support){
 if(!r||!r->ready||!support||!g159_good_float(x)||!g159_good_float(y)||
    !g159_good_float(oldz)||!g159_good_float(newz)||newz>oldz+.05f)return 0;
 int found=0;float best=-100000.f;
 for(uint32_t i=0;i<r->count;i++){
  const B24G159RoadFace *f=&r->faces[i];
  if(f->minz>oldz+.08f||f->maxz<newz-.08f)continue;
  float z;
  if(!tri_z(f,x,y,&z)||z>oldz+.08f||z<newz-.08f)continue;
  if(!found||z>best){found=1;best=z;}
 }
 if(found)*support=best;
 return found;
}
