#include "b24_gpu_hud_native.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B24NativeHudGeometry g;unsigned largest=0;
 for(int page=0;page<5;page++)for(int mode=0;mode<3;mode++)for(int suit=0;suit<2;suit++)
  for(int options=0;options<2;options++)for(int state=0;state<4;state++){
   B24Unified game={0};game.hud.page=(B22Page)page;game.hud.mode=(B22UiMode)mode;game.hud.suit=(B22Suit)suit;
   game.hud.armor=90;game.hud.energy=100;game.hud.shield=100;game.hud.charge=100;
   game.controls.menu=options?IM2_MENUOPTIONS:IM2_MENUMAIN;game.controls.selected_option=4;
   game.controls.settings.camera_sensitivity=2;game.speed_fx.enabled=1;game.speed_fx.strength=1;
   game.missile.phase=B23_LOCKED;game.missile.target_health_percent=75;
   game.missile.target_x=240;game.missile.target_y=136;
   assert(b24_native_hud_build(&g,&game));
   b24_native_hud_test_opponent(&g,state!=0,state>=2,state==3?0:75,state==3?0:90);
   assert(!g.overflow&&g.count<=B24_NATIVE_HUD_VERTICES&&g.count%3==0);
   if(g.count>largest)largest=g.count;
   for(unsigned i=0;i<g.count;i++)assert(isfinite(g.vertices[i].x)&&isfinite(g.vertices[i].y));
  }
 printf("PASS test-opponent HUD label/bars in240 page/mode/status combinations; maximum %u/%u vertices\n",largest,B24_NATIVE_HUD_VERTICES);return 0;
}
