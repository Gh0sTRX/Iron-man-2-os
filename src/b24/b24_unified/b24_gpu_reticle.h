#ifndef B24_GPU_RETICLE_H
#define B24_GPU_RETICLE_H
#include <stdint.h>
/* 480x272 B22 UI space, irrespective of 960x544 GPU physical viewport.
 * Shoulder->chase blend is the SAME B24.camera_base.shoulder_to_chase. */
typedef struct {float x,y;} B24ReticlePoint;
B24ReticlePoint b24_reticle_position(float shoulder_to_chase);
void b24_reticle_draw(uint32_t *rgb,int stride,float shoulder_to_chase,
                      int missile_lock,int paused);
#endif
