/*
 * Iron Man 2 - C1L1 native PS Vita stand-alone MAP VIEWER M1.
 * User-authorized HARDWARE TEST. No gameplay/HUD/player, does not alter old B24.
 * Uses ORIGINAL 2010 source C1G2/C1UV/C1MA/C1MT/C1TX assets.
 * Only experimental orbit/free-look camera, no claimed original 2010 camera.
 */
#include <psp2/ctrl.h>
#include <psp2/kernel/threadmgr.h>
#include <psp2/kernel/processmgr.h>
#include <vitaGL.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "b24_c1_gpu_mesh.h"
#include "b24_c1_gpu_uv.h"
#include "b24_c1_material_source.h"
#include "b24_c1_material_batches.h"
#include "b24_c1_2010_diffuse_bank.h"
#include "b24_gpu_c1_2010_diffuse_upload.h"
#include "b24_gpu_c1_2010_textured_material.h"
#include "b24_gpu_camera.h"

#define M_PI_F 3.14159265358979323846f
#define VW 960
#define VH 544
typedef struct {
 B24GpuC1Mesh world;
 B24C1UV uv;
 B24C1MaterialSource mats;
 B24C1MaterialBatchPlan draws;
 B24C1OriginalDiffuseBank textures;
 int mesh_ok, uv_ok, mat_ok, buckets_ok, bank_ok, tex_uploaded;
 int use_source_textures, focus, hud, stage;
 float yaw, pitch, range, px,py,pz;
 unsigned long frames;
} Viewer;
static Viewer v;
static const float focus_points[3][3]={{-1.319f,-6.747f,25.054f},
 {-402.2025f,-279.047f,0.f},{0.f,0.f,10.f}};
static const float focus_dist[3]={115.f,2200.f,270.f};

static unsigned char pix[20000*2];
static float hudverts[20000*2];
static unsigned npix;
static const unsigned char *glyph(char c) {
 /* 5x7 pixel font, compact and standalone. */
 static const unsigned char data[40][7]={
 {14,17,17,31,17,17,17}, /* A */
 {30,17,17,30,17,17,30}, /* B */
 {15,16,16,16,16,16,15}, /* C */
 {30,17,17,17,17,17,30}, /* D */
 {31,16,16,30,16,16,31}, /* E */
 {31,16,16,30,16,16,16}, /* F */
 {15,16,16,19,17,17,15}, /* G */
 {17,17,17,31,17,17,17}, /* H */
 {31,4,4,4,4,4,31}, /* I */
 {7,2,2,2,18,18,12}, /* J */
 {17,18,20,24,20,18,17}, /* K */
 {16,16,16,16,16,16,31}, /* L */
 {17,27,21,21,17,17,17}, /* M */
 {17,25,21,19,17,17,17}, /* N */
 {14,17,17,17,17,17,14}, /* O */
 {30,17,17,30,16,16,16}, /* P */
 {14,17,17,17,21,18,13}, /* Q */
 {30,17,17,30,20,18,17}, /* R */
 {15,16,16,14,1,1,30}, /* S */
 {31,4,4,4,4,4,4}, /* T */
 {17,17,17,17,17,17,14}, /* U */
 {17,17,17,17,17,10,4}, /* V */
 {17,17,17,21,21,21,10}, /* W */
 {17,17,10,4,10,17,17}, /* X */
 {17,17,10,4,4,4,4}, /* Y */
 {31,1,2,4,8,16,31}, /* Z */
 {14,17,19,21,25,17,14}, /* 0 */
 {4,12,4,4,4,4,14}, /* 1 */
 {14,17,1,2,4,8,31}, /* 2 */
 {30,1,1,14,1,1,30}, /* 3 */
 {2,6,10,18,31,2,2}, /* 4 */
 {31,16,30,1,1,17,14}, /* 5 */
 {7,8,16,30,17,17,14}, /* 6 */
 {31,1,2,4,8,8,8}, /* 7 */
 {14,17,17,14,17,17,14}, /* 8 */
 {14,17,17,15,1,2,28}, /* 9 */
 {0,4,4,0,4,4,0}, /* : */
 {0,0,0,31,0,0,0}, /* - */
 {0,0,0,0,0,0,0}  /* space */
 };
 if(c>='a'&&c<='z')c-=32;
 if(c>='A'&&c<='Z')return data+(c-'A')*7;
 if(c>='0'&&c<='9')return data+(26+c-'0')*7;
 if(c==':')return data+36*7;
 if(c=='-')return data+37*7;
 return data+38*7;
}
static void add_text(int x,int y,const char *str){
 for(int n=0;str[n]&&n<140;n++,x+=14){
  const unsigned char *g=glyph(str[n]);
  for(int row=0;row<7;row++)for(int col=0;col<5;col++){
   if(!(g[row]&(1<<(4-col)))||npix+4>=20000)continue;
   for(int yy=0;yy<2;yy++)for(int xx=0;xx<2;xx++){
    hudverts[npix*2]=(float)(x+col*2+xx);
    hudverts[npix*2+1]=(float)(VH-(y+row*2+yy));
    npix++;
   }
  }
 }
}
static void draw_ui(void){
 if(!v.hud)return;
 npix=0;
 add_text(18,20,"IRON MAN 2 C1L1 MAP VIEWER M1");
 add_text(18,43,"TRI OVERVIEW   SQUARE MC   CIRCLE CITY");
 add_text(18,65,"LEFT MOVE   RIGHT LOOK   L R ZOOM");
 add_text(18,87,"SELECT DIFFUSE MODE  START HUD");
 if(!v.mesh_ok)add_text(18,130,"ERROR SOURCE C1G2 NOT LOADED");
 else if(!v.uv_ok||!v.mat_ok||!v.buckets_ok)add_text(18,130,"WARN ORIGINAL MAP MATERIAL DATA MISSING");
 else if(!v.bank_ok||!v.tex_uploaded)add_text(18,130,"WARN SOURCE PVR IMAGE BANK MISSING");
 else add_text(18,130,v.use_source_textures?"MODE ORIGINAL SOURCE PVR":"MODE SOURCE VERTEX COLORS");
 add_text(18,150,v.focus==0?"FOCUS MAIN CHARACTER":v.focus==1?"FOCUS ALL ORIGINAL WORLD":"FOCUS CITY AREA");
 add_text(18,171,"370 MESH  22919 TRIANGLES  SOURCE 2010");
 glDisable(GL_TEXTURE_2D);
 glDisable(GL_DEPTH_TEST);
 glMatrixMode(GL_PROJECTION);glPushMatrix();glLoadIdentity();
 glOrthof(0.f,(float)VW,0.f,(float)VH,-1.f,1.f);
 glMatrixMode(GL_MODELVIEW);glPushMatrix();glLoadIdentity();
 glDisableClientState(GL_COLOR_ARRAY);glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glEnableClientState(GL_VERTEX_ARRAY);glColor4f(1.f,.92f,.69f,1.f);
 glPointSize(2.5f);glVertexPointer(2,GL_FLOAT,0,hudverts);
 glDrawArrays(GL_POINTS,0,(GLsizei)npix);glDisableClientState(GL_VERTEX_ARRAY);
 glMatrixMode(GL_MODELVIEW);glPopMatrix();
 glMatrixMode(GL_PROJECTION);glPopMatrix();
 glMatrixMode(GL_MODELVIEW);glEnable(GL_DEPTH_TEST);
}
static int deadzone(unsigned char b){
 int x=(int)b-127;
 return (x>-15&&x<15)?0:x;
}
static void reset_focus(int idx){
 v.focus=idx;v.px=focus_points[idx][0];v.py=focus_points[idx][1];v.pz=focus_points[idx][2];
 v.range=focus_dist[idx];v.yaw=-1.15f;v.pitch=.53f;
}
static void poll_inputs(void){
 SceCtrlData p={0};
 if(sceCtrlPeekBufferPositive(0,&p,1)!=1)return;
 static unsigned prev;
 unsigned pressed=p.buttons&~prev;prev=p.buttons;
 if(pressed&SCE_CTRL_TRIANGLE)reset_focus(1);
 if(pressed&SCE_CTRL_SQUARE)reset_focus(0);
 if(pressed&SCE_CTRL_CIRCLE)reset_focus(2);
 if(pressed&SCE_CTRL_SELECT)v.use_source_textures=!v.use_source_textures;
 if(pressed&SCE_CTRL_START)v.hud=!v.hud;
 /* Right stick look, left stick planar pan in orbit's local XY frame. */
 float x=deadzone(p.lx)/128.f,y=-deadzone(p.ly)/128.f;
 float rx=deadzone(p.rx)/128.f,ry=deadzone(p.ry)/128.f;
 v.yaw+=rx*.038f;v.pitch-=ry*.025f;
 if(v.pitch<-.2f)v.pitch=-.2f;if(v.pitch>1.48f)v.pitch=1.48f;
 float speed=fmaxf(0.12f,v.range*.008f);
 v.px+=(cosf(v.yaw)*x-sinf(v.yaw)*y)*speed;
 v.py+=(sinf(v.yaw)*x+cosf(v.yaw)*y)*speed;
 if(p.buttons&SCE_CTRL_UP)v.pz+=speed;
 if(p.buttons&SCE_CTRL_DOWN)v.pz-=speed;
 if(p.buttons&SCE_CTRL_LTRIGGER)v.range*=.978f;
 if(p.buttons&SCE_CTRL_RTRIGGER)v.range*=1.022f;
 if(v.range<5.f)v.range=5.f;
 if(v.range>3200.f)v.range=3200.f;
}
static void draw_world(void){
 if(!v.mesh_ok)return;
 B24GpuCamera cam={{v.px+v.range*cosf(v.pitch)*cosf(v.yaw),
                   v.py+v.range*cosf(v.pitch)*sinf(v.yaw),v.pz+v.range*sinf(v.pitch)},
                  {v.px,v.py,v.pz},{0,0,1},74.f,(float)VW/(float)VH,.18f,6200.f};
 B24GpuCameraMatrices m;
 if(!b24_gpu_camera_matrices(&cam,&m))return;
 glMatrixMode(GL_PROJECTION);glLoadMatrixf(m.projection);
 glMatrixMode(GL_MODELVIEW);glLoadMatrixf(m.view);
 glColor4f(1.f,1.f,1.f,1.f);
 if(v.use_source_textures&&v.tex_uploaded&&v.buckets_ok)
   (void)b24_gpu_c1_draw_original_2010_world(&v.world,&v.uv,&v.draws,&v.textures);
 else (void)b24_gpu_c1_draw_vitagl(&v.world);
}
static void open_original_map(void){
 v.mesh_ok=b24_gpu_c1_load(&v.world,"app0:maps/C1L1_environment.c1g2");
 if(!v.mesh_ok){v.stage=1;return;}
 v.uv_ok=b24_c1_uv_load(&v.uv,"app0:maps/C1L1_environment.c1uv");
 v.mat_ok=b24_c1_material_source_load(&v.mats,"app0:maps/C1L1_environment.c1ma");
 v.buckets_ok=v.mat_ok&&b24_c1_material_batches_build(&v.draws,&v.world,&v.mats);
 v.bank_ok=b24_c1_2010_diffuse_bank_load(&v.textures,"app0:maps/C1L1_environment.c1mt");
 if(v.uv_ok&&v.mat_ok&&v.buckets_ok&&v.bank_ok){
  v.tex_uploaded=b24_gpu_c1_2010_diffuse_upload(&v.textures,&v.draws,"app0:maps");
 }
 v.stage=2;
}
int main(void){
 memset(&v,0,sizeof(v));
 sceCtrlSetSamplingMode(SCE_CTRL_MODE_ANALOG);
 reset_focus(0);v.use_source_textures=1;v.hud=1;
 /* G3 hardware forensic: vitaGL returns GL_FALSE even on valid startup.
    Never interpret vglInit return value as a failure. */
 (void)vglInit(0x1800000);
 glViewport(0,0,VW,VH);
 glEnable(GL_DEPTH_TEST);glDepthFunc(GL_LESS);
 glDisable(GL_CULL_FACE);
 glClearColor(.025f,.055f,.085f,1.f);
 open_original_map();
 while(1){
  poll_inputs();
  glViewport(0,0,VW,VH);
  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
  draw_world();
  draw_ui();
  vglSwapBuffers(GL_FALSE);
  v.frames++;
  sceKernelDelayThread(7000);
 }
 return 0;
}
