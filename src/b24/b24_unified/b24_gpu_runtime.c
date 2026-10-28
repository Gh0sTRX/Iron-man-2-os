#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
#include "b24_g10_practice_target.h"
#endif
#include "b24_gpu_runtime.h"
#include "im2_game_camera.h"
#if defined(B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY) || defined(B24_G164_HERO_CAMERA_FRAMING)
#include "b24_g164_camera_sky_framing.h"
#endif
#ifdef B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY
#include <vitaGL.h>
#endif
#include "b24_gpu_boot_trace.h"
#ifdef B24_G72_DUSK_ATMOSPHERE
#include "b24_gpu_g72_sky.h"
#endif
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
                r->frame_pose.z,r->frame_pose.heading,
                r->frame_pose.pitch,r->frame_pose.roll});
}
static int b24_runtime_hud_draw(void *userdata){
 B24GpuRuntime *r=(B24GpuRuntime *)userdata;
#ifdef B24_GPU_NATIVE_HUD
 /* HUD is CPU-authored QUADS and GPU-rasterized in one draw call;
    no full-screen bitmap generation or CPU->GPU texture upload. */
 if(!b24_native_hud_build(&r->native_hud,r->frame_game))return 0;
#ifdef IM2_TEST_OPPONENT
 b24_native_hud_test_opponent(&r->native_hud,r->test_opponent.loaded,r->test_opponent.state.spawned,
   r->test_opponent.state.target.hp,r->test_opponent.state.player_hp);
#endif
 return b24_native_hud_draw(&r->native_hud);
#else
 return b24_gpu_hud_bridge_draw(&r->hud,r->frame_game);
#endif
}
int b24_gpu_runtime_open(B24GpuRuntime *r,const char *city_file){
 if(!r||r->initialized||!city_file)return 0;
#ifdef B24_G68_CITY_BACKEND
 /* REVERSE MERGE: G9/B17 gameplay engine remains authoritative. Only the
  * G68 native PVR city is injected after initializing the ONE VitaGL owner.
  * No second G68 standalone update/physics/player/mission is instantiated. */
 (void)b24_gpu_boot_trace_mark("20 G68_SOURCE_RENDER_BEGIN");
 if(!b24_gpu_owner_init(&r->owner,0))return 0;
 if(!b24_g68_city_open(&r->g68_city,
       "app0:assets/G66_city.g66m","app0:assets/G66_city")){
   (void)b24_gpu_boot_trace_mark("20 G68_SOURCE_RENDER_FAILED");
   b24_g68_city_close(&r->g68_city);
   return 0;
 }
 (void)b24_gpu_boot_trace_mark("22 G68_SOURCE_CITY_READY");
#ifdef B24_G73_REAL_SKY
 /* ACTUAL BRES authored sky, PVR material bindings provisional, never
  * a second GL context, zero impact on B14 gameplay state. */
 if(!b24_g73_sky_open(&r->original_sky)){
   (void)b24_gpu_boot_trace_mark("22 G73_NATIVE_SKY_LOAD_FAILED");
   b24_g68_city_close(&r->g68_city);
   return 0;
 }
 (void)b24_gpu_boot_trace_mark("22 G73_NATIVE_SKY_READY");
#endif
#else
 (void)b24_gpu_boot_trace_mark("20 C1G2_LOAD_BEGIN");
 if(!b24_gpu_c1_load(&r->city,city_file)){
  (void)b24_gpu_boot_trace_mark("20 C1G2_LOAD_FAILED");
  return 0;
 }
 (void)b24_gpu_boot_trace_mark("21 C1G2_LOAD_OK");
 /* The source-authentic sidecar is optional during the GPU migration.
    If absent, NO fabricated city textures will be assigned. This
    sidecar will be staged alongside C1G2 only after conversion validation. */
 (void)b24_c1_uv_load(&r->city_uv,"app0:maps/C1L1_environment.c1uv");
 /* Source-validated IDs for ALL 22919 triangles, not diffuse textures.
    Optional until original 2010 BDAE material->atlas sampler recovery. */
 (void)b24_c1_material_source_load(&r->city_material,
                                    "app0:maps/C1L1_environment.c1ma");
 (void)b24_gpu_boot_trace_mark("22 C1UV_C1MA_READ_COMPLETED");
 r->verified_vehicle_atlas=0; /* B12 original atlas not packaged yet */
 if(!b24_gpu_owner_init(&r->owner,0)){
  b24_c1_material_source_free(&r->city_material);
  b24_c1_uv_free(&r->city_uv);
  b24_gpu_c1_free(&r->city);return 0;
 }
#endif
 /* Only the original B12 C1L1_Vehicles image, converted privately to C1TX.
    If absent, stay with diagnostic car colors and do not invent textures. */
#ifndef B24_G68_CITY_BACKEND
 if(r->city_uv.loaded)
  (void)b24_gpu_c1_vehicle_atlas_open(&r->verified_vehicle_atlas,
                                      "app0:maps/C1L1_Vehicles.c1tx");
#endif
#ifndef B24_GPU_NATIVE_HUD
 /* Source-only comparison mode: old bitmap B22/B23 HUD retained. */
 if(!b24_gpu_hud_bridge_prepare(&r->hud)){
  b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
  b24_c1_material_source_free(&r->city_material);
  b24_c1_uv_free(&r->city_uv);
#ifdef B24_G68_CITY_BACKEND
  b24_g68_city_close(&r->g68_city);
#else
  b24_gpu_c1_free(&r->city);
#endif
  return 0;
 }
#endif
 (void)b24_gpu_boot_trace_mark("33 GPU_RUNTIME_OPEN_OK");
#ifdef IM2_TEST_OPPONENT
 (void)im2_test_opponent_open(&r->test_opponent);
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
 if(!r->frames)(void)b24_gpu_boot_trace_mark("40 FIRST_FRAME_ENTER");
 b24_gpu_profile_begin(&r->profile);
 if(!r->frames)(void)b24_gpu_boot_trace_mark("41 SUIT_GPU_STREAM_BEGIN");
 if(!b24_gpu_runtime_sync_model(r,m,suit_index))return 0;
 if(!r->frames)(void)b24_gpu_boot_trace_mark("42 SUIT_GPU_STREAM_OK");
 b24_gpu_profile_phase(&r->profile,B24P_MODEL_STREAM);
 /* One authoritative B17 Z-up orbit. Flying stage2/RUSH reduces the
    shoulder offset; free-look recenter remains the existing B24 controller. */
 B24GpuCamera cam;B24GpuCameraMatrices matrices;
 if(!im2_game_camera(c,g,&cam,&matrices))return 0;
 b24_gpu_profile_phase(&r->profile,B24P_CAMERA_SETUP);
 if(!r->frames)(void)b24_gpu_boot_trace_mark("43 SCENE_FRAME_BEGIN");
 if(!b24_gpu_owner_begin(&r->owner,&matrices))return 0;
#ifdef B24_G72_DUSK_ATMOSPHERE
 /* Source city stays unchanged: camera-relative temporary background only,
  * old B24 GPU owner still clears, owns ALL passes and swaps once. */
 if(!b24_g72_draw_dusk_atmosphere(c->pitch,c->orbit))return 0;
#endif
#ifdef B24_G68_CITY_BACKEND
#ifdef B24_G73_REAL_SKY
#ifdef B24_G164_CAMERA_RELATIVE_ORIGINAL_SKY
 /* G164: authentic 2010 skyline/moon/stars G73 288 source vertices are
  * centered near source origin x/y=0. The G161 render owner applied the
  * WORLD camera translation; roaming original C1L1 hundreds of units
  * off-center meant skyline/crosstrees drift or vanish while stars
  * (full spherical UV sheet) remained. Preserve authored UV/PVR, sky
  * rotation and original scene draw depth behavior; strip translation
  * ONLY in the temporary sky-only modelview. Restore before G68 city. */
 float skyview[16]={0};
 if(!b24_g164_source_sky_view(matrices.view,skyview))return 0;
 glMatrixMode(GL_MODELVIEW);
 glPushMatrix();
 glLoadMatrixf(skyview);
 const int g164_sky_ok=b24_g73_sky_draw(&r->original_sky);
 glPopMatrix();
 if(!g164_sky_ok)return 0;
#else
 if(!b24_g73_sky_draw(&r->original_sky))return 0;
#endif
#endif
 if(!b24_gpu_owner_scene_g68(&r->owner,&r->g68_city))return 0;
#else
 if(!b24_gpu_owner_scene_material(&r->owner,&r->city,
            r->city_uv.loaded?&r->city_uv:NULL,
            r->verified_vehicle_atlas))return 0;
#endif
#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
 /* The source G75 collision sampler must have explicitly found authentic
  * G68 ground before the G10 practice target can become visible. */
 if(b24_g10_practice_target_valid(&r->g92_practice_dummy))
  (void)b24_g10_practice_target_draw(&r->g92_practice_dummy);
#endif
#ifdef IM2_TEST_OPPONENT
 if(!im2_test_opponent_draw(&r->test_opponent))return 0;
#endif
 if(!r->frames)(void)b24_gpu_boot_trace_mark("44 SCENE_DRAW_OK");
 b24_gpu_profile_phase(&r->profile,B24P_SCENE_CALLS);
 /* Original B24 CPU flight stage drives the SAME animated armor GPU root.
    Stage1 retains grounded upright pose; Stage2/RUSH get genuine 3D pitch
    and lateral bank only (not a second simulation or replacement animation). */
 r->frame_pose=(B24GpuSuitPose){c->player_x,c->player_y,c->player_z,
                 c->player_heading,g->visual_root.visual_pitch_rad,
                 g->visual_root.visual_roll_rad};
 r->frame_game=g;
 if(!b24_gpu_owner_armor(&r->owner,b24_runtime_armor_draw,r))return 0;
 if(!r->frames)(void)b24_gpu_boot_trace_mark("45 ARMOR_DRAW_OK");
 b24_gpu_profile_phase(&r->profile,B24P_SUIT_CALLS);
 if(!b24_gpu_owner_hud(&r->owner,b24_runtime_hud_draw,r))return 0;
 if(!r->frames)(void)b24_gpu_boot_trace_mark("46 HUD_DRAW_OK");
 b24_gpu_profile_phase(&r->profile,B24P_HUD_CALLS);
 if(!b24_gpu_owner_present(&r->owner))return 0;
 if(!r->frames)(void)b24_gpu_boot_trace_mark("47 FIRST_SWAP_OK");
 b24_gpu_profile_phase(&r->profile,B24P_SWAP_WALL);
 r->frames++;
 return 1;
}
void b24_gpu_runtime_close(B24GpuRuntime *r){
 if(!r)return;
#ifdef IM2_TEST_OPPONENT
 im2_test_opponent_close(&r->test_opponent);
#endif
 b24_gpu_hud_bridge_release(&r->hud);
 b24_gpu_suit_release(&r->suit);
 b24_gpu_im2_stream_free(&r->stream);
 b24_gpu_c1_vehicle_atlas_close(&r->verified_vehicle_atlas);
 b24_c1_material_source_free(&r->city_material);
 b24_c1_uv_free(&r->city_uv);
#ifdef B24_G68_CITY_BACKEND
#ifdef B24_G73_REAL_SKY
 b24_g73_sky_close(&r->original_sky);
#endif
 b24_g68_city_close(&r->g68_city);
#else
 b24_gpu_c1_free(&r->city);
#endif
 /* vitaGL has no stable public vglEnd in current upstream header.
    Keep shutdown OS-owned and do not attempt a second SDL GPU teardown. */
 memset(r,0,sizeof(*r));
}
