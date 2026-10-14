#include "b24_gpu_reticle.h"
#include <math.h>
#include <stddef.h>
static void px(uint32_t *f,int stride,int x,int y,uint32_t color){
 if(x>=0&&x<480&&y>=0&&y<272)f[(size_t)y*stride+x]=color;
}
B24ReticlePoint b24_reticle_position(float t){
 if(!isfinite(t))t=0.f;
 if(t<0.f)t=0.f;if(t>1.f)t=1.f;
 return (B24ReticlePoint){278.f+(240.f-278.f)*t,110.f+(136.f-110.f)*t};
}
void b24_reticle_draw(uint32_t *rgb,int stride,float t,int locked,int paused){
 if(!rgb||stride<480||paused)return;
 B24ReticlePoint p=b24_reticle_position(t);
 int x=(int)roundf(p.x),y=(int)roundf(p.y);
 uint32_t color=locked?0xe8bb5du:0x55dff8u;
 for(int j=5;j<=12;j++){
   px(rgb,stride,x+j,y,color);px(rgb,stride,x-j,y,color);
   px(rgb,stride,x,y+j,color);px(rgb,stride,x,y-j,color);
 }
 for(int d=-1;d<=1;d++)px(rgb,stride,x+d,y+d,0xa8edfa);
}
