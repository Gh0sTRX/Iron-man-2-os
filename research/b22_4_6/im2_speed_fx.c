#include "im2_speed_fx.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
static float cap(float x,float lo,float hi){return !isfinite(x)?lo:x<lo?lo:x>hi?hi:x;}
void im2_speed_fx_init(Im2SpeedFx *s){if(s)memset(s,0,sizeof(*s));}
void im2_speed_fx_step(Im2SpeedFx *s,Im2FlightStage stage,int rush_enter,float dt){
    if(!s)return;
    dt=cap(dt,0.f,.05f);
    s->enabled=stage==IM2_FLIGHT_RUSH;
    if(!s->enabled){s->strength=0.f;s->entry_pulse=0.f;return;}
    if(rush_enter)s->entry_pulse=1.f;
    s->entry_pulse=fmaxf(0.f,s->entry_pulse-3.5f*dt);
    s->strength+= (1.f-s->strength)*(1.f-expf(-4.8f*dt));
    s->strength=cap(s->strength,0.f,1.f);
    s->ticks++;
}
static void px(uint32_t *f,int stride,int x,int y,uint32_t color){
    if(x>=0&&x<IM2_SPEED_W&&y>=0&&y<IM2_SPEED_H)f[(size_t)y*stride+x]=color;
}
int im2_speed_fx_draw(uint32_t *f,int stride,const Im2SpeedFx *s,int wm){
    if(!f||stride<IM2_SPEED_W||!s||!s->enabled||s->strength<.03f)return 0;
    /* Dedicated cheap lines at side edges. Zero full-screen reads; no ghosted frames. */
    int count=(int)(8.f+12.f*s->strength);
    if(count>20)count=20;
    uint32_t seed=0x1234567u^(s->ticks*2654435761u);
    uint32_t color=wm?0xb9a17du:0x62bad0u;
    for(int i=0;i<count;i++){
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        int x=6+(int)(seed%63u);
        if(i&1)x=IM2_SPEED_W-1-x;
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        int y=22+(int)(seed%221u);
        int len=8+(int)(11.f*s->strength)+(int)(seed%11u);
        for(int k=0;k<len;k++){
            int horizontal=(x<IM2_SPEED_W/2)?-k/3:k/3;
            px(f,stride,x+horizontal,y+k,color);
        }
    }
    return count;
}
