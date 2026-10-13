#include "b21_control_lab.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 Im2Controls c;im2_controls_init(&c);
 assert(c.state==IM2_PLAYING&&c.target_id==-1&&c.settings.music&&c.settings.sfx);
 im2_controls_tick(&c,IM2_BT_R|IM2_BT_L|IM2_BT_DUP|IM2_BT_SQUARE,.5f,-.4f,.3f,.25f);
 assert(c.fire&&c.melee&&c.vertical==1&&c.move_x>.49f);
 Im2Target t[]={{11,1,1,{0,10,0}},{22,1,1,{2,8,0}},{33,1,0,{0,3,0}}};
 Im2Point o={0,0,0},v={0,1,0};
 int id=im2_controls_lock_target(&c,o,v,t,3,25.f,.8f);
 assert(id==11&&c.target_locked);
 t[1].pos=(Im2Point){0,4,0};
 assert(im2_controls_lock_target(&c,o,v,t,3,25.f,.8f)==11);
 t[0].alive=0;
 assert(im2_controls_lock_target(&c,o,v,t,3,25.f,.8f)==22);
 im2_controls_tick(&c,IM2_BT_START,0,0,0,0);
 assert(c.state==IM2_PAUSED&&c.fire==0&&c.vertical==0);
 im2_controls_tick(&c,0,0,0,0,0);
 im2_controls_tick(&c,IM2_BT_CROSS,0,0,0,0);assert(c.menu==IM2_MENUOPTIONS);
 im2_controls_tick(&c,0,0,0,0,0);
 im2_controls_tick(&c,IM2_BT_CROSS,0,0,0,0);assert(!c.settings.music);
 im2_controls_tick(&c,0,0,0,0,0);
 im2_controls_tick(&c,IM2_BT_DDOWN,0,0,0,0);
 im2_controls_tick(&c,0,0,0,0,0);
 im2_controls_tick(&c,IM2_BT_CROSS,0,0,0,0);assert(!c.settings.sfx);
 im2_controls_tick(&c,0,0,0,0,0);
 im2_controls_tick(&c,IM2_BT_CIRCLE,0,0,0,0);assert(c.menu==IM2_MENUMAIN);
 im2_controls_tick(&c,0,0,0,0,0);
 im2_controls_tick(&c,IM2_BT_START,0,0,0,0);assert(c.state==IM2_PLAYING);
 im2_controls_tick(&c,IM2_BT_R|IM2_BT_DLEFT,0,0,0,0);
 assert(c.fire&&c.weapon_delta==-1);
 im2_controls_tick(&c,0,0,0,0,0);
 assert(!c.fire&&c.target_id==-1);
 Im2HudInfo h={.health=150,.shield=-3,.energy=NAN};float hp,sp,ep;
 im2_hud_normalized(&h,&hp,&sp,&ep);
 assert(hp==1.f&&sp==0.f&&ep==0.f);
 puts("PASS B21 controls: lock persistence/reacquire, pause/settings, shoulder fire, analog, HUD clamps");
}
