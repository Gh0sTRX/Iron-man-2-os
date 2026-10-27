#ifndef B24_GPU_CPU_PROFILE_H
#define B24_GPU_CPU_PROFILE_H
#include <stdint.h>
/* This instrument reports CPU-thread WALL TIMES around graphics commands.
 * It does NOT report true GPU occupancy, GPU busy cycles, shader time or FPS.
 * Swap wall time can include VSync or CPU/GPU synchronization stalls. */
typedef enum {
 B24P_MODEL_STREAM=0,B24P_CAMERA_SETUP=1,
 B24P_SCENE_CALLS=2,B24P_SUIT_CALLS=3,
 B24P_HUD_CALLS=4,B24P_SWAP_WALL=5,
 B24P_COUNT=6
} B24CpuGpuPhase;
typedef uint64_t (*B24GpuTicksFn)(void *userdata);
typedef struct {
 B24GpuTicksFn ticks;
 void *userdata;
 double frequency_hz;
 uint64_t previous_tick;
 double last_ms[B24P_COUNT],average_ms[B24P_COUNT],max_ms[B24P_COUNT];
 uint64_t frames;
 int enabled,frame_open,next_phase;
 int actual_gpu_timing_available; /* Always 0 until genuine GXM counters validated */
} B24CpuGpuProfile;
int b24_gpu_profile_set_clock(B24CpuGpuProfile *p,B24GpuTicksFn callback,
                               void *userdata,double ticks_per_second);
void b24_gpu_profile_begin(B24CpuGpuProfile *p);
void b24_gpu_profile_phase(B24CpuGpuProfile *p,B24CpuGpuPhase phase);
#endif
