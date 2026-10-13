#include "b21_hud_canvas.h"
#include <stddef.h>
static void rect(uint32_t *p,int x,int y,int w,int h,uint32_t color){
 if(w<=0||h<=0)return;
 int xa=x<0?0:x,ya=y<0?0:y,xb=x+w>IM2_HUD_W?IM2_HUD_W:x+w;
 int yb=y+h>IM2_HUD_H?IM2_HUD_H:y+h;
 if(xa>=xb||ya>=yb)return;
 for(int j=ya;j<yb;j++)for(int i=xa;i<xb;i++)p[j*IM2_HUD_W+i]=color;
}
static int ratio(float v){if(!(v>=0))return 0;if(v>=100.f)return 100;return (int)(v+.5f);}
static void bar(uint32_t *p,int x,int y,float value,uint32_t color){
 rect(p,x-2,y-2,125,11,0x141c28u);
 rect(p,x,y,120,7,0x283442u);
 rect(p,x,y,(120*ratio(value))/100,7,color);
}
void im2_hud_render(uint32_t *pixels,const Im2HudInfo *hud,const Im2Controls *ctl,
                    int tx,int ty,int target_visible){
 if(!pixels||!hud||!ctl)return;
 bar(pixels,12,19,hud->health,0xca4444u);
 bar(pixels,12,33,hud->shield,0x4e9be0u);
 bar(pixels,12,47,hud->energy,0x4bd7d4u);
 const int cx=240,cy=129;
 uint32_t reticle=ctl->target_locked?0xf2ba56u:0xb6d9dfu;
 rect(pixels,cx-13,cy,7,1,reticle);rect(pixels,cx+7,cy,7,1,reticle);
 rect(pixels,cx,cy-13,1,7,reticle);rect(pixels,cx,cy+7,1,7,reticle);
 if(ctl->target_locked&&target_visible){
  uint32_t lock=0xffcb65u;int s=9;
  rect(pixels,tx-s,ty-s,6,2,lock);rect(pixels,tx-s,ty-s,2,6,lock);
  rect(pixels,tx+s-5,ty-s,6,2,lock);rect(pixels,tx+s-1,ty-s,2,6,lock);
  rect(pixels,tx-s,ty+s-1,6,2,lock);rect(pixels,tx-s,ty+s-5,2,6,lock);
  rect(pixels,tx+s-5,ty+s-1,6,2,lock);rect(pixels,tx+s-1,ty+s-5,2,6,lock);
  if(hud->enemy_hp>=0.f)bar(pixels,tx-45,ty-23,hud->enemy_hp,0xf3a75eu);
 }
 if(ctl->state==IM2_PAUSED){
  rect(pixels,92,55,296,158,0x07121eu);
  rect(pixels,94,57,292,3,0x42bbd4u);
  int y=ctl->menu==IM2_MENUMAIN?113:86+ctl->selected_option*24;
  rect(pixels,107,y,6,10,0xf7c775u);
  /* Menu labels/option text use existing original Vita renderer write_text(). */
 }
}
