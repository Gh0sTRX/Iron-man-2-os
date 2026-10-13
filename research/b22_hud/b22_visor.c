#include "b22_visor.h"
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
static int clampi(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
static int pct(float f){if(!isfinite(f)||f<=0.f)return 0;if(f>=100.f)return 100;return (int)(f+.5f);}
static void pixel(uint32_t *f,int stride,int x,int y,uint32_t col){
    if(x>=0&&x<B22_W&&y>=0&&y<B22_H)f[(size_t)y*stride+x]=col;
}
static void bar(uint32_t *f,int stride,int x,int y,int w,int h,float amount,uint32_t color){
    int filled=pct(amount)*w/100;
    for(int j=0;j<h;j++)for(int i=0;i<w;i++)pixel(f,stride,x+i,y+j,i<filled?color:0x24303cu);
    for(int i=-1;i<=w;i++){pixel(f,stride,x+i,y-1,0x6d8795u);pixel(f,stride,x+i,y+h,0x6d8795u);}
}
static void line(uint32_t *f,int s,int x0,int y0,int x1,int y1,uint32_t color){
    int dx=abs(x1-x0),sx=x0<x1?1:-1,dy=-abs(y1-y0),sy=y0<y1?1:-1,err=dx+dy;
    for(;;){pixel(f,s,x0,y0,color);if(x0==x1&&y0==y1)break;int e=2*err;
        if(e>=dy){err+=dy;x0+=sx;}if(e<=dx){err+=dx;y0+=sy;}}
}
static void ring(uint32_t *f,int s,int x,int y,int r,uint32_t color){
    for(int i=0;i<40;i++){
        float a=(float)i*6.28318530718f/40.f,b=(float)(i+1)*6.28318530718f/40.f;
        line(f,s,x+(int)roundf(cosf(a)*r),y+(int)roundf(sinf(a)*r),
                 x+(int)roundf(cosf(b)*r),y+(int)roundf(sinf(b)*r),color);
    }
}
B22Palette b22_palette(B22Suit suit){
    if(suit==B22_WARMACHINE)return (B22Palette){0xb6bf9du,0xf0a753u,0xe15c46u,0x526c69u,0x39cfeau};
    return (B22Palette){0x55dff8u,0xe8bb5du,0xfa6555u,0x477ba9u,0x39cfeau};
}
static void legacy(uint32_t *f,int s,const B22UI *ui){
    /* Screenshot-guided iOS legacy LAYOUT. Does not reproduce original art files. */
    line(f,s,17,20,160,20,0xd2ffffu);line(f,s,17,20,11,28,0xd2ffffu);
    bar(f,s,20,27,130,7,ui->armor,0x39cfeau);
    if(ui->show_objective){line(f,s,165,16,299,16,0x6b96a3u);}
    if(ui->show_minimap){
        ring(f,s,44,222,31,0x247eaeu);ring(f,s,44,222,25,0x42c2e4u);
        line(f,s,44,212,44,231,0xbdeff6u);line(f,s,34,222,54,222,0xbdeff6u);
    }
    ring(f,s,442,224,23,0x247eaeu);ring(f,s,442,224,17,0x31b9e3u);
    bar(f,s,392,249,77,5,ui->charge,0x39cfeau);
}
static void suit_layer(uint32_t *f,int s,const B22UI *ui,B22Palette p){
    int long_side=ui->mode==B22_IMMERSIVE?91:43;
    line(f,s,4,50,4,50+long_side,p.suit_main);
    line(f,s,4,50,14,50,p.suit_main);
    line(f,s,475,50,475,50+long_side,p.suit_main);
    line(f,s,464,50,475,50,p.suit_main);
    line(f,s,10,258,90,258,p.soft);line(f,s,391,258,469,258,p.soft);
    bar(f,s,169,246,64,5,ui->shield,p.suit_main);
    bar(f,s,246,246,64,5,ui->energy,p.suit_accent);
    if(ui->mode==B22_IMMERSIVE){
        for(int k=0;k<3;k++){
            line(f,s,9,177+k*13,18+k*4,173+k*13,p.soft);
            line(f,s,471,177+k*13,462-k*4,173+k*13,p.soft);
        }
        line(f,s,126,7,161,7,p.suit_main);
        line(f,s,319,7,354,7,p.suit_main);
    }
    if(ui->damage_warning){
        line(f,s,4,18,29,18,p.alert);line(f,s,4,18,4,37,p.alert);
        line(f,s,475,18,449,18,p.alert);line(f,s,475,18,475,37,p.alert);
    }
}
static void lock_brackets(uint32_t *f,int s,int x,int y,uint32_t color){
    x=clampi(x,-15,495);y=clampi(y,-15,287);
    int r=13;
    line(f,s,x-r,y-r,x-r+8,y-r,color);line(f,s,x-r,y-r,x-r,y-r+8,color);
    line(f,s,x+r,y-r,x+r-8,y-r,color);line(f,s,x+r,y-r,x+r,y-r+8,color);
    line(f,s,x-r,y+r,x-r+8,y+r,color);line(f,s,x-r,y+r,x-r,y+r-8,color);
    line(f,s,x+r,y+r,x+r-8,y+r,color);line(f,s,x+r,y+r,x+r,y+r-8,color);
}
static void page_panel(uint32_t *f,int s,const B22UI *ui,B22Palette p){
    if(ui->page==B22_GAME)return;
    int x=103,y=59,w=274,h=151;
    for(int j=0;j<h;j++)for(int i=0;i<w;i++){
        if(i==0||j==0||i==w-1||j==h-1)pixel(f,s,x+i,y+j,p.suit_main);
        else pixel(f,s,x+i,y+j,0x111b28u);
    }
    line(f,s,115,90,365,90,p.soft);
    if(ui->page==B22_PAUSE)line(f,s,133,118,347,118,p.suit_accent);
    if(ui->page==B22_MAIN_MENU)ring(f,s,240,127,48,p.suit_main);
    if(ui->page==B22_UPGRADE){for(int k=0;k<4;k++)bar(f,s,142,101+21*k,190,7,75.f-(float)k*18,p.suit_accent);}
    if(ui->page==B22_RESULTS)ring(f,s,240,132,38,ui->mission_success?p.suit_main:p.alert);
    /* Real original menu SWF and font atlas are not recovered. Use a future font adapter. */
}
void b22_draw_hud(uint32_t *frame,int stride,const B22UI *ui){
    if(!frame||!ui||stride<B22_W)return;
    B22Palette palette=b22_palette(ui->suit);
    if(ui->page==B22_GAME){
        legacy(frame,stride,ui);
        if(ui->mode!=B22_ORIGINAL_LAYOUT)suit_layer(frame,stride,ui,palette);
        if(ui->locked)lock_brackets(frame,stride,ui->target_x,ui->target_y,
                                     ui->mode==B22_ORIGINAL_LAYOUT?0x3ef7e0u:palette.suit_accent);
    }else{page_panel(frame,stride,ui,palette);}
}
