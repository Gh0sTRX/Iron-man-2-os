#include "b8_combat.h"
#include "renderer.h"
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define CLAMP(x,l,h) ((x)<(l)?(l):((x)>(h)?(h):(x)))
#define COL(r,g,b) (0xff000000u|((unsigned)(r)<<16)|((unsigned)(g)<<8)|(unsigned)(b))
static const float targets[3][2]={{380,137},{325,190},{400,98}};
static void dot(uint32_t*p,int x,int y,uint32_t col){if(x>=0&&x<IM2_W&&y>=0&&y<IM2_H)p[y*IM2_W+x]=col;}
static void ln(uint32_t*p,int x0,int y0,int x1,int y1,uint32_t col){
    int dx=abs(x1-x0),sx=x0<x1?1:-1,dy=-abs(y1-y0),sy=y0<y1?1:-1,err=dx+dy;
    for(int n=0;n<1024;n++){dot(p,x0,y0,col);if(x0==x1&&y0==y1)break;int e2=2*err;if(e2>=dy){err+=dy;x0+=sx;}if(e2<=dx){err+=dx;y0+=sy;}}
}
static void circ(uint32_t*p,int cx,int cy,int radius,uint32_t color){
    int x=radius,y=0,d=1-radius;
    while(x>=y){
      dot(p,cx+x,cy+y,color);dot(p,cx+y,cy+x,color);
      dot(p,cx-y,cy+x,color);dot(p,cx-x,cy+y,color);
      dot(p,cx-x,cy-y,color);dot(p,cx-y,cy-x,color);
      dot(p,cx+y,cy-x,color);dot(p,cx+x,cy-y,color);
      y++;if(d<=0)d+=2*y+1;else{x--;d+=2*(y-x)+1;}
    }
}
static void number(uint32_t*p,int x,int y,int n,uint32_t color){
    static const unsigned char g[10][5]={{7,5,5,5,7},{2,6,2,2,7},{7,1,7,4,7},
         {7,1,7,1,7},{5,5,7,1,1},{7,4,7,1,7},{7,4,7,5,7},{7,1,1,1,1},
         {7,5,7,5,7},{7,5,7,1,7}};
    if(n<0)n=0;
    if(n>999)n=999;
    int digit[3]={n/100,(n/10)%10,n%10};
    for(int d=0;d<3;d++)for(int row=0;row<5;row++)for(int col=0;col<3;col++)
        if(g[digit[d]][row]&(1<<(2-col)))for(int yy=0;yy<2;yy++)for(int xx=0;xx<2;xx++)
            dot(p,x+d*9+col*2+xx,y+row*2+yy,color);
}
void b8_get_target(const B8Combat*c,float*x,float*y){
  unsigned idx=c->stage<3?c->stage:2;
  if(x)*x=targets[idx][0];
  if(y)*y=targets[idx][1];
}
void b8_init(B8Combat*c){
    memset(c,0,sizeof(*c));c->aim_x=340.0f;c->aim_y=137.0f;
}
void b8_update(B8Combat*c,float delta,float x_axis,float y_axis){
    delta=CLAMP(delta,0.f,.1f);
    c->aim_x=CLAMP(c->aim_x+CLAMP(x_axis,-1.f,1.f)*240.0f*delta,36.f,IM2_W-20.f);
    c->aim_y=CLAMP(c->aim_y+CLAMP(y_axis,-1.f,1.f)*200.0f*delta,93.f,IM2_H-27.f);
    c->beam_time=CLAMP(c->beam_time-delta,0.f,1.f);
    c->flash_time=CLAMP(c->flash_time-delta,0.f,1.f);
    c->cooldown=CLAMP(c->cooldown-delta,0.f,1.f);
}
int b8_fire(B8Combat*c){
    if(c->completed||c->cooldown>0.f)return 0;
    c->shots++;c->cooldown=.22f;c->beam_time=.12f;c->flash_time=.30f;
    c->beam_x=c->aim_x;c->beam_y=c->aim_y;
    c->last_hit=0;
    float tx=0,ty=0;b8_get_target(c,&tx,&ty);
    c->hit_x=tx;c->hit_y=ty;
    float dx=c->aim_x-tx,dy=c->aim_y-ty;
    if(dx*dx+dy*dy<=21.f*21.f){
      c->last_hit=1;c->hits++;c->stage++;
      if(c->stage>=3)c->completed=1;
    }
    return c->last_hit;
}
void b8_draw(uint32_t*out,const B8Combat*c){
    if(!out||!c)return;
    const uint32_t cyan=COL(90,225,247),gold=COL(255,212,103),red=COL(247,83,69);
    if(!c->completed){
      float fx,fy;b8_get_target(c,&fx,&fy);
      int x=(int)fx,y=(int)fy;
      circ(out,x,y,21,gold);circ(out,x,y,15,gold);circ(out,x,y,5,red);
      ln(out,x-29,y,x-24,y,cyan);ln(out,x+24,y,x+29,y,cyan);
      ln(out,x,y-29,x,y-24,cyan);ln(out,x,y+24,x,y+29,cyan);
    }
    if(c->flash_time>0 && c->last_hit){
      for(int i=0;i<8;i++){
        float a=(float)i*0.785398163f;
        int x=(int)c->hit_x+(int)(cosf(a)*27.f);
        int y=(int)c->hit_y+(int)(sinf(a)*27.f);
        ln(out,(int)c->hit_x,(int)c->hit_y,x,y,gold);
      }
    }
    if(c->beam_time>0){
      ln(out,276,160,(int)c->beam_x,(int)c->beam_y,cyan);
      ln(out,275,160,(int)c->beam_x,(int)c->beam_y,gold);
      circ(out,(int)c->beam_x,(int)c->beam_y,4,COL(255,250,200));
    }
    int x=(int)c->aim_x,y=(int)c->aim_y;
    ln(out,x-9,y,x-3,y,cyan);ln(out,x+3,y,x+9,y,cyan);
    ln(out,x,y-9,x,y-3,cyan);ln(out,x,y+3,x,y+9,cyan);
    /* B7's lower HUD is retained; this additional arcade test HUD intentionally
       sits above it and remains visible even with 3-D armor centered onscreen. */
    for(int j=IM2_H-42;j<IM2_H-18;j++)for(int i=4;i<282;i++)out[j*IM2_W+i]=COL(12,31,45);
    number(out,18,IM2_H-36,(int)c->hits,gold);
    number(out,72,IM2_H-36,(int)c->shots,cyan);
    number(out,126,IM2_H-36,(int)(c->stage>=3?3:c->stage+1),cyan);
    /* Icons: green HITS, blue shots and target stage. The three display values
       are spaced and intended to be read alongside the hardware button guide. */
    if(c->completed){
      for(int j=108;j<155;j++)for(int i=300;i<478;i++)out[j*IM2_W+i]=COL(9,56,39);
      for(int j=0;j<3;j++)circ(out,335+43*j,128,11,gold);
    }
}
