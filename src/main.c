/*
 * Iron Man 2 — PS Vita Flight Beta B5 (optimized software renderer).
 * Independent experimental locomotion / hovering controller.
 * Uses original IPA-derived textured assets but does NOT execute original gameplay.
 * All movement, HUD and flight simulation here are newly implemented.
 */
#include "renderer.h"
#include "b7_anim.h"
#include "b8_combat.h"
#include "b10_profile.h"
#include "b13_motion.h"
#include "b14_pose.h"
#include "b14_world.h"
#include "b24/b24_unified/im2_original_tables.h"
#include "b24/b24_unified/im2_frame_trace.h"
#include "b24/b24_unified/im2_suit_profile.h"
#include "b24/b24_unified/im2_audio_catalog.h"
#include "b24/b24_unified/im2_gameplay_clock.h"
#include "b16_action.h"
#include "b24/b24_unified/b24_unified.h"
#ifdef B24_GPU_ENGINE
#include "b24/b24_unified/b24_gpu_runtime.h"
#include "b24/b24_unified/b24_g8_live_original_motion.h"
#include "b24/b24_unified/b24_g8_wm_shoulder_gameplay.h"
#include "b24/b24_unified/b24_wm_original_rigid_sync.h"
#include "b24/b24_unified/b24_c1_original_collision.h"
#include "b24/b24_unified/b24_gpu_g68_collision.h"
#include "b24/b24_unified/b24_g75_source_capsule.h"
#ifdef B24_G169_AUTHENTIC_BEAM_3_PHASE
#include "b24/b24_unified/b24_g169_native_source_unibeam.h"
static B24G169Beam b24_g169_l1_source_beam_actor={0};
#endif
#ifdef B24_G163_CAMERA_AIM_FACING
#include "b24/b24_unified/b24_g163_aim_facing.h"
#endif
#ifdef B24_G137_MISSION000_REAL_SOURCE_EVENTS
#include "b24/b24_unified/b24_g137_source_mission000_intro.h"
#ifdef B24_G145_SOURCE_MISSION_AUDIO
#include "b24/b24_unified/b24_g142_native_sound_source_truth.h"
#include "b24/b24_unified/b24_g144_source_audio_channels.h"
#ifdef B24_G146_SOURCE_2010_QTE_1456
#include "b24/b24_unified/b24_g146_true_2010_QTE_actor.h"
#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
#include "b24/b24_unified/b24_g147_authentic_tutorial_actor.h"
#ifdef B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE
#include "b24/b24_unified/b24_g149_native_lua_bool_return.h"
#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP
#include "b24/b24_unified/b24_g152_source_tutorial_loop.h"
#endif
#endif
#endif
#endif
#endif

/* G137 native original 2010 level1 Lua Mission000OnStart SOURCE EVENTS:
 * on first real game tick, dispatch authentic linear first branch.
 * MissionPause is scoped to scripted task journal; player physics is
 * untouched until real QTE scene object and valid original input actions
 * have native bindings (so existing practice viewer stays testable). */
#ifdef B24_G137_MISSION000_REAL_SOURCE_EVENTS
static B24G137Mission000 g137_real_source_Mission000;
static int g137_real_source_initialized=0;
#ifdef B24_G145_SOURCE_MISSION_AUDIO
static B24G144NativeAudio g145_original_vita_channels;
#ifdef B24_G146_SOURCE_2010_QTE_1456
static B24G146QTE g146_real_2010_actor_QTE1456;
#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
static B24G147Tutorial g147_original_L1_source_tutorial;
#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP
static B24G152TutorialLoop g153_original_source_L1_PC73_wait_loop;
#endif
static int g147_native_Lua_PC72_queried_only=0;
static int g147_native_PC72_original_result=0;
#endif
#endif
static B24G142OwnerAudio g145_original_2010_music;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 B24G142OwnerAudio *music=(B24G142OwnerAudio*)ctx;
 if(!e||!music)return 0;
 /* Real original G137 Lua PC1 MissionPause is a mission-request journal,
  * not an unconditional global B14 physics freeze. */
 if(e->original_lua_pc==1&&
    e->opcode==B24_G137_CALL_MISSION_PAUSE)return 1;
 /* PC3 is safe equivalent only when genuine Game+0xEC initial = -1:
  * no game BGM was playing. Subsequent PC62/PC70 use actual original
  * source 803x40 .www audio table and real Vita PCM thread backend.
  * PC6 QTE Show1456 remains absolutely BLOCKED, no fake script resume. */
#ifdef B24_G146_SOURCE_2010_QTE_1456
 if(e->original_lua_pc==6&&e->opcode==B24_G137_CALL_SHOW)
  return b24_g146_qte_show_source_Lua_PC6(
    &g146_real_2010_actor_QTE1456,e,NULL,NULL);
 /* Actual QTE widget renderer has NOT been linked yet, so PC6 must
  * remain blocked. This stores exact sourced actor visibility request. */
#endif
#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
 if(e->original_lua_pc==67&&e->opcode==B24_G137_CALL_SHOW_TUT){
  /* G147A native 2010 ARM VM0xCE8CC StringMgr source CLARA339
   * translates to native TextID0x1053 = chap1.english[83].
   * Actual original UI TextBox renderer/font and PC73 Lua branch are
   * still NOT linked; pass verified translator but never ack absent draw. */
  return b24_g147_lua_ShowTut_PC67(
      &g147_original_L1_source_tutorial,e,
      b24_g147_source_native_StringMgr_translate,NULL,NULL);
 }
 if(e->original_lua_pc==72&&e->opcode==B24_G137_CALL_IS_TUT_CONFIRMED){
  /* Real ARM native Lua query returns boolean; existing G137
   * event dispatcher C API cannot deliver Lua VM return values.
   * Track source semantics for diagnostics, but do not infer PC73
   * EQ branch, MissionResume, or player flight authorization. */
#ifdef B24_G149_NATIVE_LUA_BOOL_PC72_SOURCE_GATE
  B24G149LuaBooleanReturn lua_return={0};
  if(!b24_g149_capture_original_PC72_boolean(
      e,&g147_original_L1_source_tutorial,&lua_return))return 0;
  /* Successful native Boolean FALSE is a completed Lua CALL, not a
   * failed scene binding. G137 still STOPS at the original PC73 EQ. */
  g147_native_Lua_PC72_queried_only=lua_return.result_is_valid;
  g147_native_PC72_original_result=lua_return.lua_boolean;
  return lua_return.result_is_valid;
#else
  g147_native_Lua_PC72_queried_only=1;
  g147_native_PC72_original_result=
    b24_g147_lua_IsTutConfirmed_native(&g147_original_L1_source_tutorial);
  return 0;
#endif
 }
#endif
 return b24_g142_owner_source_music_call(music,e);
}
#else
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 (void)ctx;return e&&e->opcode==B24_G137_CALL_MISSION_PAUSE;
}
#endif
#endif
#endif
#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
#include "b24/b24_unified/b24_g10_practice_target.h"
#include "b24/b24_unified/b24_g11_practice_melee_feedback.h"
/* G92_STATIC_DUMMY_SOURCE_IN_SINGLE_MAIN */
static B24G11PracticeMeleeFeedback g92_debug_feedback={0};
static int g92_debug_floor_found=0;
/* Shared accepted source G8 combat edge; diagnostic never polls it twice. */
static unsigned g92_debug_accepted_melee_edge=0;
#endif
#ifdef B24_G84_ORIGINAL_MOVESET_ROUTER
#include "b24/b24_unified/b24_g83_authentic_timed_router.h"
#ifdef B24_G218_SOURCE_STATE_OBSERVER
#include "b24/b24_unified/b24_g218_live_authentic_2010_state_observer.h"
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
#include "b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"
#include "b24/b24_unified/b24_g277_real_c1l1_ground_reject_reasons.h"
#ifdef B24_G279_WALK_TRACE_FILE
#include "b24/b24_unified/b24_g279_walk_trace.h"
#endif
#include "b24/b24_unified/b24_g229_ground_trajectory_window.h"
#endif
/* G218 sole passive original iOS 2010 StateData observer, NOT StateMgr. */
static B24G218LiveObserver b24_g218_live_source_state={0};
#endif
/* G84_OPTIONAL_TRUE_B24_MAIN */
static B24G83Timeline g84_time={0};
#ifdef B24_G87_REAL_TRANSITION_EVENTS
#include "b24/b24_unified/b24_g87_transition_events.h"
static B24G87TransitionState g87_events={0};
#endif
static int g84_previous_suit=-1;
static B24G83Dir g84_last_flight_dir=B24G83_DIR_IDLE;
#endif
/* G75_SOURCE_ONLY_GAMEPLAY_RECOVERY */ /* G70_REVERSE_MERGE */
#include "b24/b24_unified/b24_gpu_boot_trace.h"
static B24GpuRuntime b24_gpu_rt={0};
/* One source animation state/stream for the already-authoritative B14 body.
   G8 renderer remains the SAME real VitaGL owner. */
static B24G8LiveOriginalMotion b24_original_motion={0};
static B24WMShoulder b24_wm_shoulder={0};
static B24WMOutput b24_wm_frame_events={0};
/* Diagnostic ONLY: owner-authentic War Machine rigid Gun03 markers are not
   player weapon muzzle/FX sources until exact original binding is proven. */
static B24WMRigidSync b24_wm_original_rigid={0};
static B24C1OriginalCollision b24_original_walls={0};
#endif
#include "b24/b24_unified/b24_camera_recenter.h"
#include "b24/b18_gpu_probe/b17_input_landing_gate.h"
#include <SDL2/SDL.h>
#ifdef B24_GPU_ENGINE
static uint64_t b24_gpu_ticks(void *unused){
    (void)unused;
    return (uint64_t)SDL_GetPerformanceCounter();
}
#endif
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static const char *filename[5] = {"mark6.im2t", "mark4.im2t", "warmachine.im2t", "stealth.im2t", "suitcase.im2t"};
static const char *title[5] = {"MARK VI", "MARK IV", "WAR MACHINE", "STEALTH", "MARK V"};
static IM2Model model = {0};
static B7Motion motion = {0};
static B13Motion motion13={0};
static B14Pose animator={0};
static B16Action attack={0};
static B8Combat range={0};
static B24Unified b24_game={0};
static B24CameraRecenter b24_camera_follow={0};
static uint32_t b24_input_latched=0;
static B17GateState b24_gate={0};
static B17GateConfig b24_gate_cfg={0};

static unsigned b17_chest_vertex=0,b17_shoulder_vertex=0;
static unsigned b17_find_anchor(const IM2Model *m,int shoulder) {
    if(!m || !m->nv)return 0;
    float minx=m->vertices[0].x,maxx=minx;
    float miny=m->vertices[0].y,maxy=miny;
    float minz=m->vertices[0].z,maxz=minz;
    for(unsigned i=1;i<m->nv;i++){
        const IM2Vertex v=m->vertices[i];
        if(v.x<minx)minx=v.x;if(v.x>maxx)maxx=v.x;
        if(v.y<miny)miny=v.y;if(v.y>maxy)maxy=v.y;
        if(v.z<minz)minz=v.z;if(v.z>maxz)maxz=v.z;
    }
    const float dx=fmaxf(.01f,maxx-minx),dy=fmaxf(.01f,maxy-miny),dz=fmaxf(.01f,maxz-minz);
    /* Best candidate surface vertex near chest arc-reactor or shoulder hardpoint.
       This IS a geometry heuristic, not a decoded original weapon socket. */
    const float wantx=shoulder?minx+dx*.79f:(minx+maxx)*.5f;
    const float wanty=miny+dy*.22f;
    const float wantz=minz+dz*(shoulder?.84f:.73f);
    float best=1e30f;unsigned which=0;
    for(unsigned i=0;i<m->nv;i++){
        const IM2Vertex v=m->vertices[i];
        float xx=(v.x-wantx)/dx,yy=(v.y-wanty)/dy,zz=(v.z-wantz)/dz;
        float metric=xx*xx*2.8f+yy*yy*.5f+zz*zz*3.f;
        if(metric<best){best=metric;which=i;}
    }
    return which;
}
static void b17_rush_lean(IM2Model *m,float radians) {
    if(!m || !m->vertices)return;
    float sn=sinf(radians),cs=cosf(radians);
    for(unsigned i=0;i<m->nv;i++) {
        float y=m->vertices[i].y,z=m->vertices[i].z-m->center_z;
        m->vertices[i].y=y*cs-z*sn;
        m->vertices[i].z=m->center_z+y*sn+z*cs;
    }
}


static int load(int idx) {
    char path[256];
#ifdef __vita__
    snprintf(path, sizeof(path), "app0:models/%s", filename[idx]);
#else
    snprintf(path, sizeof(path), "models/%s", filename[idx]);
#endif
    b16_action_release(&attack);
    b14_pose_free(&animator);
    b13_release(&motion13);
    if(!im2_load(&model, path))return 0;
    b17_chest_vertex=b17_find_anchor(&model,0);
    b17_shoulder_vertex=b17_find_anchor(&model,1);
    if(!b7_prepare(&motion,(unsigned)idx,&model))return 0;
    if(!b13_prepare(&motion13,idx,&model))return 0;
    if(!b14_pose_init(&animator,&model))return 0;
    return b16_action_load(&attack,idx,&model);
}

/* Recreate renderer only after explicit user input. SDL2 Vita releases may
 * lack SDL_RenderSetVSync; renderer flags are used for a portable A/B test.
 * Keep the old B9 app separate as a reliable rollback. */
#ifndef B24_GPU_ENGINE
static int b10_make_display(SDL_Window *w, SDL_Renderer **out_r, SDL_Texture **out_t,
                            int vsync, int *real_vsync, int *error_flag) {
    SDL_Renderer *r=NULL;
    SDL_Texture *t=NULL;
    Uint32 flags=SDL_RENDERER_ACCELERATED | (vsync?SDL_RENDERER_PRESENTVSYNC:0);
    r=SDL_CreateRenderer(w,-1,flags);
    if(!r && vsync) r=SDL_CreateRenderer(w,-1,SDL_RENDERER_ACCELERATED);
    if(!r) r=SDL_CreateRenderer(w,-1,SDL_RENDERER_SOFTWARE);
    if(!r) return 0;
    t=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,IM2_W,IM2_H);
    if(!t){SDL_DestroyRenderer(r);return 0;}
    SDL_RendererInfo info={0};
    if(SDL_GetRendererInfo(r,&info)==0){
        *real_vsync=(info.flags & SDL_RENDERER_PRESENTVSYNC)!=0;
        *error_flag=vsync && !*real_vsync;
    }else { *real_vsync=0; *error_flag=1; }
    *out_r=r;*out_t=t;
    return 1;
}
static int b10_switch_display(SDL_Window *w,SDL_Renderer **r,SDL_Texture **t,
    int *requested,int *effective,int *error_flag){
    const int previous=*requested;
    const int target=!previous;
    SDL_DestroyTexture(*t);*t=NULL;
    SDL_DestroyRenderer(*r);*r=NULL;
    *requested=target;
    if(b10_make_display(w,r,t,target,effective,error_flag))return 1;
    /* Recovery attempt with a conservative no-VSync renderer. */
    *requested=0;
    if(b10_make_display(w,r,t,0,effective,error_flag)){
        *error_flag=1;return 1;
    }
    return 0;
}

#endif /* SDL graphics owner functions excluded in GPU mode */
static float clip(float a,float lo,float hi) {return a<lo?lo:(a>hi?hi:a);}
static float deadzone(float a) {return fabsf(a)<0.16f?0.0f:a;}
/* Stable head orbit anchor: compute once from bind mesh, not each animated
 * frame (sampling animated extrema would make the camera bob/jitter). */
static float b15_suit_head(const IM2Model *m){
 if(!m||!m->nv)return 1.02f;
 float top=m->vertices[0].z;
 for(unsigned i=1;i<m->nv;i++)if(m->vertices[i].z>top)top=m->vertices[i].z;
 return clip(top-m->center_z-.14f,.60f,1.65f);
}


int main(int argc,char **argv) {
    (void)argc;(void)argv;
#ifdef B24_GPU_ENGINE
    /* SDL gamepad/timer retained, SDL graphics subsystem not initialized:
       exactly one GPU owner (vitaGL/sceGxm). */
    (void)b24_gpu_boot_trace_reset();
    (void)b24_gpu_boot_trace_mark("10 SDL_GAMECONTROLLER_TIMER_INIT_BEGIN");
    if(SDL_Init(SDL_INIT_GAMECONTROLLER|SDL_INIT_TIMER)<0)return 1;
    (void)b24_gpu_boot_trace_mark("11 SDL_INIT_OK");
    SDL_Window *window=NULL;
    SDL_Renderer *sdl=NULL;
    SDL_Texture *display=NULL;
    int vsync_requested=0,vsync_active=0,profile_error=0;
#else
    if(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMECONTROLLER|SDL_INIT_TIMER)<0)return 1;
    SDL_Window *window=SDL_CreateWindow("Iron Man 2 - Arena B17",SDL_WINDOWPOS_CENTERED,
                                 SDL_WINDOWPOS_CENTERED,960,544,SDL_WINDOW_SHOWN);
    if(!window){SDL_Quit();return 2;}
    SDL_Renderer *sdl=NULL;
    SDL_Texture *display=NULL;
    int vsync_requested=1,vsync_active=0,profile_error=0;
    if(!b10_make_display(window,&sdl,&display,vsync_requested,&vsync_active,&profile_error)){
        SDL_DestroyWindow(window);SDL_Quit();return 3;
    }
#endif
    B10Profiler profiler={0};
#ifdef B24_GPU_ENGINE
    /* No full CPU world frame or zbuffer allocations in GPU version. */
    uint32_t *pixels=NULL;
    float *zbuffer=NULL;
    (void)pixels;(void)zbuffer;(void)sdl;(void)display;(void)window;
#else
    uint32_t *pixels=(uint32_t*)malloc(IM2_W*IM2_H*sizeof(uint32_t));
    float *zbuffer=(float*)malloc(IM2_W*IM2_H*sizeof(float));
    if(!pixels||!zbuffer){free(pixels);free(zbuffer);SDL_DestroyTexture(display);
        SDL_DestroyRenderer(sdl);SDL_DestroyWindow(window);SDL_Quit();return 5;}
#endif
    SDL_GameController *pad=NULL;
    for(int i=0;i<SDL_NumJoysticks();i++)if(SDL_IsGameController(i)){pad=SDL_GameControllerOpen(i);break;}
    b8_init(&range);
    B16Combat combat; b16_combat_init(&combat);
    /* Optional original tables are owner-supplied assets, never code payload. */
    const int original_tables_ready=im2_original_tables_load("app0:data/source_tables.im2d");
    (void)original_tables_ready;
    (void)im2_audio_catalog_load("app0:data/audio_catalog.im2a");
#ifdef B24_GPU_ENGINE
    (void)b24_gpu_boot_trace_mark(original_tables_ready?
        "13 ORIGINAL_TABLES_LOADED":"13 ORIGINAL_TABLES_MISSING_OR_INVALID");
#endif
    b24_unified_init(&b24_game);
#ifdef B24_GPU_ENGINE
    B24WMConfig b24_wm_cfg;
    b24_wm_default_config(&b24_wm_cfg);
    if(!b24_wm_init(&b24_wm_shoulder,&b24_wm_cfg))return 1;
#endif
    b17_gate_defaults(&b24_gate_cfg);b17_gate_init(&b24_gate);
    int idx=0,running=load(idx);
#ifdef B24_GPU_ENGINE
    (void)b24_gpu_boot_trace_mark(running?"12 FIRST_ORIGINAL_SUIT_LOADED":"12 FIRST_ORIGINAL_SUIT_LOAD_FAILED");
    /* Exact 2010 iOS C1L1_col_01 + C1L1_building_col BDAE faces:
       source-owned original 1908 faces, 1690 steep candidates, Z-UP.
       Fail closed rather than showing a fake wall collider as working. */
    if(running&&!b24_g70_g68_collision_load(&b24_original_walls,
                             "app0:assets/G66_original_collision.g66c")){
       (void)b24_gpu_boot_trace_mark("23 C1WC_ORIGINAL_COLLISION_LOAD_FAILED");
       running=0;
    }
    if(running)(void)b24_gpu_boot_trace_mark("23 C1WC_ORIGINAL_COLLISION_LOADED");
    if(running&&!b24_gpu_runtime_open(&b24_gpu_rt,"app0:maps/C1L1_environment.c1g2"))
        running=0;
    if(running&&!b24_gpu_runtime_set_clock(&b24_gpu_rt,b24_gpu_ticks,NULL,
                                          (double)SDL_GetPerformanceFrequency()))
        running=0;
#endif
    B14World world; b14_world_init(&world);world.head_height=b15_suit_head(&model);world.cam_z=world.head_height;
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
 /* G278: original Vita reconstructed port B14 initial source world,
  * NOT proof of original 2010 iOS first-story mission spawn. */
 const float g278_initial_b14_x=world.x,g278_initial_b14_y=world.y,g278_initial_b14_z=world.z;
 unsigned g278_boot_sample_count=0u;
#ifdef B24_G279_WALK_TRACE_FILE
 (void)b24_g279_trace_open("ux0:data/ironman2_g279_walk.csv");
#endif
#endif
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
 B24G227GroundProbe b24_g227_probe={0}; /* one read-only snapshot per game frame */
 B24G229WalkWindow b24_g229_window={0}; /* diagnostic only; no actor mutation */
#endif
    IM2Camera camera={0};camera.yaw=3.10f;camera.zoom=1.0f;
    float phase=0.0f,smooth_fps=0.0f;
    Uint32 landing_started=0; int landing_now=0,landing_stamp_pending=0;
    int trigger=0;
    int boost=0;
    int invert_move_x=0; /* G5 REAL VITA: inverted left stick was wrong; force natural L/R */
    int invert_camera_y=1; /* Vita hardware test reports looking down on UP */
    int previous_flight_stage=0;
    Uint32 rush_begin=SDL_GetTicks();
    Uint32 last=SDL_GetTicks(),frame=0;
    Im2GameplayClock motion_clock={0};
    (void)im2_gameplay_clock_tick(&motion_clock,last,0);
#if defined(IM2_FRAME_DIAGNOSTICS) && defined(B24_GPU_ENGINE)
    Im2FrameTrace frame_trace={0};
    (void)im2_frame_trace_open(&frame_trace,"ux0:data/ironman2_frame_profile.csv");
#endif
    while(running){
#if defined(IM2_FRAME_DIAGNOSTICS) && defined(B24_GPU_ENGINE)
        const Uint64 frame_wall_begin=SDL_GetPerformanceCounter();
        b24_original_motion.observed_dt=0.f;
#endif
        SDL_Event e;
        while(SDL_PollEvent(&e)){
            if(e.type==SDL_QUIT)running=0;
            if(e.type==SDL_KEYDOWN){
                SDL_Keycode key=e.key.keysym.sym;
                if(key==SDLK_ESCAPE)running=0;
                if(key==SDLK_f && !e.key.repeat)trigger=1;
                if(key==SDLK_RIGHTBRACKET && !e.key.repeat)b16_combat_mode(&combat,1);
                if(key==SDLK_LEFTBRACKET && !e.key.repeat)b16_combat_mode(&combat,-1);
                if(key==SDLK_t && !e.key.repeat){boost=!boost;world.rush=boost;rush_begin=motion_clock.game_ms;}
                if(key==SDLK_v && !e.key.repeat){
#ifndef B24_GPU_ENGINE
                  if(!b10_switch_display(window,&sdl,&display,&vsync_requested,&vsync_active,&profile_error))running=0;
                  profiler=(B10Profiler){0};
#endif
                }
                if(!e.key.repeat){
                    if(key==SDLK_x||key==SDLK_SPACE){idx=(idx+1)%5;load(idx);world.head_height=b15_suit_head(&model);}
                    if(key==SDLK_z||key==SDLK_TAB)camera.wireframe=!camera.wireframe;
                    if(key==SDLK_c){b14_world_toggle_flight(&world);landing_now=!world.flying;landing_stamp_pending=1;}
                    if(key==SDLK_r){b14_world_init(&world);boost=0;landing_now=0;camera.zoom=1.f;}
                }
            }
            if(e.type==SDL_CONTROLLERBUTTONDOWN){
                /* B24: Cross is an interaction input; suit switching moved to SELECT. */
                /* B24: Square is reserved for melee, not repulsor. */
                if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_BACK){
                    idx=(idx+1)%5;
                    if(!load(idx))running=0;
                    world.head_height=b15_suit_head(&model);
                }
                if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_B){
                    b14_world_toggle_flight(&world);
                    landing_now=!world.flying;landing_stamp_pending=1;
                }
                /* B24: D-pad Up moves vertically when airborne. */
                /* B24: D-pad Down moves vertically when airborne. */
                if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_LEFT)b16_combat_mode(&combat,-1);
                if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_DPAD_RIGHT)b16_combat_mode(&combat,1);
                /* START is event-latched so a quick press can't be lost at low FPS. */
                if(e.cbutton.button==SDL_CONTROLLER_BUTTON_START)
                    b24_input_latched|=IM2_BT_START;
                if(b24_unified_paused(&b24_game)){
                    switch(e.cbutton.button){
                    case SDL_CONTROLLER_BUTTON_A:b24_input_latched|=IM2_BT_CROSS;break;
                    case SDL_CONTROLLER_BUTTON_B:b24_input_latched|=IM2_BT_CIRCLE;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_UP:b24_input_latched|=IM2_BT_DUP;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_DOWN:b24_input_latched|=IM2_BT_DDOWN;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_LEFT:b24_input_latched|=IM2_BT_DLEFT;break;
                    case SDL_CONTROLLER_BUTTON_DPAD_RIGHT:b24_input_latched|=IM2_BT_DRIGHT;break;
                    default:break;
                    }
                }
                /* B24: Triangle RUSH held state is applied before movement tick. */

            }
        }
        if(!running)break;
        Uint32 now=SDL_GetTicks();float raw_dt=(now-last)*0.001f;last=now;
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
 b24_g227_probe=(B24G227GroundProbe){0}; /* pause, fail or missing input never reuse stale frame */
#endif
        float dt=clip(raw_dt,.0005f,.09f);
        float move_x=0,move_y=0,turn=0,look=0,ascend=0,zoom=0;
        const Uint8 *keys=SDL_GetKeyboardState(NULL);
        if(keys[SDL_SCANCODE_A])move_x-=1;
        if(keys[SDL_SCANCODE_D])move_x+=1;
        if(keys[SDL_SCANCODE_W])move_y+=1;
        if(keys[SDL_SCANCODE_S])move_y-=1;
        if(keys[SDL_SCANCODE_LEFT])turn-=1;
        if(keys[SDL_SCANCODE_RIGHT])turn+=1;
        if(keys[SDL_SCANCODE_UP])look+=1;
        if(keys[SDL_SCANCODE_DOWN])look-=1;
        if(keys[SDL_SCANCODE_E])ascend+=1;
        if(keys[SDL_SCANCODE_Q])ascend-=1;
        if(keys[SDL_SCANCODE_EQUALS])zoom+=1;
        if(keys[SDL_SCANCODE_MINUS])zoom-=1;
        if(pad){
            move_x+=(invert_move_x?-1.0f:1.0f)*deadzone(SDL_GameControllerGetAxis(pad,SDL_CONTROLLER_AXIS_LEFTX)/32768.0f);
            move_y-=deadzone(SDL_GameControllerGetAxis(pad,SDL_CONTROLLER_AXIS_LEFTY)/32768.0f);
            turn+=deadzone(SDL_GameControllerGetAxis(pad,SDL_CONTROLLER_AXIS_RIGHTX)/32768.0f);
            look+=(invert_camera_y?1.0f:-1.0f)*deadzone(SDL_GameControllerGetAxis(pad,SDL_CONTROLLER_AXIS_RIGHTY)/32768.0f);
            if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_RIGHTSHOULDER))trigger=1;
            if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_DPAD_UP))ascend+=1;
            if(SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_DPAD_DOWN))ascend-=1;
            boost=SDL_GameControllerGetButton(pad,SDL_CONTROLLER_BUTTON_Y)!=0;
            world.rush=boost;

        }
        uint32_t b24_buttons=0;
        if(pad){
          static const struct {SDL_GameControllerButton b; uint32_t mask;} buttons[]={
            {SDL_CONTROLLER_BUTTON_RIGHTSHOULDER,IM2_BT_R},
            {SDL_CONTROLLER_BUTTON_LEFTSHOULDER,IM2_BT_L},
            {SDL_CONTROLLER_BUTTON_X,IM2_BT_SQUARE},
            {SDL_CONTROLLER_BUTTON_Y,IM2_BT_TRIANGLE},
            {SDL_CONTROLLER_BUTTON_B,IM2_BT_CIRCLE},
            {SDL_CONTROLLER_BUTTON_A,IM2_BT_CROSS},
            {SDL_CONTROLLER_BUTTON_DPAD_UP,IM2_BT_DUP},
            {SDL_CONTROLLER_BUTTON_DPAD_DOWN,IM2_BT_DDOWN},
            {SDL_CONTROLLER_BUTTON_DPAD_LEFT,IM2_BT_DLEFT},
            {SDL_CONTROLLER_BUTTON_DPAD_RIGHT,IM2_BT_DRIGHT},
            {SDL_CONTROLLER_BUTTON_START,IM2_BT_START},
            {SDL_CONTROLLER_BUTTON_BACK,IM2_BT_SELECT}};
          for(unsigned b=0;b<sizeof(buttons)/sizeof(buttons[0]);b++)
            if(SDL_GameControllerGetButton(pad,buttons[b].b))b24_buttons|=buttons[b].mask;
        }
        b24_buttons|=b24_input_latched;
        b24_input_latched=0;
        world.camera_distance=clip(world.camera_distance-zoom*dt*1.8f,2.8f,6.4f);
        /* Bind-pose head anchor remains stable through limb animations. */
        /* Camera-relative movement in a 3D test world. The right analog is
           dedicated to a follow-camera, not a static model turntable. */
        float frame_world_dt=0.f;
        (void)frame_world_dt;
        if(!b24_unified_paused(&b24_game)){
#ifdef B24_GPU_ENGINE
          const float old_c1x=world.x,old_c1y=world.y,old_c1z=world.z;
#endif
          b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
          frame_world_dt=dt;
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
 b24_g227_probe.old_world_x=old_c1x;
 b24_g227_probe.old_world_y=old_c1y;
 b24_g227_probe.proposed_world_x=world.x;
 b24_g227_probe.proposed_world_y=world.y;
 b24_g227_probe.proposed_world_z=world.z;
 b24_g227_probe.stick_x=move_x;
 b24_g227_probe.stick_y=move_y;
 b24_g227_probe.flying=(uint8_t)world.flying;
 b24_g227_probe.recorded=1;
#endif
#ifdef B24_GPU_ENGINE
          const float proposed_c1x=world.x,proposed_c1y=world.y;
          /* Sub-frame genuine triangle sweep, original XY+Z collision.
             B14 drives normal walk, hover, Stage2 and RUSH the same way;
             only original wall contacts reconcile actor world XY.
             NO invented boxes and NO GL queries or per-frame heap allocation. */
#ifdef B24_G75_SOURCE_CAPSULE
          /* G75 original G67-style source 3-plane capsule + floor delta.
             The B14 world tick above remains the ONE gameplay integrator. */
          const float b75_proposed_z=world.z;
          float b75_x=world.x,b75_y=world.y,b75_z=world.z;
          if(!b24_g75_capsule_reconcile(&b24_original_walls,
                 old_c1x,old_c1y,old_c1z,
                 b75_x,b75_y,b75_z,
                 !world.flying,.35f,2.24f,&b75_x,&b75_y,&b75_z)){
             running=0;break;
          }
          world.x=b75_x;world.y=b75_y;world.z=b75_z;
          /* Source support is observed AFTER the single G75 reconciliation.
           * A nearby floor is insufficient: feet must actually be on it. */
          float b75_support_z=0.f;
          const int b75_supported=!world.flying && b24_g75_support_at(
              &b24_original_walls,world.x,world.y,world.z,&b75_support_z);
          b14_world_accept_ground_support(&world,b75_supported,b75_support_z);
          world.cam_z+=(world.z-b75_proposed_z)*fminf(7.f*dt,1.f);
#else
          if(!b24_c1_original_collision_resolve(&b24_original_walls,
              old_c1x,old_c1y,old_c1z,world.z,.35f,&world.x,&world.y)){
              running=0;break;
          }
#endif

#if defined(B24_G74_GROUND_CONTACT) && !defined(B24_G75_SOURCE_CAPSULE)
          /* G74: only snap if one original sourced floor is within
           * [-0.5,+0.45] player-foot Z. Never lift to remote sky roof.
           * Source collider has limited horizontal coverage; original
           * B14 fallback stays authoritative elsewhere. */
          if(world.flight_stage==0){
            float g74_native_floor=0.f;
            if(b24_g74_near_original_floor(&b24_original_walls,
                                          world.x,world.y,world.z,
                                          &g74_native_floor)){
              float support_delta=g74_native_floor-world.z;
              world.z=g74_native_floor;
              world.cam_z+=support_delta*fminf(7.f*dt,1.f);
            }
          }
#endif
          float c1_follow=fminf(7.f*dt,1.f);
          world.cam_x+=(world.x-proposed_c1x)*c1_follow;
          world.cam_y+=(world.y-proposed_c1y)*c1_follow;
#endif
          world.orbit=b24_camera_recenter(&b24_camera_follow,
              world.flying?world.flight_stage:0,dt,
              turn,look,world.orbit,world.heading);
#ifdef B24_G163_CAMERA_AIM_FACING
          /* G163 one current B14 actor and G83 original clip owner.
           * Current prototype L+repulsor aim prevents rotating away
           * toward move vector when strafing or backpedalling. Movement
           * delta, camera position, crosshair and Stage2/RUSH remain
           * untouched. Device source G161 reported actor turned backward. */
          world.heading=b24_g163_aim_heading(
              world.heading,world.orbit,dt,
              (b24_buttons&IM2_BT_L)&&combat.mode==B16_REPULSOR,
              !world.flying||world.flight_stage<=1);
#endif
          b14_world_target(&world);
          b16_combat_tick(&combat,&world,dt);
        }
        B24Observation b24_obs={0};
        b24_obs.player_z_up=(Im2Vec3){world.x,world.y,world.z};
        b24_obs.heading_rad=world.heading;
        b24_obs.orbit_rad=world.orbit;
        b24_obs.pitch_rad=world.pitch;
        b24_obs.left_x=move_x;b24_obs.left_forward=move_y;
        b24_obs.right_x=turn;b24_obs.right_y=look;
        b24_obs.buttons=b24_buttons;
        b24_obs.stage=world.flying?world.flight_stage:0;
        b24_obs.suit_index=idx;
        b24_obs.weapon_index=combat.mode;
        b24_obs.target_visible=world.visible;
        b24_obs.target_alive=world.visible;
        b24_obs.target_id=world.visible?0:-1; /* B17 sphere ONLY, not real enemy */
        b24_obs.target_occluded=0; /* real mission raycast unavailable */
        b24_obs.target_distance=world.visible?8.f:0.f; /* provisional demo range */
        b24_obs.target_screen_x=(int)world.screen_x;
        b24_obs.target_screen_y=(int)world.screen_y;
        b24_obs.target_health_percent=-1.f;
#ifdef B24_GPU_ENGINE
        b24_obs.melee_anim_active=
             b24_g8_motion_melee_source_active(&b24_original_motion);
#else
        b24_obs.melee_anim_active=0;
#endif
        b24_obs.energy_percent=combat.energy;
        b24_obs.wave=(int)combat.wave;
        b24_obs.real_enemies_loaded=0; /* no invisible B19 drones */
        b24_obs.dt=dt;
        b24_unified_tick(&b24_game,&b24_obs);
        /* Every source pose/shot owner uses the SAME pause-adjusted timestamp.
         * Keep `now` as raw SDL wall time for frame/G279 observations. */
        const uint32_t motion_now=im2_gameplay_clock_tick(
            &motion_clock,(uint32_t)now,b24_unified_paused(&b24_game));
        if(landing_stamp_pending){landing_started=motion_now;landing_stamp_pending=0;}
#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP
        /* G137 previously invoked source Mission000 only once at boot.
         * Retry EXACT blocked Lua event on later frames. G137's cursor
         * guarantees PC1 MissionPause and PC3 PauseMusic are NOT replayed
         * after their authentic ACK; current QTE Show1456 (PC6) remains
         * unacknowledged without actual render and does not release input. */
        if(g137_real_source_initialized &&
           g137_real_source_Mission000.phase==
             B24_G137_BLOCKED_NATIVE_SCENE_BINDING){
          (void)b24_g137_mission000_dispatch_verified_prefix(
            &g137_real_source_Mission000,
            g137_real_scene_MissionPause_only,
            &g145_original_2010_music);
        }
        /* Only after original PC1..72 actually ACK can original PC73
         * EQ evaluate. G152 waits on REAL native Wait(10) bridge
         * (currently NULL), StopVoice (NULL) and HUD340 (NULL).
         * This is deliberately fail-closed, not an in-game QTE claim. */
        if(g137_real_source_initialized &&
           g137_real_source_Mission000.phase==
             B24_G137_WAITING_2010_LUA_BRANCH_PC73){
          (void)b24_g152_tutorial_loop_step(
            &g153_original_source_L1_PC73_wait_loop,
            &g147_original_L1_source_tutorial,
            0, NULL, NULL, NULL, NULL);
        }
#endif
#ifdef B24_G137_MISSION000_REAL_SOURCE_EVENTS
        if(!g137_real_source_initialized){
          g137_real_source_initialized=1;
          if(b24_g137_mission000_init(&g137_real_source_Mission000)){
#ifdef B24_G145_SOURCE_MISSION_AUDIO
            b24_g144_source_audio_init(&g145_original_vita_channels);
#ifdef B24_G146_SOURCE_2010_QTE_1456
            (void)b24_g146_qte_source_init(&g146_real_2010_actor_QTE1456);
#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
            b24_g147_tutorial_init(&g147_original_L1_source_tutorial);
#ifdef B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP
            b24_g152_tutorial_loop_init(&g153_original_source_L1_PC73_wait_loop);
#endif
#endif
#endif
            g145_original_2010_music=(B24G142OwnerAudio){0};
            /* Original 2010 Game::Game source ARM0x99564 sets
             * Game+0xEC current music ID=-1. No source BGM has
             * played in rebuilt Vita game at Mission000 start. */
            g145_original_2010_music.original_current_music_zero_based_id=-1;
            g145_original_2010_music.original_current_music_id_from_actual_game_state_verified=1;
            g145_original_2010_music.original_current_music_track_is_playing=0;
            g145_original_2010_music.backend=
              b24_g144_source_audio_backend(&g145_original_vita_channels);
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,
               &g145_original_2010_music);
#else
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);
#endif
          }
        }
        /* G145: Source PC1 MissionPause then PC3 empty-current-BGM
         * native-value -1 (Game+0xEC) advances; PC6 QTE Show(1456)
         * remains explicitly blocked until true iOS scene node 1456
         * has render/touch event bindings. No fabricated Camera/QTE,
         * PC914/927 input enable or PC935 MissionResume. */
#endif

#ifdef B24_G145_SOURCE_MISSION_AUDIO
        if(g137_real_source_initialized)
          (void)b24_g144_source_audio_pause(&g145_original_vita_channels,
                                           b24_unified_paused(&b24_game));
#endif
#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
        /* Exactly ONE debug target; initially invalid until ORIGINAL 2010
           G68 collision surface proves placement. Never fake an invisible
           support plane. Fixed for the remainder of this test session. */
        if(!g92_debug_floor_found && b24_original_walls.ready){
          const float xx[]={0.f,world.x,world.x+5.f,world.x-5.f};
          const float yy[]={10.f,world.y+5.f,world.y,world.y};
          for(unsigned candidate=0;candidate<4;candidate++){
            float zfloor=0.f;
            if(!b24_g75_floor_crossed(&b24_original_walls,
                  xx[candidate],yy[candidate],world.z+2.f,
                  world.z-5.f,&zfloor))continue;
            B24G10PracticeTarget demo=b24_g10_practice_target_at_floor(zfloor);
            demo.x=xx[candidate];demo.y=yy[candidate];
            if(!b24_g10_practice_target_valid(&demo))continue;
            b24_gpu_rt.g92_practice_dummy=demo;
            g92_debug_floor_found=1;
            break;
          }
        }
        if(g92_debug_floor_found &&
           !b24_unified_paused(&b24_game)&&!world.flying&&
           (im2_suit_uses_802_bank(idx)||idx==4)&&g92_debug_accepted_melee_edge){
           (void)b24_g11_practice_melee_hit(&g92_debug_feedback,
             &b24_gpu_rt.g92_practice_dummy,
             world.x,world.y,world.z,motion_now,1,1);
        }
        if(g92_debug_floor_found)
          b24_gpu_rt.g92_practice_dummy.hit_flash=
            b24_g11_practice_hit_flash(&g92_debug_feedback,motion_now);
        g92_debug_accepted_melee_edge=0; /* one consumed debug latch */
        /* ORIGINAL HP/mission data/weapon fire events remain untouched. */
#endif
#ifdef B24_GPU_ENGINE
#ifdef B24_G85_NATIVE_MARKV_629
         /* G85_NATIVE_MARKV_629: retain ONE existing user combo button
            owner, now valid also for 629v original Mark V suit index 4. */
        if(!b24_unified_paused(&b24_game) && (im2_suit_uses_802_bank(idx)||idx==4) &&
           !world.flying && b24_unified_should_melee(&b24_game))
#else
        if(!b24_unified_paused(&b24_game) && im2_suit_uses_802_bank(idx) &&
           !world.flying && b24_unified_should_melee(&b24_game))
#endif
          {
           b24_g8_motion_melee_trigger(&b24_original_motion,motion_now);
          #ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
           g92_debug_accepted_melee_edge=1;
          #endif
          }
        /* Right-shoulder autonomous turret skill uses REAL B24 controls and
           one shared B14 world tick. L+Square is PROTOTYPE skill input.
           With real_enemies_loaded=0 the weapon NEVER spawns fake targets
           or pretends to damage invisible enemies. Actual original 2010
           left/right gun muzzle nodes remain unproven, so there are NO
           projectile/particle emissions in G8 from these placeholders. */
        B24WMInput b24_wm_in={0};
        b24_wm_in.war_machine_selected=(idx==2);
        b24_wm_in.real_enemies_loaded=b24_obs.real_enemies_loaded;
        b24_wm_in.trigger_skill_edge=(!b24_unified_paused(&b24_game) && idx==2 &&
                (b24_game.controls.held&IM2_BT_L)!=0 &&
                b24_unified_should_melee(&b24_game));
        b24_wm_in.dt=dt;
        b24_wm_in.muzzle_left_rocket=(B24WMVec3){world.x,world.y,world.z};
        b24_wm_in.muzzle_right_gatling=(B24WMVec3){world.x,world.y,world.z};
        b24_wm_in.rocket_aim_direction=(B24WMVec3){0.f,1.f,0.f};
        b24_wm_in.targets=NULL;b24_wm_in.target_count=0;
        b24_wm_in.trigger_missile_edge=0; /* exact left muzzle unverified */
        if(b24_unified_paused(&b24_game))
          b24_wm_frame_events=(B24WMOutput){0};
        else if(!b24_wm_tick(&b24_wm_shoulder,&b24_wm_in,&b24_wm_frame_events)){
           running=0;break;
        }
#endif
        world.camera_distance=b24_unified_chase_distance(&b24_game);
        if(world.flight_stage==3 && previous_flight_stage!=3)rush_begin=motion_now;
        previous_flight_stage=world.flight_stage;
        camera.third_person=1;
        camera.player_x=world.x;camera.player_y=world.y;camera.player_z=world.z;
        camera.player_heading=world.heading;
        camera.orbit=world.orbit;camera.pitch=world.pitch;
        camera.cam_x=world.cam_x;camera.cam_y=world.cam_y;camera.cam_z=world.cam_z;
        camera.flying=world.flying;camera.altitude=world.z;
        camera.zoom=1.f;
        camera.camera_distance=world.camera_distance;
        camera.flight_stage=world.flight_stage;
        camera.waves=world.waves;
        camera.invert_x=invert_move_x;camera.invert_y=invert_camera_y;
        if(!b24_unified_paused(&b24_game))
          camera.hover_bob=world.flying?.018f*sinf(phase):0.f;
        camera.target_visible=world.visible;camera.target_screen_x=world.screen_x;
        camera.target_screen_y=world.screen_y;camera.target_radius=world.screen_radius;
        camera.aim_x=278.f;camera.aim_y=110.f;
        camera.beam_time=world.beam_time;
        camera.hits=world.hits;camera.shots=world.shots;camera.completed=world.completed;
        if(!b24_unified_paused(&b24_game))phase+=dt*7.f;
        float immediate_fps=1.0f/fmaxf(raw_dt,.001f);
        smooth_fps=smooth_fps==0.0f?immediate_fps:smooth_fps*.95f+immediate_fps*.05f;
        camera.fps=smooth_fps;
        /* Diagnostic timings are deliberately measured separately. On real Vita
           this tells us whether the CPU rasterizer or SDL texture upload/present
           is the actual FPS limiter; do not infer from desktop FPS alone. */
        if(landing_now && motion_now-landing_started>800u)landing_now=0;
        const int has_move=world.speed>.16f;
        const Uint64 t0=SDL_GetPerformanceCounter();
        B17GateInput b24_analog={0};
        b24_analog.stick_x=move_x;b24_analog.stick_forward=move_y;
        b24_analog.airborne=world.flying;
        if(!b24_unified_paused(&b24_game))
          b17_gate_step(&b24_gate,&b24_gate_cfg,&b24_analog);
        const int ground_run=b24_gate.is_ground_running;
        B14Mode mode=b15_pose_pick(&motion13,world.flying,has_move,world.flight_stage,
                                 world.flying?boost:ground_run,landing_now,motion_now-rush_begin);
        const B13Clip *chosen=b16_idle_override(&attack,mode,idx);
        /* No neutral WM walk baked yet. Use REAL IronMan_run-to-WM skinned retarget
           rather than the known-bad, raised-hand Warmachine_Aim_Ground_move_F.
           This is interim locomotion, not verified original WM walking. */
        if(idx==2 && mode==B14_WALK && motion13.clips[B13_RUN].xyz)
            chosen=&motion13.clips[B13_RUN];
        if(!b24_unified_paused(&b24_game) && !b14_pose_tick_ex(&animator,&model,&motion,&motion13,mode,(unsigned)motion_now,
              chosen)){running=0;break;}
        if(!b24_unified_paused(&b24_game) && idx==2 && world.flying && world.flight_stage==3)
            b17_rush_lean(&model,0.43f); /* PROTOTYPE tilt, NOT original Rush clip */
        if(trigger && !b24_unified_paused(&b24_game)){
          const unsigned palm=attack.palm_r; /* B24: RIGHT REPULSOR ONLY */
          const unsigned emitter=combat.mode==B16_UNIBEAM?b17_chest_vertex:
                                 combat.mode==B16_MISSILE?b17_shoulder_vertex:palm;
          float muzzle[3];b16_model_palm(&model,&world,emitter,muzzle);
          int fired=b16_combat_fire(&combat,&world,muzzle);
#ifdef B24_G169_AUTHENTIC_BEAM_3_PHASE
           /* Exact 2010 authored original 3×Beam IM2V: ONLY when the
            * existing B16 combat accepted a unibeam energy/damage event.
            * Current B16 accepted event remains port HLE, not proven
            * native Gameloft dispatch. Mark V=629 and MarkVI=802 real
            * bind sources. No WarMachine Beam original and no Stage2
            * cruise or Rush fire. Original QTE/weapon type not forged. */
           if(fired>=0 && combat.mode==B16_UNIBEAM &&
              (!world.flying||world.flight_stage<=1))
             (void)b24_g169_native_beam_begin(
                 &b24_g169_l1_source_beam_actor,idx,world.flying!=0,
                 motion_now);
#endif
          if(fired>=0 && combat.mode==B16_REPULSOR && !attack.attack_active){
              b16_attack_begin(&attack,motion_now,world.flying,0,0);
#ifdef B24_GPU_ENGINE
              /* Trigger on REAL accepted shot. Source _Att begins NEXT tick.
                 Existing B16 is fallback when exact IM2V is absent. */
              b24_g8_motion_repulsor_trigger(&b24_original_motion,motion_now);
#endif
          }
        }
        trigger=0; /* paused presses cannot queue a shot for resume */
#ifdef B24_GPU_ENGINE
        /* B14 has already computed SINGLE authoritative world pose and B13
           59-bank fallback. Only geometry-verified VI/IV/Stealth / War Machine
           get genuine streamed 2010 motion; failure leaves fallback intact.
           IMPORTANT: do this BEFORE B16 right-palm-only repulsor blending,
           never replace the original B16 attack mask/muzzle direction. */
        if(!b24_unified_paused(&b24_game)){
          const B24MotionStage original_stage=
              !world.flying?(landing_now?B24M_LAND:
                        ground_run?B24M_RUN:has_move?B24M_WALK:B24M_IDLE):
              (world.flight_stage>=3?B24M_RUSH:
               world.flight_stage==2?B24M_CRUISE:
               has_move?B24M_DRIFT:B24M_HOVER);
#ifdef B24_G84_ORIGINAL_MOVESET_ROUTER
          /* B14 ticked ONCE before this point; G8 is sole original
             source IM2V animator. Existing G8 melee and accepted B16
             repulsor have priority; NO second weapon event is created.
             L aims in this PROTOTYPE controller; original iOS L semantics
             still need touchHLE validation. */
          if(g84_previous_suit!=idx){
             b24_g83_timeline_reset(&g84_time);
#ifdef B24_G87_REAL_TRANSITION_EVENTS
             b24_g87_transition_reset(&g87_events);
#endif
             g84_last_flight_dir=B24G83_DIR_IDLE;
             g84_previous_suit=idx;
          }
          B24G83Input g84_input={0};
          g84_input.suit_index=idx;
          g84_input.motion=!world.flying?B24G83_GROUND:
             world.flight_stage>=3?B24G83_RUSH:
             world.flight_stage==2?B24G83_FLIGHT:B24G83_HOVER;
          g84_input.aim=(b24_buttons&IM2_BT_L)&&
             combat.mode==B16_REPULSOR?B24G83_AIM_HAND:B24G83_AIM_NONE;
          g84_input.axis_x=clip(move_x,-1.f,1.f);
          g84_input.axis_y=clip(move_y,-1.f,1.f);
          g84_input.run=ground_run;
          g84_input.previous_flight_dir=g84_last_flight_dir;
          g84_input.accepted_weapon_event=0; /* sole accepted B16->G8 */
          #ifdef B24_G87_REAL_TRANSITION_EVENTS
          /* Physics and floor contact from the SAME G75/G68 original
             triangle world. Flight mode OFF alone proves no landing.
             Never sample made-up ground height or teleport into floors. */
          float g87_source_floor=0.f;
#ifdef B24_G75_SOURCE_CAPSULE
          g84_input.grounded_contact_verified=(!world.flying &&
               b24_g74_near_original_floor(&b24_original_walls,
                world.x,world.y,world.z,&g87_source_floor) &&
               fabsf(world.z-g87_source_floor)<=.08f);
#else
          /* Without the original source-backed floor resolver, fail closed:
             transition can be selected but landing is never invented. */
          g84_input.grounded_contact_verified=0;
#endif
          g84_input.transition=b24_g87_transition_tick(&g87_events,
               g84_input.motion,g84_input.grounded_contact_verified,0);
#else
          g84_input.grounded_contact_verified=0;
#endif
          B24G83Selection g84_route={0};
          if(!b24_g83_timeline_tick(&g84_time,NULL,motion_now,
                &g84_input,&g84_route)){running=0;break;}
          /* G301: the visual G83 selection may be a pinned authored
             800ms fly_ftol while B14's stick has already turned again.
             Keep the next transition input in PHYSICAL Stage2 input
             space; never inherit a stale visual clip direction.
             HOVER/RUSH are separate flight modes with no Stage2
             turn history. A single B14 world tick remains sole owner. */
          #ifdef B24_G169_AUTHENTIC_BEAM_3_PHASE
           /* One REAL G83/G8 source streaming owner, no second animated
            * model: accepted weapon event routes through normal motion
            * sample selection, respecting native beam source durations. */
           const char *g169_original_source_beam_clip=
               b24_g169_native_beam_clip(
                  &b24_g169_l1_source_beam_actor,idx,
                  world.flying!=0,world.flying?world.flight_stage:0,
                  motion_now);
           if(g169_original_source_beam_clip)
              g84_route.stem=g169_original_source_beam_clip;
#endif
           g84_last_flight_dir=b24_g83_physical_flight_dir(
                g84_input.motion,g84_input.axis_x,g84_input.axis_y);
          if(!b24_g8_motion_tick_g84(&b24_original_motion,
                "app0:animations",model.vertices,sizeof(IM2Vertex),
                model.nv,idx,original_stage,move_x,move_y,
                motion_now,g84_route.stem)){running=0;break;}
#ifdef B24_G218_SOURCE_STATE_OBSERVER
          /* G218 observes the ACTUAL successfully opened original 2010
           * G8 selected source IM2V, not G83's intended candidate.
           * This original owner-authenticated 194-state lookup makes
           * source AttackType / native event data available for QA.
           * No original touch meaning, hit time, missile/projectile,
           * physics or callback is changed. */
          (void)b24_g218_observe_actually_loaded_G8_clip(
             &b24_g218_live_source_state,idx,
             b24_original_motion.selected,b24_original_motion.active,
             b24_original_motion.missing);
#endif
#else
          if(!b24_g8_motion_tick(&b24_original_motion,
                "app0:animations",
                model.vertices,sizeof(IM2Vertex),model.nv,idx,
                original_stage,move_x,move_y,motion_now)){
             running=0;break;
          }
#endif
          /* Original 2010 WM Gun01-04 and Gun03 author marker stream is
             synchronized with EXACT selected original body clip + B14 age.
             No extra physics tick, no second model, no projectile emission.
             Missing IM2K files silently preserve G8's old 59 fallback. */
          const B24WMG8ActorPose wm_actor={
               world.x,world.y,world.z,world.heading,
               model.center_z,camera.hover_bob};
          if(!b24_wm_rigid_sync_tick(&b24_wm_original_rigid,
             "app0:animations",
             b24_original_motion.selected,
             b24_original_motion.stream.frames,
             b24_original_motion.stream.duration_ms,
             b24_original_motion.started_ms,motion_now,
             idx==2 && b24_original_motion.active &&
                    !b24_original_motion.missing,
             &wm_actor)){
              /* Only an optional unproven diagnostic failed; DO NOT
                 interrupt combat/flying or replace the known-good suit. */
              b24_wm_rigid_sync_release(&b24_wm_original_rigid);
          }
        }
#endif
#ifdef B24_GPU_ENGINE
        /* Real full-body 2010 directional _Att must NOT be overdrawn by B16
           upper-arm overlay. If exact source absent B16 remains fallback. */
        if(b24_g8_motion_whole_body_fire(&b24_original_motion) ||
           b24_g8_motion_melee_source_active(&b24_original_motion))
          attack.attack_active=0;
#endif
        if(!b24_unified_paused(&b24_game))
          b16_apply_attack(&attack,&model,motion_now);
        camera.beam_time=world.beam_time;
        camera.shots=world.shots;camera.hits=world.hits;camera.completed=world.completed;
        camera.b16_active=1;camera.weapon_mode=combat.mode;camera.energy=combat.energy;
        camera.combo_step=combat.combo_step;
        camera.emitter_vertex=combat.mode==B16_UNIBEAM?(int)b17_chest_vertex:
              combat.mode==B16_MISSILE?(int)b17_shoulder_vertex:
              (int)attack.palm_r; /* B24: HUD muzzle uses SAME right arm */
        camera.missile_active=combat.active_missile;
        camera.missile_x=combat.missile_x;camera.missile_y=combat.missile_y;camera.missile_z=combat.missile_z;
        const Uint64 t1=SDL_GetPerformanceCounter();
        camera.vsync_requested=vsync_requested;
        camera.vsync_active=vsync_active;
        camera.profile_error=profile_error;
        camera.motion_ms=profiler.motion_ms;
        camera.raster_ms=profiler.cpu_ms;
        camera.upload_ms=profiler.upload_ms;
        camera.copy_ms=profiler.copy_ms;
        camera.present_ms=profiler.present_ms;
        char label[50];
        const char *suffix=world.flying?(world.flight_stage==3?" RUSH":""):
                           (ground_run?" RUN":"");
        snprintf(label,sizeof(label),"%s%s",title[idx],suffix);
#ifdef B24_GPU_ENGINE
        /* Original B14/B16 motion, suit cycle, B24 HUD and game input state;
           C1L1 GPU scene + animated original suit + alpha B22 HUD + ONE swap. */
        if(!b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)){
            running=0;break;
        }
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
          /* TRUE GPU root AFTER render, vs resolved original 2010 G66C
           * collision/world, vs follow camera target. This does not
           * draw another frame or change player's movement. Logging
           * every 120 frames (not every tick); original 2010 weapon
           * and animation semantics remain completely untouched. */
          b24_g227_probe.resolved_world_x=world.x;
          b24_g227_probe.resolved_world_y=world.y;
          b24_g227_probe.resolved_world_z=world.z;
          b24_g227_probe.gpu_actor_world_x=b24_gpu_rt.frame_pose.x;
          b24_g227_probe.gpu_actor_world_y=b24_gpu_rt.frame_pose.y;
          b24_g227_probe.gpu_actor_world_z=b24_gpu_rt.frame_pose.z;
          /* Camera cam_x/y is a position, not the look-at target. */
          b24_g227_probe.camera_target_x=camera.cam_x;
          b24_g227_probe.camera_target_y=camera.cam_y;
          b24_g227_probe.original_G8_clip_loaded=
             (uint8_t)(b24_original_motion.active&&!b24_original_motion.missing);
          b24_g227_probe.original_G8_source_clip_missing=
             (uint8_t)b24_original_motion.missing;
          b24_g227_probe.frame_num=(uint32_t)frame;
          /* G278 FIRST 3 ACTUAL SUCCESSFULLY RENDERED Vita frames.
           * G75 loaded real G66C original collision; unlike G276
           * source-authored local coordinates, this observes WORLD
           * coordinates of the actual reconstructed Vita runtime.
           * Three samples expose early Mission000 camera/state changes
           * without modifying player's velocity/spawn/weapon/animation.
           */
          if(g278_boot_sample_count<3u){
            float g278_nearby_native_floor=0.f;
            const unsigned g278_has_native_floor =
                (unsigned)(b24_original_walls.ready &&
                b24_g74_near_original_floor(&b24_original_walls,
                   world.x,world.y,world.z,&g278_nearby_native_floor));
            const B24G277CollisionReasons g278_reject=b24_g277_last_collision_reasons();
            SDL_Log("G278_INITIAL_BOOT_WORLD render_sample=%u rendered_frame=%u "
              "B14_initial=(%.5f,%.5f,%.5f) resolved_WORLD=(%.5f,%.5f,%.5f) "
              "original_G66C_ready=%u near_native_floor=%u native_floor_Zup=%.5f "
              "GPU_actor=(%.5f,%.5f,%.5f) camera_player=(%.5f,%.5f,%.5f) "
              "grounded=%u flight_stage=%d original_wall_reject=%u "
              "missing_floor_reject=%u step_height_reject=%u accepted_substeps=%u "
              "original_2010_iOS_story_spawn_unverified=YES",
              g278_boot_sample_count,(unsigned)frame,
              g278_initial_b14_x,g278_initial_b14_y,g278_initial_b14_z,
              world.x,world.y,world.z,
              (unsigned)b24_original_walls.ready,g278_has_native_floor,
              g278_nearby_native_floor,
              b24_gpu_rt.frame_pose.x,b24_gpu_rt.frame_pose.y,
              b24_gpu_rt.frame_pose.z,
              camera.player_x,camera.player_y,camera.player_z,
              (unsigned)!world.flying,(int)world.flight_stage,
              (unsigned)g278_reject.candidate_wall_reject,
              (unsigned)g278_reject.candidate_no_source_support,
              (unsigned)g278_reject.candidate_unsupported_step_height,
              (unsigned)g278_reject.candidate_accepted);
            #ifdef B24_G279_WALK_TRACE_FILE
            /* Same 3 successful GPU frames captured by G278. No invented
             * mission start, root offset, floor or network source. */
            B24G279Row g279_first={0};
            g279_first.phase="BOOT";
            g279_first.frame=(unsigned)frame;
            g279_first.millis=(unsigned)now;
            g279_first.initial_x=g278_initial_b14_x;
            g279_first.initial_y=g278_initial_b14_y;
            g279_first.initial_z=g278_initial_b14_z;
            g279_first.x=world.x;g279_first.y=world.y;g279_first.z=world.z;
            g279_first.gpu_x=b24_gpu_rt.frame_pose.x;
            g279_first.gpu_y=b24_gpu_rt.frame_pose.y;
            g279_first.gpu_z=b24_gpu_rt.frame_pose.z;
            g279_first.cam_x=camera.cam_x;g279_first.cam_y=camera.cam_y;
            g279_first.stick_x=b24_g227_probe.stick_x;
            g279_first.stick_y=b24_g227_probe.stick_y;
            g279_first.wall_reject=(unsigned)g278_reject.candidate_wall_reject;
            g279_first.missing_floor=(unsigned)g278_reject.candidate_no_source_support;
            g279_first.step_reject=(unsigned)g278_reject.candidate_unsupported_step_height;
            g279_first.has_native_floor=g278_has_native_floor;
            g279_first.native_floor_z=g278_has_native_floor?g278_nearby_native_floor:0.f;
            (void)b24_g279_trace_write(&g279_first);
#endif
            ++g278_boot_sample_count;
          }
          /* G277: same real successful GPU frame, latest authentic
           * B14 -> G75 candidate wall/source floor/step verdict.
           * Every 120 frames only; counts are per most recent sweep. */
          if((frame%120u)==0u){
            const B24G277CollisionReasons g277=b24_g277_last_collision_reasons();
            SDL_Log("G277_GROUND_REJECTION_BREAKDOWN original C1L1 "
              "wall_reject=%u missing_floor=%u step_height_reject=%u "
              "accepted=%u sweep_substeps=%u "
              "world_Zup=%.4f actorGPU_Zup=%.4f grounded=%u",
              (unsigned)g277.candidate_wall_reject,
              (unsigned)g277.candidate_no_source_support,
              (unsigned)g277.candidate_unsupported_step_height,
              (unsigned)g277.candidate_accepted,
              (unsigned)g277.sweep_substeps,
              b24_g227_probe.resolved_world_z,
              b24_g227_probe.gpu_actor_world_z,
              (unsigned)!world.flying);
          }
          /* G229: compare 120 consecutive successful rendered ground frames.
           * 'now' is SDL_GetTicks() captured this frame by original main.
           * Camera.cam_x/y is POSITION; no landmark projection inference. */
          if(b24_g229_window_push(&b24_g229_window,&b24_g227_probe,(uint32_t)now)){
             const B24G229WindowVerdict vw=b24_g229_window_classify(&b24_g229_window);
             const float dwx=b24_g229_window.last_world_x-b24_g229_window.first_world_x;
             const float dwy=b24_g229_window.last_world_y-b24_g229_window.first_world_y;
             const float dcx=b24_g229_window.last_camera_x-b24_g229_window.first_camera_x;
             const float dcy=b24_g229_window.last_camera_y-b24_g229_window.first_camera_y;
             SDL_Log("G229_WALK_WINDOW source-only verdict=%s frames=%u elapsed_ms=%u "
                  "active_stick=%u B14_idle=%u collision_reject=%u GPU_root_mismatch=%u "
                  "B14_path=%.4f accepted_world_path=%.4f max_GPU_error=%.4f "
                  "world_displacement=(%.4f,%.4f) camera_position_displacement=(%.4f,%.4f) "
                  "G8_missing_frames=%u Zup_first_last=(%.4f,%.4f) "
                  "Zup_min_max=(%.4f,%.4f) GPU_actor_Zup_last=%.4f",
                  b24_g229_window_verdict_name(vw),
                  (unsigned)b24_g229_window.samples,
                  (unsigned)(b24_g229_window.last_tick_ms-b24_g229_window.first_tick_ms),
                  (unsigned)b24_g229_window.active_stick_frames,
                  (unsigned)b24_g229_window.b14_idle_frames,
                  (unsigned)b24_g229_window.collision_reject_frames,
                  (unsigned)b24_g229_window.root_mismatch_frames,
                  b24_g229_window.b14_path_xy,b24_g229_window.resolved_path_xy,
                  b24_g229_window.max_gpu_root_error,dwx,dwy,dcx,dcy,
                  (unsigned)b24_g229_window.missing_original_clip_frames,
                  b24_g229_window.first_world_z,b24_g229_window.last_world_z,
                  b24_g229_window.min_world_z,b24_g229_window.max_world_z,
                  b24_g227_probe.gpu_actor_world_z);
             #ifdef B24_G279_WALK_TRACE_FILE
             /* G229 has a WHOLE contiguous 120 SUCCESSFUL ground
              * render-frame window. Preserve world/GPU/camera deltas,
              * verified G171 collision rejects, input and native sample.
              * Last G277 wall/no-floor/step counts are per final sweep,
              * while G229 collision_reject is over full 120-frame window. */
             const B24G277CollisionReasons g279_last=
                 b24_g277_last_collision_reasons();
             B24G279Row g279_win={0};
             g279_win.phase="WALK120";
             g279_win.frame=(unsigned)frame;
             g279_win.millis=(unsigned)now;
             g279_win.initial_x=g278_initial_b14_x;
             g279_win.initial_y=g278_initial_b14_y;
             g279_win.initial_z=g278_initial_b14_z;
             g279_win.x=world.x;g279_win.y=world.y;g279_win.z=world.z;
             /* G296: unlike G278's BOOT-only original C1L1 floor probe,
              * measure the true source G66C floor near the CURRENT 120-frame
              * window endpoint. Read-only; neither world position nor G75
              * movement/collision result is changed. */
             g279_win.has_native_floor=(unsigned)(
                 b24_original_walls.ready &&
                 b24_g74_near_original_floor(&b24_original_walls,
                     world.x,world.y,world.z,&g279_win.native_floor_z));
             g279_win.gpu_x=b24_gpu_rt.frame_pose.x;
             g279_win.gpu_y=b24_gpu_rt.frame_pose.y;
             g279_win.gpu_z=b24_gpu_rt.frame_pose.z;
             g279_win.cam_x=camera.cam_x;g279_win.cam_y=camera.cam_y;
             g279_win.stick_x=b24_g227_probe.stick_x;
             g279_win.stick_y=b24_g227_probe.stick_y;
             g279_win.verdict=b24_g229_window_verdict_name(vw);
             g279_win.net_world_dx=b24_g229_window.last_world_x-b24_g229_window.first_world_x;
             g279_win.net_world_dy=b24_g229_window.last_world_y-b24_g229_window.first_world_y;
             g279_win.net_camera_dx=b24_g229_window.last_camera_x-b24_g229_window.first_camera_x;
             g279_win.net_camera_dy=b24_g229_window.last_camera_y-b24_g229_window.first_camera_y;
             g279_win.b14_path=(float)b24_g229_window.b14_path_xy;
             g279_win.accepted_path=(float)b24_g229_window.resolved_path_xy;
             g279_win.active_stick=(unsigned)b24_g229_window.active_stick_frames;
             g279_win.coll_reject=(unsigned)b24_g229_window.collision_reject_frames;
             g279_win.root_mismatch=(unsigned)b24_g229_window.root_mismatch_frames;
             g279_win.wall_reject=(unsigned)g279_last.candidate_wall_reject;
             g279_win.missing_floor=(unsigned)g279_last.candidate_no_source_support;
             g279_win.step_reject=(unsigned)g279_last.candidate_unsupported_step_height;
             (void)b24_g279_trace_write(&g279_win);
#endif
             b24_g229_window_reset(&b24_g229_window);
          }
          if((frame%120u)==0u){
             const B24G227WalkVerdict verdict=
                b24_g227_qa_classify(&b24_g227_probe);
             SDL_Log("G227_WALK_ROOT source-only verdict=%s "
                 "stick=(%.3f,%.3f) world_pre=(%.4f,%.4f) "
                 "B14_proposal=(%.4f,%.4f) native_collision_resolved=(%.4f,%.4f) "
                 "GPU_ACTOR=(%.4f,%.4f) camera_POSITION=(%.4f,%.4f) "
                 "G8_original_loaded=%u G8_missing=%u original_clip=%s "
                 "Zup_B14=%.4f Zup_G75=%.4f Zup_GPU=%.4f",
               b24_g227_walk_verdict_name(verdict),
               b24_g227_probe.stick_x,b24_g227_probe.stick_y,
               b24_g227_probe.old_world_x,b24_g227_probe.old_world_y,
               b24_g227_probe.proposed_world_x,b24_g227_probe.proposed_world_y,
               b24_g227_probe.resolved_world_x,b24_g227_probe.resolved_world_y,
               b24_g227_probe.gpu_actor_world_x,b24_g227_probe.gpu_actor_world_y,
               b24_g227_probe.camera_target_x,b24_g227_probe.camera_target_y,
               (unsigned)b24_g227_probe.original_G8_clip_loaded,
               (unsigned)b24_g227_probe.original_G8_source_clip_missing,
               b24_original_motion.selected,
               b24_g227_probe.proposed_world_z,
               b24_g227_probe.resolved_world_z,
               b24_g227_probe.gpu_actor_world_z);
          }
#endif
#ifdef IM2_FRAME_DIAGNOSTICS
        Im2FrameSample perf={0};
        perf.frame=(unsigned long long)frame;perf.millis=(unsigned)now;
        perf.raw_dt_ms=(double)raw_dt*1000.0;
        perf.paused=b24_unified_paused(&b24_game);
        perf.simulation_dt_ms=(double)frame_world_dt*1000.0;
        perf.controls_dt_ms=(double)b24_game.observed_dt*1000.0;
        perf.animation_blend_dt_ms=perf.paused?0.0:(double)b24_original_motion.observed_dt*1000.0;
        perf.cpu_frame_wall_ms=(double)(SDL_GetPerformanceCounter()-frame_wall_begin)*1000.0/
                              (double)SDL_GetPerformanceFrequency();
        for(unsigned pi=0;pi<B24P_COUNT;pi++)perf.phase_ms[pi]=b24_gpu_rt.profile.last_ms[pi];
        perf.world_x=world.x;perf.world_y=world.y;perf.world_z=world.z;
        perf.gpu_x=b24_gpu_rt.frame_pose.x;perf.gpu_y=b24_gpu_rt.frame_pose.y;
        perf.gpu_z=b24_gpu_rt.frame_pose.z;
        if(frame<3 || frame%60u==0u){
          im2_frame_trace_clocks(&perf);
          (void)im2_frame_trace_write(&frame_trace,&perf);
        }
#endif
        frame++;
#ifdef B24_GPU_PROFILE_LOG
        if(frame%120u==0u){
            const B24CpuGpuProfile *p=&b24_gpu_rt.profile;
            fprintf(stderr,"B24 CPU ms: stream %.2f camera %.2f scene-call %.2f armor-call %.2f HUD-call %.2f swap-wall %.2f | REAL GPU BUSY UNKNOWN\n",
                p->average_ms[B24P_MODEL_STREAM],
                p->average_ms[B24P_CAMERA_SETUP],
                p->average_ms[B24P_SCENE_CALLS],
                p->average_ms[B24P_SUIT_CALLS],
                p->average_ms[B24P_HUD_CALLS],
                p->average_ms[B24P_SWAP_WALL]);
        }
#endif
        const Uint64 t5=SDL_GetPerformanceCounter();
        const double scale=1000.0/(double)SDL_GetPerformanceFrequency();
        b10_record(&profiler,(float)((t1-t0)*scale),
                   (float)((t5-t1)*scale),0.f,0.f,0.f);
        camera.display_ms=0.f; /* no valid GPU display timer measured yet */
#else
        if(!b24_unified_paused(&b24_game))
            im2_render(pixels,zbuffer,&model,&camera,label,frame++);
        b24_unified_draw_overlay(&b24_game,pixels,IM2_W);
        const Uint64 t2=SDL_GetPerformanceCounter();
        if(SDL_UpdateTexture(display,NULL,pixels,IM2_W*sizeof(uint32_t))!=0){running=0;break;}
        const Uint64 t3=SDL_GetPerformanceCounter();
        SDL_RenderClear(sdl);
        SDL_RenderCopy(sdl,display,NULL,NULL);
        const Uint64 t4=SDL_GetPerformanceCounter();
        SDL_RenderPresent(sdl);
        const Uint64 t5=SDL_GetPerformanceCounter();
        const double scale=1000.0/(double)SDL_GetPerformanceFrequency();
        b10_record(&profiler,(float)((t1-t0)*scale), (float)((t2-t1)*scale),
                (float)((t3-t2)*scale),(float)((t4-t3)*scale),(float)((t5-t4)*scale));
        camera.display_ms=profiler.upload_ms+profiler.copy_ms+profiler.present_ms;
#endif
        if(!pad)SDL_Delay(10);
    }
#if defined(IM2_FRAME_DIAGNOSTICS) && defined(B24_GPU_ENGINE)
    im2_frame_trace_close(&frame_trace);
#endif
    if(pad)SDL_GameControllerClose(pad);
    b16_action_release(&attack);b14_pose_free(&animator);b13_release(&motion13);b7_release(&motion);im2_free(&model);free(pixels);free(zbuffer);
#ifdef B24_GPU_ENGINE
    b24_c1_original_collision_free(&b24_original_walls);
    b24_wm_rigid_sync_release(&b24_wm_original_rigid);
    b24_g8_motion_release(&b24_original_motion);
    b24_gpu_runtime_close(&b24_gpu_rt);
#else
    SDL_DestroyTexture(display);SDL_DestroyRenderer(sdl);SDL_DestroyWindow(window);
#endif
#ifdef B24_G145_SOURCE_MISSION_AUDIO
    if(g137_real_source_initialized)b24_g144_source_audio_release(&g145_original_vita_channels);
#endif
    im2_audio_catalog_close();
    im2_original_tables_close();
    SDL_Quit();return 0;
}
