#include "b24_c1_material_source.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
_Static_assert(sizeof(B24C1MatMesh)==20,"C1MA 5x uint32 mesh ABI drift");
static uint32_t rd32(const unsigned char *p){
 return (uint32_t)p[0]|(uint32_t)p[1]<<8|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24;
}
static uint16_t rd16(const unsigned char *p){
 return (uint16_t)((unsigned)p[0]|((unsigned)p[1]<<8));
}
void b24_c1_material_source_free(B24C1MaterialSource *s){
 if(!s)return;
 if(s->labels){
  for(uint32_t i=0;i<s->nmaterials;i++)free(s->labels[i]);
 }
 free(s->labels);free(s->triangle_material);
 memset(s,0,sizeof(*s));
}
const char *b24_c1_material_label(const B24C1MaterialSource *s,uint16_t id){
 if(!s||!s->loaded||!s->labels||id>=s->nmaterials)return NULL;
 return s->labels[id];
}
int b24_c1_material_source_load(B24C1MaterialSource *dest,const char *path){
 if(!dest||!path)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 int good=1;
 unsigned char header[28]={0};
 if(fread(header,1,sizeof(header),f)!=sizeof(header))good=0;
 uint32_t mats=0,dictbytes=0;
 if(good){
  mats=rd32(header+20);dictbytes=rd32(header+24);
  if(memcmp(header,"C1MA",4)!=0||rd32(header+4)!=1u||
     rd32(header+8)!=B24_C1_MAT_NVERT||
     rd32(header+12)!=B24_C1_MAT_NTRI||
     rd32(header+16)!=B24_C1_MAT_NMESH||
     mats!=B24_C1_MAT_NLABEL||dictbytes<2u*mats||
     dictbytes>32768u)good=0;
 }
 const size_t minsize=28u+B24_C1_MAT_NMESH*20u+B24_C1_MAT_NTRI*2u;
 if(good&&fseek(f,0,SEEK_END)!=0)good=0;
 long len=good?ftell(f):-1;
 if(len<0||(size_t)len!=minsize+dictbytes||
    (good&&fseek(f,28,SEEK_SET)!=0))good=0;
 B24C1MaterialSource s={0};
 if(good){
  uint32_t prev_v=0,prev_t=0,prev_group=0;
  for(unsigned i=0;i<B24_C1_MAT_NMESH;i++){
   unsigned char b[20];
   if(fread(b,1,sizeof(b),f)!=sizeof(b)){good=0;break;}
   B24C1MatMesh m={rd32(b),rd32(b+4),rd32(b+8),rd32(b+12),rd32(b+16)};
   if(m.group>3u||m.group<prev_group||m.first_vertex!=prev_v||
      m.first_triangle!=prev_t||!m.vertex_count||!m.triangle_count||
      m.vertex_count>B24_C1_MAT_NVERT-prev_v||
      m.triangle_count>B24_C1_MAT_NTRI-prev_t){good=0;break;}
   s.meshes[i]=m;
   prev_v+=m.vertex_count;prev_t+=m.triangle_count;
   prev_group=m.group;
  }
  if(prev_v!=B24_C1_MAT_NVERT||prev_t!=B24_C1_MAT_NTRI)good=0;
 }
 if(good){
  s.triangle_material=malloc(B24_C1_MAT_NTRI*sizeof(*s.triangle_material));
  if(!s.triangle_material)good=0;
 }
 if(good){
  unsigned char buf[2];
  for(size_t i=0;i<B24_C1_MAT_NTRI;i++){
   if(fread(buf,1,2,f)!=2){good=0;break;}
   uint16_t mat=rd16(buf);
   if(mat>=mats){good=0;break;}
   s.triangle_material[i]=mat;
  }
 }
 if(good){
  s.labels=calloc(mats,sizeof(char*));
  if(!s.labels)good=0;
  else s.nmaterials=mats;
 }
 if(good){
  uint32_t consumed=0;
  for(uint32_t i=0;i<mats;i++){
   unsigned char length[2];
   if(fread(length,1,2,f)!=2){good=0;break;}
   uint16_t n=rd16(length);
   consumed+=2u;
   if(n==0||n>255||consumed+n>dictbytes){good=0;break;}
   char *label=malloc(n+1u);
   if(!label){good=0;break;}
   s.labels[i]=label;
   if(fread(label,1,n,f)!=n){good=0;break;}
   label[n]='\0';
   consumed+=n;
   /* Original file-qualified source identity MUST NOT be a mere texture
      alias. All known 10 genuine input BDAEs are C1L1_ files. */
   if(strncmp(label,"C1L1_",5)!=0||!strstr(label,".bdae:")){good=0;break;}
   for(uint32_t j=0;j<i;j++)if(strcmp(s.labels[j],label)==0){good=0;break;}
   if(!good)break;
  }
  if(consumed!=dictbytes)good=0;
 }
 fclose(f);
 if(!good){b24_c1_material_source_free(&s);return 0;}
 s.loaded=1;s.material_bytes=dictbytes;
 b24_c1_material_source_free(dest);
 *dest=s;return 1;
}
