#include "b24_gpu_c1_vehicle_texture.h"
#include <vitaGL.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t rd32(const unsigned char *p){
 return (uint32_t)p[0]|(uint32_t)p[1]<<8|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
int b24_gpu_c1_vehicle_atlas_open(uint32_t *id,const char *path){
 if(!id||*id||!path)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 const size_t atlas_bytes=512u*512u*4u;
 const size_t file_bytes=20u+atlas_bytes;
 int ok=fseek(f,0,SEEK_END)==0;
 long length=ok?ftell(f):-1;
 if(length<0||(size_t)length!=file_bytes||fseek(f,0,SEEK_SET))ok=0;
 unsigned char h[20]={0};
 if(ok&&fread(h,1,sizeof(h),f)!=sizeof(h))ok=0;
 if(ok&&(memcmp(h,"C1TX",4)!=0||rd32(h+4)!=1||
         rd32(h+8)!=512||rd32(h+12)!=512||rd32(h+16)>1))ok=0;
 unsigned char *pixels=NULL;
 if(ok){pixels=malloc(atlas_bytes);if(!pixels)ok=0;}
 if(ok&&fread(pixels,1,atlas_bytes,f)!=atlas_bytes)ok=0;
 fclose(f);
 if(!ok){free(pixels);return 0;}
 GLuint gltex=0;
 glGenTextures(1,&gltex);
 if(!gltex){free(pixels);return 0;}
 glBindTexture(GL_TEXTURE_2D,gltex);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
 glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,512,512,0,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
 free(pixels);
 *id=(uint32_t)gltex;
 return 1;
}
void b24_gpu_c1_vehicle_atlas_close(uint32_t *id){
 if(!id||!*id)return;
 GLuint gltex=(GLuint)*id;
 glDeleteTextures(1,&gltex);
 *id=0;
}
