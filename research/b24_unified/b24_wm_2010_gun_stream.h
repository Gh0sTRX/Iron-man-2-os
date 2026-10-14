#ifndef B24_WM_2010_GUN_STREAM_H
#define B24_WM_2010_GUN_STREAM_H
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
/* Original model-local BRES WORLD matrices (inside character root), not
   game-world muzzle coordinates until a verified character transform is
   composed. Source graph proven, exact fired-muzzle identity UNPROVEN.
   Original fixed node order:
   Gun01, Gun02, Gun03, Gun04, DummyE_Green_Gun.
   LE IM2K <4sIIII>, 5*16 float32 matrices per timestamp, 20Hz + final.
   No complete clip RAM preload. NOT included in any current G8 VPK. */
#define B24_WM_GUN_NODES 5u
#define B24_WM_GUN_MAT_FLOATS 16u
#define B24_WM_GUN_FRAME_FLOATS (B24_WM_GUN_NODES*B24_WM_GUN_MAT_FLOATS)
typedef struct {
 FILE *file;
 float frame_a[B24_WM_GUN_FRAME_FLOATS];
 float frame_b[B24_WM_GUN_FRAME_FLOATS];
 uint32_t frames,duration_ms,segment;
 int segment_valid;
} B24WM2010GunStream;
int b24_wm_gun_stream_open(B24WM2010GunStream *s,const char *root,
                           const char *basename);
int b24_wm_gun_stream_sample(B24WM2010GunStream *s,uint32_t time_ms,
                             int loop,float world_matrices[5][16]);
void b24_wm_gun_stream_close(B24WM2010GunStream *s);
#endif
