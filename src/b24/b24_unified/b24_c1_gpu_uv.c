#include "b24_c1_gpu_uv.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
_Static_assert(sizeof(B24C1UVPair)==8,"C1UV float UV layout");
static uint32_t little(const unsigned char *p){
 return (uint32_t)p[0]|(uint32_t)p[1]<<8|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
void b24_c1_uv_free(B24C1UV *dest){
 if(!dest)return;
 free(dest->uv);memset(dest,0,sizeof(*dest));
}
int b24_c1_uv_load(B24C1UV *dst,const char *path){
 if(!dst||!path)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 int good=1;
 const size_t len=16u+B24_C1_UV_MESHES+B24_C1_UV_VERTS*8u;
 if(fseek(f,0,SEEK_END))good=0;
 const long filelen=good?ftell(f):-1;
 if(filelen<0||(size_t)filelen!=len||fseek(f,0,SEEK_SET))good=0;
 unsigned char hdr[16]={0};
 if(good&&fread(hdr,1,16,f)!=16)good=0;
 if(good&&(memcmp(hdr,"C1UV",4)!=0||little(hdr+4)!=1u||
             little(hdr+8)!=B24_C1_UV_VERTS||
             little(hdr+12)!=B24_C1_UV_MESHES))good=0;
 B24C1UV tmp={0};
 if(good&&fread(tmp.flags,1,B24_C1_UV_MESHES,f)!=B24_C1_UV_MESHES)good=0;
 if(good){
  tmp.uv=malloc(B24_C1_UV_VERTS*sizeof(*tmp.uv));
  if(!tmp.uv)good=0;
 }
 if(good&&fread(tmp.uv,sizeof(*tmp.uv),B24_C1_UV_VERTS,f)!=B24_C1_UV_VERTS)
  good=0;
 fclose(f);
 if(good){
  for(unsigned i=0;i<B24_C1_UV_MESHES;i++){
   if(tmp.flags[i]>1u){good=0;break;}
   tmp.recognized_uv_meshes+=tmp.flags[i];
  }
  if(tmp.recognized_uv_meshes!=169u)good=0;
  for(size_t i=0;i<B24_C1_UV_VERTS&&good;i++){
   float u=tmp.uv[i].u,v=tmp.uv[i].v;
   if(!isfinite(u)||!isfinite(v)||fabsf(u)>500.f||fabsf(v)>500.f)
    good=0;
  }
 }
 if(!good){b24_c1_uv_free(&tmp);return 0;}
 tmp.loaded=1;tmp.nverts=B24_C1_UV_VERTS;tmp.nmeshes=B24_C1_UV_MESHES;
 b24_c1_uv_free(dst);*dst=tmp;return 1;
}
