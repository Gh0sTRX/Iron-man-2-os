#include "b24_gpu_c1_2010_diffuse_upload.h"
#include <vitaGL.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define GPU_MAX_ATLAS_DIM 512u
#define GPU_ATLAS_BUDGET (14u*1024u*1024u)
static unsigned get32(const unsigned char *p){
 return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;
}
static int read_original_C1TX(const char *path,unsigned char **pix,unsigned *w,unsigned *h){
 if(!path||!pix||!w||!h)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 int ok=1;
 unsigned char head[20]={0};
 if(fread(head,1,20,f)!=20)ok=0;
 unsigned width=ok?get32(head+8):0,height=ok?get32(head+12):0;
 if(ok&&(memcmp(head,"C1TX",4)!=0||get32(head+4)!=1u||
          width<8u||height<8u||width>2048u||height>2048u||
          (width&(width-1u))||(height&(height-1u))||
          get32(head+16)>1u))ok=0;
 size_t bytes=(size_t)width*height*4u;
 if(ok&&((size_t)width*height>4194304u||bytes>16777216u))ok=0;
 if(ok&&fseek(f,0,SEEK_END)!=0)ok=0;
 long sz=ok?ftell(f):-1;
 if(sz<0||(size_t)sz!=20u+bytes||fseek(f,20,SEEK_SET)!=0)ok=0;
 unsigned char *data=ok?malloc(bytes):NULL;
 if(ok&&!data)ok=0;
 if(ok&&fread(data,1,bytes,f)!=bytes)ok=0;
 fclose(f);
 if(!ok){free(data);return 0;}
 *w=width;*h=height;*pix=data;
 return 1;
}
static unsigned char *downsample_source_once(unsigned char *in,
                                              unsigned *w,unsigned *h){
 if(!in||!w||!h)return NULL;
 unsigned oldw=*w,oldh=*h,neww=oldw,newh=oldh;
 while(neww>GPU_MAX_ATLAS_DIM||newh>GPU_MAX_ATLAS_DIM){
  if(neww>1u)neww/=2u;
  if(newh>1u)newh/=2u;
 }
 if(neww==oldw&&newh==oldh)return in;
 size_t pixels=(size_t)neww*newh;
 unsigned char *small=malloc(pixels*4u);
 if(!small)return NULL;
 for(unsigned y=0;y<newh;y++){
  unsigned sy=(unsigned)(((unsigned long long)y*oldh)/newh);
  for(unsigned x=0;x<neww;x++){
   unsigned sx=(unsigned)(((unsigned long long)x*oldw)/neww);
   memcpy(small+4u*((size_t)y*neww+x),
          in+4u*((size_t)sy*oldw+sx),4u);
  }
 }
 free(in);*w=neww;*h=newh;
 return small;
}
void b24_gpu_c1_2010_diffuse_release(B24C1OriginalDiffuseBank *bank){
 if(!bank)return;
 for(unsigned i=0;i<B24_C1_2010_ATLASES;i++){
  if(bank->gl_texture_ids[i]){
   GLuint id=(GLuint)bank->gl_texture_ids[i];
   glDeleteTextures(1,&id);
   bank->gl_texture_ids[i]=0;
  }
 }
}
int b24_gpu_c1_2010_diffuse_upload(B24C1OriginalDiffuseBank *bank,
 const B24C1MaterialBatchPlan *plan,const char *base){
 if(!bank||!bank->loaded||!plan||!plan->ready||!base||!*base||
    !plan->indices||plan->index_count!=B24_GPU_C1_INDICES||
    bank->source_verified_count==0)return 0;
 unsigned char selected[B24_C1_2010_ATLASES]={0};
 for(unsigned i=0;i<plan->nbuckets;i++){
  const B24C1MaterialBucket *q=&plan->buckets[i];
  /* source lights with zero UV are intentionally left in diagnostic color
     until original 370 mesh-level UV flag partitions are source-proven. */
  if(q->group>=3u)continue;
  int id=b24_c1_2010_diffuse_bank_lookup(bank,q->material_id);
  if(id>=0)selected[id]=1;
 }
 unsigned budget=0,success=0;
 for(unsigned id=0;id<B24_C1_2010_ATLASES;id++){
  if(!selected[id])continue;
  char path[172];
  int written=snprintf(path,sizeof(path),"%s/%s",base,bank->names[id]);
  if(written<0||(size_t)written>=sizeof(path))continue;
  unsigned char *pixels=NULL;
  unsigned w=0,h=0;
  if(!read_original_C1TX(path,&pixels,&w,&h))continue;
  unsigned char *source=pixels;
  pixels=downsample_source_once(pixels,&w,&h);
  if(!pixels){free(source);continue;}
  unsigned bytes=w*h*4u;
  if(bytes>GPU_ATLAS_BUDGET-budget){free(pixels);continue;}
  GLuint tex=0;glGenTextures(1,&tex);
  if(!tex){free(pixels);continue;}
  glBindTexture(GL_TEXTURE_2D,tex);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
  const int vehicle=strcmp(bank->names[id],"c1l1_vehicles.c1tx")==0;
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,vehicle?GL_CLAMP_TO_EDGE:GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,vehicle?GL_CLAMP_TO_EDGE:GL_REPEAT);
  glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,(GLsizei)w,(GLsizei)h,
               0,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
  free(pixels);
  if(glGetError()!=GL_NO_ERROR){glDeleteTextures(1,&tex);continue;}
  bank->gl_texture_ids[id]=(uint32_t)tex;
  budget+=bytes;success++;
 }
 glBindTexture(GL_TEXTURE_2D,0);
 return success>0;
}
