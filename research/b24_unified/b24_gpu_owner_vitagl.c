#include "b24_gpu_owner.h"
#include "b24_gpu_boot_trace.h"
#include <vitaGL.h>
#include <stddef.h>
/* This is the future B24 ENGINE frame owner.
 * Never call from a running SDL_Renderer frame. Keep SDL input while
 * replacing the SDL video renderer (no secondary SwapBuffers).
 * Does not pretend to have original armored mesh/HUD callbacks yet. */
int b24_gpu_owner_init(B24GpuOwner *o,int sdl_renderer_exists){
 if(!o||o->initialized||sdl_renderer_exists)return 0;
 (void)b24_gpu_boot_trace_mark("31 VITAGL_INIT_BEGIN");
 if(!vglInit(0x1000000)){
  (void)b24_gpu_boot_trace_mark("31 VITAGL_INIT_FAILED");
  return 0;
 }
 (void)b24_gpu_boot_trace_mark("32 VITAGL_INIT_OK");
 glViewport(0,0,960,544);
 glEnable(GL_DEPTH_TEST);
 glDepthFunc(GL_LESS);
 glClearColor(.015f,.025f,.045f,1.f);
 o->initialized=1;
 o->frame_open=0;
 o->pass=0;
 o->frames_presented=o->scene_draws=o->armor_draws=o->hud_draws=0;
 return 1;
}
int b24_gpu_owner_begin(B24GpuOwner *o,const B24GpuCameraMatrices *cam){
 if(!o||!o->initialized||o->frame_open||!cam)return 0;
 o->frame_open=1;o->pass=0;
 glViewport(0,0,960,544);
 glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
 glMatrixMode(GL_PROJECTION);
 glLoadMatrixf(cam->projection);
 glMatrixMode(GL_MODELVIEW);
 glLoadMatrixf(cam->view);
 return 1;
}
int b24_gpu_owner_scene(B24GpuOwner *o,const B24GpuC1Mesh *scene){
 if(!o||!o->frame_open||o->pass!=0||!scene)return 0;
 if(!b24_gpu_c1_draw_vitagl(scene))return 0;
 o->pass=1;o->scene_draws++;return 1;
}
int b24_gpu_owner_armor(B24GpuOwner *o,B24GpuDrawCallback draw,void *user){
 if(!o||!o->frame_open||o->pass!=1||!draw||!draw(user))return 0;
 o->pass=2;o->armor_draws++;return 1;
}
int b24_gpu_owner_hud(B24GpuOwner *o,B24GpuDrawCallback draw,void *user){
 if(!o||!o->frame_open||o->pass!=2||!draw||!draw(user))return 0;
 o->pass=3;o->hud_draws++;return 1;
}
int b24_gpu_owner_present(B24GpuOwner *o){
 if(!o||!o->initialized||!o->frame_open||o->pass!=3)return 0;
 vglSwapBuffers(GL_FALSE);
 o->frames_presented++;
 o->pass=0;o->frame_open=0;return 1;
}
