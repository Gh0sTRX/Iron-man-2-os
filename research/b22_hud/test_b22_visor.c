#include "b22_visor.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#define LEN (B22_W*B22_H)
static uint32_t pixels[LEN+2], baseline[LEN];
static void start(void){memset(pixels,0,sizeof pixels);pixels[0]=0x4badcafe;pixels[LEN+1]=0xdeadbaba;}
static void guards(void){assert(pixels[0]==0x4badcafe && pixels[LEN+1]==0xdeadbaba);}
static B22UI state(B22Suit suit,B22UiMode mode){
    B22UI ui={0};ui.suit=suit;ui.page=B22_GAME;ui.mode=mode;ui.armor=78;ui.shield=67;ui.energy=54;
    ui.charge=39;ui.locked=1;ui.target_x=240;ui.target_y=131;ui.show_minimap=1;ui.show_objective=1;
    return ui;
}
int main(void){
    B22UI ui=state(B22_IRONMAN,B22_ORIGINAL_LAYOUT);
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    memcpy(baseline,pixels+1,sizeof baseline);
    assert(pixels[1+27*B22_W+20]==0x39cfeau);
    assert(pixels[1+131*B22_W+240]==0);
    B22UI wm=state(B22_WARMACHINE,B22_ORIGINAL_LAYOUT);
    start();b22_draw_hud(pixels+1,B22_W,&wm);guards();
    assert(memcmp(pixels+1,baseline,sizeof baseline)==0);
    ui.mode=B22_HYBRID;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    assert(pixels[1+50*B22_W+4]==b22_palette(B22_IRONMAN).suit_main);
    assert(pixels[1+131*B22_W+240]==0);
    uint32_t cyan=pixels[1+50*B22_W+4];
    ui.suit=B22_WARMACHINE;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    assert(pixels[1+50*B22_W+4]!=cyan);
    assert(pixels[1+50*B22_W+4]==b22_palette(B22_WARMACHINE).suit_main);
    ui.mode=B22_IMMERSIVE;ui.target_x=-20;ui.target_y=280;ui.damage_warning=1;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    ui.page=B22_PAUSE;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    assert(pixels[1+59*B22_W+103]!=0);
    ui.page=B22_MAIN_MENU;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    ui.page=B22_UPGRADE;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    ui.page=B22_RESULTS;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    ui.page=B22_GAME;ui.mode=B22_IMMERSIVE;ui.target_x=500;ui.target_y=-100;
    ui.armor=NAN;ui.shield=-1.f;ui.energy=200.f;ui.charge=NAN;
    start();b22_draw_hud(pixels+1,B22_W,&ui);guards();
    for(int n=0;n<200;n++){
        ui.suit=n&1?B22_IRONMAN:B22_WARMACHINE;
        ui.mode=(B22UiMode)(n%3);ui.page=(B22Page)(n%5);
        ui.target_x=n*11-900;ui.target_y=500-n*7;
        ui.armor=(float)(n-30);ui.shield=(float)(n*3);ui.energy=n&1?INFINITY:-INFINITY;
        b22_draw_hud(pixels+1,B22_W,&ui);guards();
    }
    assert(b22_palette(B22_IRONMAN).suit_main!=b22_palette(B22_WARMACHINE).suit_main);
    puts("PASS B22 VISOR: classic fidelity layout, distinct suits, hybrid/immersive, menus, clipping/guards, 200 fuzz cases");
}
