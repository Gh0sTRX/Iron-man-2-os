#ifndef IM2_B21_HUD_CANVAS_H
#define IM2_B21_HUD_CANVAS_H
#include <stdint.h>
#include "b21_control_lab.h"
#define IM2_HUD_W 480
#define IM2_HUD_H 272
/* 480x272 B17 CPU-fallback frame overlay, reused later by GPU display. */
void im2_hud_render(uint32_t *pixels,const Im2HudInfo *hud,const Im2Controls *ctl,
                    int target_x,int target_y,int target_visible);
#endif
