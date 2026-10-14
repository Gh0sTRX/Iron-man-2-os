#!/usr/bin/env python3
"""B24 opt-in real GPU main integration AFTER C2 & right-arm source patch.
Source-only; never builds VPK. Fail closed on any unknown generated code.
Default SDL renderer path preserved unless -DB24_ENABLE_GPU=ON.
"""
from pathlib import Path
W=Path(__file__).resolve().parents[2]/"work"
p=W/"src/main.c"
s=p.read_text()
def rep(before,after):
    global s
    n=s.count(before)
    if n!=1:raise RuntimeError(f"B24 GPU source drift: {n} matches of {before[:90]!r}")
    s=s.replace(before,after)
rep('#include "../b24/b24_unified/b24_unified.h"',
'''#include "../b24/b24_unified/b24_unified.h"
#ifdef B24_GPU_ENGINE
#include "../b24/b24_unified/b24_gpu_runtime.h"
static B24GpuRuntime b24_gpu_rt={0};
#endif''')
rep('#include <SDL2/SDL.h>', '''#include <SDL2/SDL.h>
#ifdef B24_GPU_ENGINE
static uint64_t b24_gpu_ticks(void *unused){
    (void)unused;
    return (uint64_t)SDL_GetPerformanceCounter();
}
#endif''')
rep("static int b10_make_display(", "#ifndef B24_GPU_ENGINE\nstatic int b10_make_display(")
rep("static float clip(float a,float lo,float hi)",
    "#endif /* SDL graphics owner functions excluded in GPU mode */\nstatic float clip(float a,float lo,float hi)")
before='''    if(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_GAMECONTROLLER|SDL_INIT_TIMER)<0)return 1;
    SDL_Window *window=SDL_CreateWindow("Iron Man 2 - Arena B17",SDL_WINDOWPOS_CENTERED,
                                 SDL_WINDOWPOS_CENTERED,960,544,SDL_WINDOW_SHOWN);
    if(!window){SDL_Quit();return 2;}
    SDL_Renderer *sdl=NULL;
    SDL_Texture *display=NULL;
    int vsync_requested=1,vsync_active=0,profile_error=0;
    if(!b10_make_display(window,&sdl,&display,vsync_requested,&vsync_active,&profile_error)){
        SDL_DestroyWindow(window);SDL_Quit();return 3;
    }'''
after='''#ifdef B24_GPU_ENGINE
    /* SDL gamepad/timer retained, SDL graphics subsystem not initialized:
       exactly one GPU owner (vitaGL/sceGxm). */
    if(SDL_Init(SDL_INIT_GAMECONTROLLER|SDL_INIT_TIMER)<0)return 1;
    SDL_Window *window=NULL;
    SDL_Renderer *sdl=NULL;
    SDL_Texture *display=NULL;
    int vsync_requested=0,vsync_active=0,profile_error=0;
#else
'''+before+'''
#endif'''
rep(before,after)
before='''    uint32_t *pixels=(uint32_t*)malloc(IM2_W*IM2_H*sizeof(uint32_t));
    float *zbuffer=(float*)malloc(IM2_W*IM2_H*sizeof(float));
    if(!pixels||!zbuffer){free(pixels);free(zbuffer);SDL_DestroyTexture(display);
        SDL_DestroyRenderer(sdl);SDL_DestroyWindow(window);SDL_Quit();return 5;}'''
rep(before,'''#ifdef B24_GPU_ENGINE
    /* No full CPU world frame or zbuffer allocations in GPU version. */
    uint32_t *pixels=NULL;
    float *zbuffer=NULL;
    (void)pixels;(void)zbuffer;(void)sdl;(void)display;(void)window;
#else
'''+before+'''
#endif''')
rep("    int idx=0,running=load(idx);",
'''    int idx=0,running=load(idx);
#ifdef B24_GPU_ENGINE
    if(running&&!b24_gpu_runtime_open(&b24_gpu_rt,"app0:maps/C1L1_environment.c1g2"))
        running=0;
    if(running&&!b24_gpu_runtime_set_clock(&b24_gpu_rt,b24_gpu_ticks,NULL,
                                          (double)SDL_GetPerformanceFrequency()))
        running=0;
#endif''')
before='''                  if(!b10_switch_display(window,&sdl,&display,&vsync_requested,&vsync_active,&profile_error))running=0;
                  profiler=(B10Profiler){0};'''
rep(before,"#ifndef B24_GPU_ENGINE\n"+before+"\n#endif")
before='''        if(!b24_unified_paused(&b24_game))
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
        camera.display_ms=profiler.upload_ms+profiler.copy_ms+profiler.present_ms;'''
after='''#ifdef B24_GPU_ENGINE
        /* Original B14/B16 motion, suit cycle, B24 HUD and game input state;
           C1L1 GPU scene + animated original suit + alpha B22 HUD + ONE swap. */
        if(!b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)){
            running=0;break;
        }
        frame++;
        const Uint64 t5=SDL_GetPerformanceCounter();
        const double scale=1000.0/(double)SDL_GetPerformanceFrequency();
        b10_record(&profiler,(float)((t1-t0)*scale),
                   (float)((t5-t1)*scale),0.f,0.f,0.f);
        camera.display_ms=0.f; /* no valid GPU display timer measured yet */
#else
'''+before+'''
#endif'''
rep(before,after)
before='''    SDL_DestroyTexture(display);SDL_DestroyRenderer(sdl);SDL_DestroyWindow(window);
    SDL_Quit();return 0;'''
rep(before,'''#ifdef B24_GPU_ENGINE
    b24_gpu_runtime_close(&b24_gpu_rt);
#else
    SDL_DestroyTexture(display);SDL_DestroyRenderer(sdl);SDL_DestroyWindow(window);
#endif
    SDL_Quit();return 0;''')
rep('''        frame++;
        const Uint64 t5=SDL_GetPerformanceCounter();''',
'''        frame++;
#ifdef B24_GPU_PROFILE_LOG
        if(frame%120u==0u){
            const B24CpuGpuProfile *p=&b24_gpu_rt.profile;
            fprintf(stderr,"B24 CPU ms: stream %.2f camera %.2f scene-call %.2f armor-call %.2f HUD-call %.2f swap-wall %.2f | REAL GPU BUSY UNKNOWN\\n",
                p->average_ms[B24P_MODEL_STREAM],
                p->average_ms[B24P_CAMERA_SETUP],
                p->average_ms[B24P_SCENE_CALLS],
                p->average_ms[B24P_SUIT_CALLS],
                p->average_ms[B24P_HUD_CALLS],
                p->average_ms[B24P_SWAP_WALL]);
        }
#endif
        const Uint64 t5=SDL_GetPerformanceCounter();''')

p.write_text(s)
cmake=W/"CMakeLists.txt"
body=cmake.read_text()
if "B24_GPU_SINGLE_OWNER_INTEGRATION" in body:raise RuntimeError("duplicate GPU CMake")
sources=[
 "b24_gpu_camera.c","b24_gpu_owner_vitagl.c","b24_c1_gpu_mesh.c",
 "b24_c1_gpu_vitagl.c","b24_gpu_suit_vitagl.c",
 "b24_gpu_suit_im2_adapter.c","b24_gpu_hud_bridge_vitagl.c",
 "b24_gpu_reticle.c",
 "b24_gpu_hud_native.c","b24_gpu_hud_native_vitagl.c",
 "b24_gpu_cpu_profile.c",
 "b24_gpu_runtime.c"
]
cmroot="$"+"{CMAKE_CURRENT_SOURCE_DIR}"
base=cmroot+"/b24/b24_unified/"
for name in sources:
 if not (W/"b24/b24_unified"/name).is_file():raise FileNotFoundError(name)
body+='''

# B24_GPU_SINGLE_OWNER_INTEGRATION
# Default off preserves old CPU renderer and B15/B17 regression behavior.
option(B24_ENABLE_GPU "Exclusive original-game B24 native GPU" OFF)
if(B24_ENABLE_GPU)
  if(NOT DEFINED ENV{VITASDK})
    message(FATAL_ERROR "B24_GPU_ENGINE requires VitaSDK")
  endif()
  target_compile_definitions(im2_beta PRIVATE B24_GPU_ENGINE=1)
  option(B24_ENABLE_NATIVE_HUD "GPU-native shapes/text; no HUD bitmap transfer" ON)
  if(B24_ENABLE_NATIVE_HUD)
    target_compile_definitions(im2_beta PRIVATE B24_GPU_NATIVE_HUD=1)
  endif()
  option(B24_ENABLE_GPU_PROFILE_LOG "Log CPU-side submission/vblank time; GPU BUSY unknown" OFF)
  if(B24_ENABLE_GPU_PROFILE_LOG)
    target_compile_definitions(im2_beta PRIVATE B24_GPU_PROFILE_LOG=1)
  endif()
  target_sources(im2_beta PRIVATE
'''+''.join("    "+base+f+"\n" for f in sources)+'''  )
  target_include_directories(im2_beta PRIVATE '''+cmroot+'''/src)
endif()
'''
cmake.write_text(body)
print("PASS generated original B24 main now has opt-in GPU runtime path; legacy SDL remains default")
print("No VPK built. GPU mode still untested on physical PS Vita.")
