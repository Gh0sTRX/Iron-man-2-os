#ifndef IM2_B7_ANIM_H
#define IM2_B7_ANIM_H
#include "renderer.h"
#include <stdint.h>
/* Prebaked from authentic .anim tracks, BDAE inverse bind matrices, and skin influences.
   This preview is original motion data, but NOT original game's runtime. */
typedef struct {float *xyz;uint32_t verts,frames,fps,duration_ms;} B7Clip;
typedef struct {B7Clip hover,walk,land,fly;float *rest;uint32_t nverts;} B7Motion;
int b7_prepare(B7Motion *m,unsigned armor,const IM2Model *model);
void b7_apply(B7Motion *m,IM2Model *model,int flying,int walking,int landing,
              unsigned frame_time_ms,unsigned elapsed_ms);
void b7_release(B7Motion *m);
#endif
