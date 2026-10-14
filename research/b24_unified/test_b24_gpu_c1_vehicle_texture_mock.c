#include "b24_gpu_c1_vehicle_texture.h"
#include <vitaGL.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned gens=0,uploads=0,deletes=0;
void glGenTextures(GLsizei n,GLuint *out){
 assert(n==1&&out);*out=91;gens++;
}
void glBindTexture(GLenum target,GLuint id){assert(target==GL_TEXTURE_2D&&id==91);}
void glTexParameteri(GLenum t,GLenum pname,int value){
 assert(t==GL_TEXTURE_2D);
 assert(pname==GL_TEXTURE_WRAP_S||pname==GL_TEXTURE_WRAP_T||
        pname==GL_TEXTURE_MIN_FILTER||pname==GL_TEXTURE_MAG_FILTER);
 assert(value==GL_LINEAR||value==GL_CLAMP_TO_EDGE);
}
void glTexImage2D(GLenum t,int level,int format,GLsizei w,GLsizei h,
 int border,GLenum src,GLenum type,const void *pixels){
 assert(t==GL_TEXTURE_2D&&level==0&&format==GL_RGBA);
 assert(w==512&&h==512&&border==0&&src==GL_RGBA&&type==GL_UNSIGNED_BYTE);
 assert(pixels);
 const unsigned char *x=pixels;
 assert(x[0]==0x12 && x[512u*512u*4u-1u]==0x12);
 uploads++;
}
void glDeleteTextures(GLsizei count,const GLuint *ids){
 assert(count==1&&ids&&*ids==91);deletes++;
}
static void write_fixture(int kind){
 FILE *f=fopen("/tmp/IM2_original_vehicle_test.c1tx","wb");assert(f);
 unsigned char hdr[20]={'C','1','T','X',1,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0};
 if(kind==1)hdr[0]='Z';
 if(kind==2)hdr[8]=0;
 if(kind==3)hdr[16]=4;
 assert(fwrite(hdr,1,sizeof hdr,f)==sizeof hdr);
 size_t n=512u*512u*4u;
 if(kind==4)n--;
 unsigned char *rgba=malloc(n);assert(rgba);
 memset(rgba,0x12,n);
 assert(fwrite(rgba,1,n,f)==n);
 free(rgba);fclose(f);
}
int main(void){
 uint32_t texture=0u;
 assert(!b24_gpu_c1_vehicle_atlas_open(&texture,"/tmp/does-not-exist.c1tx"));
 for(int i=1;i<=4;i++){
  write_fixture(i);
  assert(!b24_gpu_c1_vehicle_atlas_open(&texture,"/tmp/IM2_original_vehicle_test.c1tx"));
  assert(!texture&&!gens&&!uploads);
 }
 write_fixture(0);
 assert(b24_gpu_c1_vehicle_atlas_open(&texture,"/tmp/IM2_original_vehicle_test.c1tx"));
 assert(texture==91u&&gens==1&&uploads==1);
 assert(!b24_gpu_c1_vehicle_atlas_open(&texture,"/tmp/IM2_original_vehicle_test.c1tx"));
 assert(uploads==1);
 b24_gpu_c1_vehicle_atlas_close(&texture);
 assert(texture==0&&deletes==1);
 b24_gpu_c1_vehicle_atlas_close(&texture);
 assert(deletes==1);
 remove("/tmp/IM2_original_vehicle_test.c1tx");
 puts("PASS B24 original vehicle GPU atlas 512x512: uploaded exactly once; corrupt magic/dims/flip and truncated files rejected; no VPK");
}
