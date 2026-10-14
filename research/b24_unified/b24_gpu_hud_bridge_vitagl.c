#include "b24_gpu_hud_bridge.h"
#include <vitaGL.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
enum { HW=480,HH=272,TW=512,TH=512 };
typedef struct {float x,y,u,v;} HUDV;
static const HUDV quad[4]={
 {0,0,0,0},{480,0,480.f/512.f,0},
 {480,272,480.f/512.f,272.f/512.f},{0,272,0,272.f/512.f}
};
static const uint16_t indices[6]={0,1,2,0,2,3};
int b24_gpu_hud_bridge_prepare(B24GpuHudBridge *h){
 if(!h||h->prepared)return 0;
 uint32_t *canvas=calloc((size_t)HW*HH,sizeof(uint32_t));
 unsigned char *rgba=malloc((size_t)HW*HH*4);
 if(!canvas||!rgba){free(canvas);free(rgba);return 0;}
 GLuint tex=0;glGenTextures(1,&tex);
 if(!tex){free(canvas);free(rgba);return 0;}
 glBindTexture(GL_TEXTURE_2D,tex);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
 glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,TW,TH,0,GL_RGBA,GL_UNSIGNED_BYTE,NULL);
 h->texture=(uint32_t)tex;h->rgb_canvas=canvas;h->rgba_canvas=rgba;
 h->prepared=1;h->frames=0;h->texture_uploads=0;
 return 1;
}
int b24_gpu_hud_bridge_draw(B24GpuHudBridge *h,B24Unified *game){
 if(!h||!h->prepared||!h->rgb_canvas||!h->rgba_canvas||!game)return 0;
 memset(h->rgb_canvas,0,(size_t)HW*HH*4);
 b24_unified_draw_overlay(game,h->rgb_canvas,HW);
 for(size_t i=0;i<(size_t)HW*HH;i++){
   uint32_t c=h->rgb_canvas[i];
   unsigned char *p=h->rgba_canvas+i*4;
   p[0]=(unsigned char)(c>>16);p[1]=(unsigned char)(c>>8);
   p[2]=(unsigned char)c;p[3]=(unsigned char)((c&0xffffffu)?255u:0u);
 }
 glMatrixMode(GL_PROJECTION);glPushMatrix();glLoadIdentity();
 glOrthof(0.f,(float)HW,(float)HH,0.f,-1.f,1.f);
 glMatrixMode(GL_MODELVIEW);glPushMatrix();glLoadIdentity();
 glDisable(GL_DEPTH_TEST);glDepthMask(GL_FALSE);
 glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
 glEnable(GL_TEXTURE_2D);
 glBindTexture(GL_TEXTURE_2D,(GLuint)h->texture);
 glTexSubImage2D(GL_TEXTURE_2D,0,0,0,HW,HH,GL_RGBA,GL_UNSIGNED_BYTE,h->rgba_canvas);
 glColor4f(1.f,1.f,1.f,1.f);
 glEnableClientState(GL_VERTEX_ARRAY);
 glEnableClientState(GL_TEXTURE_COORD_ARRAY);
 glVertexPointer(2,GL_FLOAT,sizeof(HUDV),&quad[0].x);
 glTexCoordPointer(2,GL_FLOAT,sizeof(HUDV),&quad[0].u);
 glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_SHORT,indices);
 glDisableClientState(GL_TEXTURE_COORD_ARRAY);glDisableClientState(GL_VERTEX_ARRAY);
 glDisable(GL_TEXTURE_2D);glDisable(GL_BLEND);
 glDepthMask(GL_TRUE);glEnable(GL_DEPTH_TEST);
 glPopMatrix();glMatrixMode(GL_PROJECTION);glPopMatrix();
 glMatrixMode(GL_MODELVIEW);
 h->texture_uploads++;h->frames++;
 return 1;
}
void b24_gpu_hud_bridge_release(B24GpuHudBridge *h){
 if(!h)return;
 if(h->prepared){GLuint tex=(GLuint)h->texture;glDeleteTextures(1,&tex);}
 free(h->rgb_canvas);free(h->rgba_canvas);
 memset(h,0,sizeof(*h));
}
