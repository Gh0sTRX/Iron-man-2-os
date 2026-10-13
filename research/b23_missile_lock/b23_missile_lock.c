#include "b23_missile_lock.h"
#include <math.h>
#include <stddef.h>
#include <stdlib.h>

static int clampi(int v,int lo,int hi){return v<lo?lo:v>hi?hi:v;}
static int eligible(const B23Target *t,const B23Lock *s){
    return t && t->id>=0 && t->alive && t->visible && !t->occluded &&
        isfinite(t->distance) && t->distance>=0.f && t->distance<=s->max_distance &&
        isfinite(t->aim_cos) && t->aim_cos>=s->min_aim_cos && t->aim_cos<=1.f &&
        t->screen_x>=0 && t->screen_x<B22_W && t->screen_y>=0 && t->screen_y<B22_H;
}
static void clear_target(B23Lock *s){
    s->phase=B23_IDLE;s->target_id=-1;s->target_x=B22_W/2;s->target_y=B22_H/2;
    s->target_health_percent=-1.f;s->acquire_s=0.f;
}
void b23_init(B23Lock *s){
    if(!s)return;
    s->weapon=B23_REPULSOR;s->lock_button_held=0;
    s->required_s=0.45f;s->max_distance=250.f;s->min_aim_cos=0.80f;
    clear_target(s);
}
void b23_tick(B23Lock *s,B23Weapon weapon,int held,const B23Target *targets,size_t count,float dt){
    if(!s)return;
    s->weapon=weapon;s->lock_button_held=held!=0;
    if(weapon!=B23_MISSILE || !held){clear_target(s);return;}
    if(!targets)count=0;
    /* Portable bounded gameplay API: no arbitrarily huge input scans. */
    if(count>64)count=64;
    const B23Target *choice=NULL;
    if(s->target_id>=0){
        for(size_t i=0;i<count;i++)if(targets[i].id==s->target_id && eligible(&targets[i],s)){
            choice=&targets[i];break;
        }
    }
    if(!choice){
        for(size_t i=0;i<count;i++)if(eligible(&targets[i],s)){
            if(!choice || targets[i].aim_cos>choice->aim_cos ||
                (targets[i].aim_cos==choice->aim_cos && targets[i].distance<choice->distance) ||
                (targets[i].aim_cos==choice->aim_cos && targets[i].distance==choice->distance && targets[i].id<choice->id))
                choice=&targets[i];
        }
    }
    if(!choice){clear_target(s);return;}
    if(choice->id!=s->target_id){
        s->target_id=choice->id;s->acquire_s=0.f;s->phase=B23_ACQUIRING;
    }
    s->target_x=choice->screen_x;s->target_y=choice->screen_y;
    s->target_health_percent=choice->health_percent;
    /* Cap huge frame stalls: locking cannot complete in a single 10-second hitch. */
    if(isfinite(dt)&&dt>0.f)s->acquire_s+=dt>0.1f?0.1f:dt;
    if(!isfinite(s->acquire_s) || s->acquire_s<0.f)s->acquire_s=0.f;
    s->phase=s->acquire_s>=s->required_s?B23_LOCKED:B23_ACQUIRING;
}
float b23_progress(const B23Lock *s){
    if(!s || s->phase==B23_IDLE || s->weapon!=B23_MISSILE || !s->lock_button_held)return 0.f;
    if(s->phase==B23_LOCKED)return 1.f;
    if(!isfinite(s->required_s)||s->required_s<=0.f)return 0.f;
    float p=s->acquire_s/s->required_s;
    return !isfinite(p)||p<0.f?0.f:p>1.f?1.f:p;
}
void b23_prepare_b22_ui(B22UI *ui){if(ui)ui->locked=0;}
static void pixel(uint32_t *f,int s,int x,int y,uint32_t c){
    if(x>=0&&x<B22_W&&y>=0&&y<B22_H)f[(size_t)y*(size_t)s+(size_t)x]=c;
}
static void line(uint32_t *f,int s,int x0,int y0,int x1,int y1,uint32_t c){
    /* Coordinates are clamped before Bresenham to keep worst-case bounded. */
    x0=clampi(x0,-32,B22_W+32);x1=clampi(x1,-32,B22_W+32);
    y0=clampi(y0,-32,B22_H+32);y1=clampi(y1,-32,B22_H+32);
    int dx=abs(x1-x0),sx=x0<x1?1:-1,dy=-abs(y1-y0),sy=y0<y1?1:-1,err=dx+dy;
    for(;;){pixel(f,s,x0,y0,c);if(x0==x1&&y0==y1)break;
        int e=err*2;if(e>=dy){err+=dy;x0+=sx;}if(e<=dx){err+=dx;y0+=sy;}}
}
static void corners(uint32_t *f,int s,int x,int y,int radius,uint32_t c){
    int r=radius,t=7;
    line(f,s,x-r,y-r,x-r+t,y-r,c);line(f,s,x-r,y-r,x-r,y-r+t,c);
    line(f,s,x+r,y-r,x+r-t,y-r,c);line(f,s,x+r,y-r,x+r,y-r+t,c);
    line(f,s,x-r,y+r,x-r+t,y+r,c);line(f,s,x-r,y+r,x-r,y+r-t,c);
    line(f,s,x+r,y+r,x+r-t,y+r,c);line(f,s,x+r,y+r,x+r,y+r-t,c);
}
void b23_draw_missile_hud(uint32_t *f,int stride,const B23Lock *s,
                          B22Suit suit,B22UiMode mode,B22Page page){
    if(!f||!s||stride<B22_W || page!=B22_GAME ||
       s->weapon!=B23_MISSILE || !s->lock_button_held || s->phase==B23_IDLE || s->target_id<0)return;
    const int x=B22_W/2,y=B22_H/2;
    uint32_t accent=mode==B22_ORIGINAL_LAYOUT?0x3ef7e0u:
        suit==B22_WARMACHINE?0xf0a753u:0x55dff8u;
    uint32_t active=s->phase==B23_LOCKED?(suit==B22_WARMACHINE?0xffbd66u:0x70ffb0u):accent;
    int r=s->phase==B23_LOCKED?21:26;
    corners(f,stride,s->target_x,s->target_y,r,active);
    /* PSP-inspired center targeting inset, distinct from target-world marker. */
    line(f,stride,x-8,y,x-3,y,active);line(f,stride,x+3,y,x+8,y,active);
    line(f,stride,x,y-8,x,y-3,active);line(f,stride,x,y+3,x,y+8,active);
    corners(f,stride,x,y,14,accent);
    int filled=(int)(b23_progress(s)*46.f+0.5f);
    for(int i=0;i<46;i++)pixel(f,stride,x-23+i,y+23,i<filled?active:0x36515bu);
    if(s->phase==B23_LOCKED){
        line(f,stride,x-10,y-28,x+10,y-28,active);
        line(f,stride,x-3,y-30,x,y-27,active);
        line(f,stride,x,y-27,x+6,y-33,active);
    }
    /* Small enemy health rail only when HP value is known; never fabricate. */
    if(isfinite(s->target_health_percent)&&s->target_health_percent>=0.f){
        float hp=s->target_health_percent>100.f?100.f:s->target_health_percent;
        int filledhp=(int)(hp*0.36f+0.5f);
        for(int i=0;i<36;i++)pixel(f,stride,s->target_x-18+i,s->target_y-r-6,
                                   i<filledhp?active:0x36515bu);
    }
}
