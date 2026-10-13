#include "b21_control_lab.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
static float cap(float x,float a,float b){return !isfinite(x)?0.f:(x<a?a:x>b?b:x);}
static int just(Im2Controls *c,Im2Button bit){return (c->pressed & (uint32_t)bit)!=0;}
static float dot(Im2Point a,Im2Point b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static float len(Im2Point a){return sqrtf(dot(a,a));}
static Im2Point sub(Im2Point a,Im2Point b){Im2Point p={a.x-b.x,a.y-b.y,a.z-b.z};return p;}
static void toggle_selected(Im2Controls *c){
 switch(c->selected_option){
 case IM2_SETTING_MUSIC:c->settings.music=!c->settings.music;break;
 case IM2_SETTING_SFX:c->settings.sfx=!c->settings.sfx;break;
 case IM2_SETTING_INVERT_X:c->settings.invert_x=!c->settings.invert_x;break;
 case IM2_SETTING_INVERT_Y:c->settings.invert_y=!c->settings.invert_y;break;
 case IM2_SETTING_SENSITIVITY:c->settings.camera_sensitivity=c->settings.camera_sensitivity>=1.5f?.7f:c->settings.camera_sensitivity+.2f;break;
 default:break;
 }
}
void im2_controls_init(Im2Controls *c){if(!c)return;memset(c,0,sizeof *c);c->state=IM2_PLAYING;c->target_id=-1;c->settings.music=1;c->settings.sfx=1;c->settings.camera_sensitivity=1.f;}
void im2_controls_tick(Im2Controls *c,uint32_t buttons,float lx,float ly,float rx,float ry){
 if(!c)return;
 c->pressed=buttons & ~c->held;c->released=c->held & ~buttons;c->held=buttons;
 c->fire=0;c->melee=0;c->boost=0;c->interact=0;c->flight_toggle=0;c->vertical=0;c->weapon_delta=0;
 c->move_x=c->move_y=c->cam_x=c->cam_y=0;
 if(just(c,IM2_BT_START)){
  c->state=c->state==IM2_PLAYING?IM2_PAUSED:IM2_PLAYING;
  c->menu=IM2_MENUMAIN;c->selected_option=0;
 }
 if(c->state==IM2_PAUSED){
  if(just(c,IM2_BT_CIRCLE)){if(c->menu==IM2_MENUOPTIONS)c->menu=IM2_MENUMAIN;else c->state=IM2_PLAYING;}
  else if(c->menu==IM2_MENUMAIN){if(just(c,IM2_BT_CROSS))c->menu=IM2_MENUOPTIONS;}
  else {
   if(just(c,IM2_BT_DUP))c->selected_option=(c->selected_option+IM2_SETTING_COUNT-1)%IM2_SETTING_COUNT;
   if(just(c,IM2_BT_DDOWN))c->selected_option=(c->selected_option+1)%IM2_SETTING_COUNT;
   if(just(c,IM2_BT_CROSS)||just(c,IM2_BT_DLEFT)||just(c,IM2_BT_DRIGHT))toggle_selected(c);
  }
  return;
 }
 c->move_x=cap(lx,-1,1);c->move_y=cap(ly,-1,1);
 c->cam_x=(c->settings.invert_x?-1.f:1.f)*cap(rx,-1,1)*c->settings.camera_sensitivity;
 c->cam_y=(c->settings.invert_y?-1.f:1.f)*cap(ry,-1,1)*c->settings.camera_sensitivity;
 c->fire=(buttons&IM2_BT_R)!=0;
 c->melee=just(c,IM2_BT_SQUARE);
 c->boost=(buttons&IM2_BT_TRIANGLE)!=0;
 c->interact=just(c,IM2_BT_CROSS);
 c->flight_toggle=just(c,IM2_BT_CIRCLE);
 c->vertical=((buttons&IM2_BT_DUP)!=0)-((buttons&IM2_BT_DDOWN)!=0);
 c->weapon_delta=just(c,IM2_BT_DRIGHT)-just(c,IM2_BT_DLEFT);
 if(!(buttons&IM2_BT_L)){c->target_locked=0;c->target_id=-1;}
}
int im2_controls_lock_target(Im2Controls *c,Im2Point origin,Im2Point view,
                             const Im2Target *targets,int count,float max_dist,float cone_cos){
 if(!c)return -1;
 if(c->state==IM2_PAUSED||!(c->held&IM2_BT_L))return -1;
 if(!targets||count<0||count>IM2_MAX_TARGETS||!isfinite(max_dist)||max_dist<=0.f)return -1;
 float vlen=len(view);if(!isfinite(vlen)||vlen<1e-5f)return -1;
 if(c->target_locked){
  for(int i=0;i<count;i++)if(targets[i].id==c->target_id && targets[i].alive && targets[i].visible){
   Im2Point rel=sub(targets[i].pos,origin);float d=len(rel);
   if(isfinite(d)&&d<=max_dist && d>1e-5f){return c->target_id;}
  }
 }
 int id=-1;float best=-1e30f;
 for(int i=0;i<count;i++){
  if(!targets[i].alive||!targets[i].visible)continue;
  Im2Point rel=sub(targets[i].pos,origin);float d=len(rel);
  if(!isfinite(d)||d<1e-5f||d>max_dist)continue;
  float facing=dot(rel,view)/(d*vlen);
  if(!isfinite(facing)||facing<cone_cos)continue;
  float score=facing*6.f-d/max_dist;
  if(score>best){best=score;id=targets[i].id;}
 }
 c->target_id=id;c->target_locked=id>=0;
 return id;
}
void im2_hud_normalized(const Im2HudInfo *h,float *health,float *shield,float *energy){
 if(health)*health=h?cap(h->health,0.f,100.f)*.01f:0.f;
 if(shield)*shield=h?cap(h->shield,0.f,100.f)*.01f:0.f;
 if(energy)*energy=h?cap(h->energy,0.f,100.f)*.01f:0.f;
}
