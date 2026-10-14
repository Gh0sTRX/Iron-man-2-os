#include "b24_gpu_runtime.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
int b24_gpu_runtime_set_clock(B24GpuRuntime *r,B24GpuTicksFn fn,void *ctx,double hz){
 return r&&b24_gpu_profile_set_clock(&r->profile,fn,ctx,hz);
}
static int b24_runtime_armor_draw(void *userdata){
 B24GpuRuntime *r=(B24GpuRuntime *)userdata;
 return b24_gpu_suit_draw(&r->suit,&r->stream.source,
                &(B24GpuSuitPose){r->frame_pose.x,r->frame_pose.y,
                r->frame_pose.z,r->frame_pose.heading});
}
static int b24_runtime_hud_draw(void *userdata){
 B24GpuRuntime *r=(B24GpuRuntime *)userdata;
#ifdef B24_GPU_NATIVE_HUD
 /* HUD is CPU-authored QUADS and GPU-rasterized in one draw call;
    no full-screen bitmap generation or CPU->GPU texture upload. */
 if(!b24_native_hud_build(&r->native_hud,r->frame_game))return 0;
 return b24_native_hud_draw(&r->native_hud);
#else
 return b24_gpu_hud_bridge_draw(&r->hud,r->frame_game);
#endif
}
int b24_gpu_runtime_open(B24GpuRuntime *r,const char *city_file){
 if(!r||r->initialized||!city_file)return 0;
 if(!b24_gpu_c1_load(&r->city,city_file))return 0;
 /* The source-authentic sidecar is optional during the GPU migration.
    If absent, NO fabricated city textures will be assigned. This
    sidecar will be staged alongside C1G2 only after conversion validation. */
 (void)b24_c1_uv_load(&r->city_uv,"app0:maps/C1L1_environment.c1uv");
 r->verified_vehicle_atlas=0; /* B12 original atlas not packaged yet */
 if(!b24_gpu_owner_init(&r->owner,0)){
  b24_c1_uv_free(&r->city_uv);
  b24_gpu_c1_free(&r->city);return 0;
 }
#ifndef B24_GPU_NATIVE_HUD
 /* Source-only comparison mode: old bitmap B22/B23 HUD retained. */
 if(!b24_gpu_hud_bridge_prepare(&r->hud)){
  b24_c1_uv_free(&r->city_uv);
  b24_gpu_c1_free(&r->city);return 0;
 }
#endif
 r->initialized=1;
 r->loaded_suit_index=-1;
 return 1;
}
int b24_gpu_runtime_sync_model(B24GpuRuntime *r,const IM2Model *m,int suit_index){
 if(!r||!r->initialized||!m||suit_index<0||suit_index>=5)return 0;
 /* The allocator may reuse the SAME addresses for two different armors!
    Suit identity is authoritative even if texture pointer/dimensions match. */
 if(r->loaded_suit_index!=suit_index||
    r->stream.source.texture_rgba!=m->texture||
    r->stream.source.nv!=m->nv||r->stream.source.nt!=m->nt){
    /* Authentic armor change loads a NEW IM2T atlas+geometry and B14/B16
       reinitializes its animation buffers; keep them in sync with GPU. */
    b24_gpu_suit_release(&r->suit);
    b24_gpu_im2_stream_free(&r->stream);
    if(!b24_gpu_im2_stream_init(&r->stream,m))return 0;
    if(!b24_gpu_suit_prepare(&r->suit,&r->stream.source)){
       b24_gpu_im2_stream_free(&r->stream);return 0;
    }
    r->loaded_suit_index=suit_index;
    r->suit_rebinds++;
 }
 return b24_gpu_im2_stream_update(&r->stream,m);
}
int b24_gpu_runtime_draw(B24GpuRuntime *r,const IM2Model *m,
                          const IM2Camera *c,B24Unified *g,int suit_index){
 if(!r||!r->initialized||!m||!c||!g)return 0;
 b24_gpu_profile_begin(&r->profile);
 if(!b24_gpu_runtime_sync_model(r,m,suit_index))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_MODEL_STREAM);
 /* One authoritative B17 Z-up orbit. Flying stage2/RUSH reduces the
    shoulder offset; free-look recenter remains the existing B24 controller. */
 float a=c->orbit, cp=cosf(c->pitch),sp=sinf(c->pitch);
 float fd=c->camera_distance;
 if(!isfinite(a)||!isfinite(cp)||!isfinite(sp)||
    !isfinite(fd)||fd<.1f)return 0;
 float fx=sinf(a),fy=cosf(a),rx=cosf(a),ry=-sinf(a);
 float side=c->flying&&c->flight_stage>=2?0.f:.55f;
 B24GpuCamera cam={
  {c->cam_x-fx*fd*cp+rx*side,
   c->cam_y-fy*fd*cp+ry*side,
   c->cam_z+fd*sp},
  {c->cam_x,c->cam_y,c->cam_z},
  {0,0,1},
  72.f,960.f/544.f,.15f,2600.f
 };
 B24GpuCameraMatrices matrices={0};
 if(!b24_gpu_camera_matrices(&cam,&matrices))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_CAMERA_SETUP);
 if(!b24_gpu_owner_begin(&r->owner,&matrices))return 0;
 if(!b24_gpu_owner_scene_material(&r->owner,&r->city,
            r->city_uv.loaded?&r->city_uv:NULL,
            r->verified_vehicle_atlas))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_SCENE_CALLS);
 r->frame_pose=(B24GpuSuitPose){c->player_x,c->player_y,c->player_z,
                                c->player_heading};
 r->frame_game=g;
 if(!b24_gpu_owner_armor(&r->owner,b24_runtime_armor_draw,r))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_SUIT_CALLS);
 if(!b24_gpu_owner_hud(&r->owner,b24_runtime_hud_draw,r))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_HUD_CALLS);
 if(!b24_gpu_owner_present(&r->owner))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_SWAP_WALL);
 r->frames++;
 return 1;
}
void b24_gpu_runtime_close(B24GpuRuntime *r){
 if(!r)return;
 b24_gpu_hud_bridge_release(&r->hud);
 b24_gpu_suit_release(&r->suit);
 b24_gpu_im2_stream_free(&r->stream);
 b24_c1_uv_free(&r->city_uv);
 b24_gpu_c1_free(&r->city);
 /* vitaGL has no stable public vglEnd in current upstream header.
    Keep shutdown OS-owned and do not attempt a second SDL GPU teardown. */
 memset(r,0,sizeof(*r));
}
