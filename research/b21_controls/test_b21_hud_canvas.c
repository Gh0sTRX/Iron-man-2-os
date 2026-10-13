#include "b21_hud_canvas.h"
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
static uint32_t frame[IM2_HUD_W*IM2_HUD_H+2];
int main(void){
 frame[0]=0xfeedbeefu;frame[IM2_HUD_W*IM2_HUD_H+1]=0xdeadbeefu;
 Im2HudInfo hud={.health=62,.shield=50,.energy=20,.enemy_hp=65};
 Im2Controls c;im2_controls_init(&c);
 im2_hud_render(frame+1,&hud,&c,480,-10,0);
 assert(frame[1+19*IM2_HUD_W+12]==0xca4444u);
 assert(frame[1+33*IM2_HUD_W+12]==0x4e9be0u);
 assert(frame[1+47*IM2_HUD_W+12]==0x4bd7d4u);
 c.target_locked=1;c.target_id=19;
 im2_hud_render(frame+1,&hud,&c,475,4,1);
 c.state=IM2_PAUSED;c.menu=IM2_MENUOPTIONS;c.selected_option=4;
 im2_hud_render(frame+1,&hud,&c,240,125,1);
 assert(frame[1+57*IM2_HUD_W+94]==0x42bbd4u);
 assert(frame[0]==0xfeedbeefu && frame[IM2_HUD_W*IM2_HUD_H+1]==0xdeadbeefu);
 puts("PASS B21 HUD: health/shield/energy, lock markers, clipped edges and pause overlay");
}
