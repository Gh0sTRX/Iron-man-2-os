#include "b23_missile_lock.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define STRIDE 496
#define FB_COUNT ((size_t)STRIDE*B22_H)
static uint32_t buf[FB_COUNT+2];
static B23Target target(int id,float aim,int x,int y){
    B23Target t={0};t.id=id;t.alive=1;t.visible=1;t.occluded=0;
    t.distance=65.f;t.aim_cos=aim;t.health_percent=65.f;t.screen_x=x;t.screen_y=y;
    return t;
}
static void reset_frame(void){for(size_t i=0;i<FB_COUNT+2;i++)buf[i]=0x101010u;
    buf[0]=0x12345678u;buf[FB_COUNT+1]=0xfedcba98u;}
static void frame_guards(void){
    assert(buf[0]==0x12345678u && buf[FB_COUNT+1]==0xfedcba98u);
    for(int y=0;y<B22_H;y++)for(int x=B22_W;x<STRIDE;x++)
        assert(buf[1+(size_t)y*STRIDE+x]==0x101010u);
}
int main(void){
    B23Lock s;b23_init(&s);
    assert(s.phase==B23_IDLE && s.target_id==-1 && b23_progress(&s)==0.f);
    B23Target a[3]={target(10,.95f,233,119),target(20,.90f,270,110),target(30,.65f,290,119)};
    for(int w=0;w<4;w++)if(w!=B23_MISSILE){
        b23_tick(&s,(B23Weapon)w,1,a,3,1.f);
        assert(s.phase==B23_IDLE && s.target_id==-1);
    }
    b23_tick(&s,B23_MISSILE,0,a,3,.1f);
    assert(s.phase==B23_IDLE);
    b23_tick(&s,B23_MISSILE,1,a,3,.1f);
    assert(s.phase==B23_ACQUIRING && s.target_id==10);
    assert(b23_progress(&s)>0.21f && b23_progress(&s)<0.23f);
    /* Stronger new target must not steal stable lock. */
    a[1].aim_cos=.999f;
    for(int i=0;i<4;i++)b23_tick(&s,B23_MISSILE,1,a,3,.1f);
    assert(s.phase==B23_LOCKED && s.target_id==10);
    assert(b23_progress(&s)==1.f);
    /* Projectile state must NEVER cause a camera snap; no camera variables exposed. */
    B22UI ui={0};ui.locked=1;b23_prepare_b22_ui(&ui);assert(ui.locked==0);
    reset_frame();b23_draw_missile_hud(buf+1,STRIDE,&s,B22_IRONMAN,B22_HYBRID,B22_GAME);
    frame_guards();
    assert(buf[1+(size_t)136*STRIDE+235]!=0x101010u);
    reset_frame();b23_draw_missile_hud(buf+1,STRIDE,&s,B22_WARMACHINE,B22_HYBRID,B22_PAUSE);
    frame_guards();assert(buf[1+(size_t)136*STRIDE+235]==0x101010u);
    a[0].alive=0;
    b23_tick(&s,B23_MISSILE,1,a,3,.1f);
    assert(s.phase==B23_ACQUIRING && s.target_id==20);
    assert(b23_progress(&s)>0.f && b23_progress(&s)<1.f);
    a[1].occluded=1;
    b23_tick(&s,B23_MISSILE,1,a,3,.1f);
    assert(s.target_id==-1 && s.phase==B23_IDLE);
    a[0].alive=1;a[1].occluded=0;
    a[0].distance=300.f;a[1].screen_x=-10;
    b23_tick(&s,B23_MISSILE,1,a,3,.1f);
    assert(s.target_id==-1);
    a[0].distance=60.f;a[1].screen_x=270;
    b23_tick(&s,B23_MISSILE,1,a,3,INFINITY);
    assert(s.phase==B23_ACQUIRING && b23_progress(&s)==0.f);
    b23_tick(&s,B23_MISSILE,1,a,3,120.f);
    assert(s.phase==B23_ACQUIRING && b23_progress(&s)<.23f);
    b23_tick(&s,B23_REPULSOR,1,a,3,.2f);
    assert(s.phase==B23_IDLE && s.target_id==-1);
    b23_tick(&s,B23_MISSILE,1,a,3,.1f);
    b23_tick(&s,B23_MISSILE,0,a,3,.1f);
    assert(s.phase==B23_IDLE);
    /* Deterministic fuzz including weird/offscreen coordinates and no candidate input. */
    for(int n=0;n<300;n++){
        B23Target t=target(n,.81f,-100+n*3,400-n*2);
        t.distance=n%7==0?NAN:(float)(n%300);
        t.alive=n%13!=0;t.visible=n%11!=0;t.occluded=n%17==0;
        b23_tick(&s,B23_MISSILE,1,&t,1,n%3==0?NAN:0.016f);
        reset_frame();
        b23_draw_missile_hud(buf+1,STRIDE,&s,
            n%2==0?B22_IRONMAN:B22_WARMACHINE,(B22UiMode)(n%3),B22_GAME);
        frame_guards();
    }
    b23_tick(&s,B23_MISSILE,1,NULL,1000,.1f);
    assert(s.target_id==-1);
    puts("PASS B23: missiles-only acquisition, stable ID, loss/reset, elapsed-time guard, B22 adapter, 300 framebuffer guard tests");
    return 0;
}
