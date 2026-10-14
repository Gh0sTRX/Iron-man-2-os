#include "b24_gpu_hud_native.h"
#include <vitaGL.h>
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static B24NativeHudGeometry g;
static B24Unified state;
static unsigned draw_calls=0,vertex_count=0,texture_updates=0;
static unsigned matrix_push=0,matrix_pop=0;
void glMatrixMode(GLenum x){assert(x==GL_PROJECTION||x==GL_MODELVIEW);}
void glPushMatrix(void){matrix_push++;}
void glPopMatrix(void){matrix_pop++;}
void glLoadIdentity(void){}
void glOrthof(float l,float r,float b,float t,float n,float f){
 assert(l==0&&r==480&&b==272&&t==0&&n==-1&&f==1);
}
void glEnable(GLenum x){assert(x==GL_DEPTH_TEST||x==GL_BLEND);}
void glDisable(GLenum x){assert(x==GL_DEPTH_TEST||x==GL_BLEND||x==GL_TEXTURE_2D);}
void glDepthMask(GLboolean x){assert(x==GL_TRUE||x==GL_FALSE);}
void glBlendFunc(GLenum a,GLenum b){
 assert(a==GL_SRC_ALPHA&&b==GL_ONE_MINUS_SRC_ALPHA);
}
void glEnableClientState(GLenum x){assert(x==GL_VERTEX_ARRAY||x==GL_COLOR_ARRAY);}
void glDisableClientState(GLenum x){assert(x==GL_VERTEX_ARRAY||x==GL_COLOR_ARRAY);}
void glVertexPointer(int n,GLenum mode,GLsizei size,const void *ptr){
 assert(n==2&&mode==GL_FLOAT&&size==sizeof(B24NativeHudVertex)&&ptr);
}
void glColorPointer(int n,GLenum mode,GLsizei size,const void *ptr){
 assert(n==4&&mode==GL_UNSIGNED_BYTE&&size==sizeof(B24NativeHudVertex)&&ptr);
}
void glDrawArrays(GLenum type,GLint first,GLsizei count){
 assert(type==GL_TRIANGLES&&first==0&&count>0&&count%6==0);
 draw_calls++;vertex_count+=(unsigned)count;
}
void glTexSubImage2D(GLenum t,GLint a,GLint b,GLint c,GLsizei d,GLsizei e,
 GLenum f,GLenum h,const void *pixels){
 (void)t;(void)a;(void)b;(void)c;(void)d;(void)e;
 (void)f;(void)h;(void)pixels;
 texture_updates++;
 assert(!"GPU-native B24 HUD must never upload bitmap textures");
}
/* The crosshair remains centered even when source camera shoulder/chase blends.
   These vertices come from four crosshair bars, not a screenshot guess. */
static int have_reticle_left_bar(void){
 for(unsigned i=0;i+5<g.count;i+=6u){
  const float x=g.vertices[i].x,y=g.vertices[i].y;
  if(fabsf(x-228.f)<.015f&&fabsf(y-135.35f)<.015f &&
     fabsf(g.vertices[i+1].x-236.f)<.015f)return 1;
 }
 return 0;
}
static void validate(void){
 assert(b24_native_hud_build(&g,&state));
 assert(!g.overflow);
 assert(g.count>=6u&&g.count<=B24_NATIVE_HUD_VERTICES);
 assert(g.count%6u==0&&g.quads==g.count/6u);
 for(unsigned i=0;i<g.count;i++){
  assert(isfinite(g.vertices[i].x)&&isfinite(g.vertices[i].y));
  assert(g.vertices[i].x>=-128.f&&g.vertices[i].x<=608.f); /* GPU clips offscreen missile brackets */
  assert(g.vertices[i].y>=-128.f&&g.vertices[i].y<=400.f); /* 2D viewport clip */
  assert((g.vertices[i].rgba&0xff000000u)==0xff000000u);
 }
 assert(b24_native_hud_draw(&g));
 assert(texture_updates==0);
 assert(matrix_push==matrix_pop);
}
int main(void){
 memset(&state,0,sizeof(state));
 state.hud.page=B22_GAME;
 state.hud.mode=B22_HYBRID;
 state.hud.suit=B22_IRONMAN;
 state.hud.armor=85.f;
 state.hud.energy=75.f;
 state.hud.charge=30.f;
 state.hud.show_objective=1;
 state.missile.weapon=B23_REPULSOR;
 state.missile.phase=B23_LOCKED; /* bug guard: non-missile -> NO LOCK */
 state.missile.lock_button_held=1;
 state.missile.target_id=4;
 state.camera_base.shoulder_to_chase=0.f;
 validate();
 assert(g.missile_brackets==0u);
 assert(g.reticle_quads==4u);
 assert(have_reticle_left_bar());
 state.camera_base.shoulder_to_chase=1.f;
 state.missile.weapon=B23_MISSILE;
 state.missile.target_x=240;state.missile.target_y=140;
 state.missile.target_health_percent=70;
 validate();
 assert(have_reticle_left_bar());
 assert(g.missile_brackets==16u);
 state.speed_fx.enabled=1;
 state.speed_fx.strength=1.f;
 state.speed_fx.ticks=9;
 validate();
 state.hud.page=B22_PAUSE;
 validate();
 assert(g.pause_glyph_quads>25u);
 assert(g.missile_brackets==0u);
 assert(g.reticle_quads==0u);
 state.controls.menu=IM2_MENUOPTIONS;
 state.controls.selected_option=IM2_SETTING_MUSIC;
 state.controls.settings.music=1;
 state.controls.settings.sfx=1;
 state.controls.settings.camera_sensitivity=1.f;
 validate();
 assert(g.pause_glyph_quads>50u);
 unsigned options_on=g.count;
 state.controls.selected_option=IM2_SETTING_SENSITIVITY;
 state.controls.settings.camera_sensitivity=1.5f;
 state.controls.settings.music=0;
 validate();
 assert(g.pause_glyph_quads>50u);
 assert(g.count!=options_on);
 state.controls.menu=IM2_MENUMAIN;
 uint32_t rng=0xA11CEu;
 for(int i=0;i<20000;i++){
  rng=rng*1664525u+1013904223u;
  state.hud.page=(rng&1u)?B22_GAME:B22_PAUSE;
  state.hud.mode=(B22UiMode)((rng>>2)%3u);
  state.hud.suit=(rng&16u)?B22_WARMACHINE:B22_IRONMAN;
  state.hud.ammo=(int)((rng>>5)%20u);
  state.hud.armor=(float)((rng>>9)%130u);
  state.missile.weapon=(B23Weapon)((rng>>12)%4u);
  state.missile.phase=(B23Phase)((rng>>14)%3u);
  state.missile.target_id=(int)((rng>>17)%12u);
  state.missile.target_x=(int)((rng>>2)%580u)-50;
  state.missile.target_y=(int)((rng>>5)%330u)-30;
  state.missile.target_health_percent=(float)((rng>>7)%120u);
  state.camera_base.shoulder_to_chase=(float)((rng>>11)%130u)/100.f;
  state.speed_fx.enabled=(int)((rng>>18)&1u);
  state.speed_fx.strength=(float)((rng>>20)%130u)/100.f;
  state.speed_fx.ticks=rng;
  validate();
  if(state.missile.weapon!=B23_MISSILE)assert(g.missile_brackets==0u);
 }
 assert(draw_calls==20006u);
 assert(vertex_count>draw_calls*6u);
 assert(texture_updates==0);
 printf("PASS B24 native GPU HUD: 20k fuzz+4 vectors, one draw/frame, ZERO pixel/texture uploads, original pause glyphs, missile-only lock, stage Rush streaks; %u GL draws\n",draw_calls);
 return 0;
}
