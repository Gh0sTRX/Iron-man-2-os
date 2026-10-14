#include "b24_gpu_hud_native.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
/* Header-only geometry preparation: no OpenGL symbols, no CPU screen buffer.
   Pixel-accurate curves/fonts are deliberately NOT claimed; colors, lock
   restrictions, pause labels, armor/status logic mirror current B22/B23 UI. */
static uint32_t rgba(uint32_t rgb){
 return (rgb>>16&255u)|((rgb>>8&255u)<<8)|((rgb&255u)<<16)|0xff000000u;
}
static float bound(float x,float a,float b){
 return !isfinite(x)?a:(x<a?a:(x>b?b:x));
}
static void rect(B24NativeHudGeometry *g,float x,float y,float w,float h,uint32_t color){
 if(!g||!isfinite(x)||!isfinite(y)||!isfinite(w)||!isfinite(h)||
    !isfinite((float)color)||w<=0.f||h<=0.f)return;
 float xa=bound(x,0.f,480.f),xb=bound(x+w,0.f,480.f);
 float ya=bound(y,0.f,272.f),yb=bound(y+h,0.f,272.f);
 if(xb<=xa||yb<=ya)return;
 if(g->count>B24_NATIVE_HUD_VERTICES-6u){g->overflow=1;return;}
 B24NativeHudVertex *v=&g->vertices[g->count];
 uint32_t color_le=rgba(color);
 v[0]=(B24NativeHudVertex){xa,ya,color_le};
 v[1]=(B24NativeHudVertex){xb,ya,color_le};
 v[2]=(B24NativeHudVertex){xb,yb,color_le};
 v[3]=v[0];v[4]=v[2];
 v[5]=(B24NativeHudVertex){xa,yb,color_le};
 g->count+=6;g->quads++;
}
static void line(B24NativeHudGeometry *g,float x,float y,float bx,float by,float width,uint32_t c){
 if(!isfinite(x)||!isfinite(y)||!isfinite(bx)||!isfinite(by)||
    !isfinite(width)||width<=0.f)return;
 float dx=bx-x,dy=by-y,dist=sqrtf(dx*dx+dy*dy);
 if(!isfinite(dist)||dist>10000.f)return;
 if(dist<.001f){rect(g,x,y,width,width,c);return;}
 float rx=(-dy/dist)*width*.5f,ry=(dx/dist)*width*.5f;
 /* Use one conservative axis-aligned quad only for horizontal/vertical,
    polygon geometry for true diagonal lines added in later visual pass. */
 if(fabsf(dy)<.01f){rect(g,fminf(x,bx),y-width*.5f,fabsf(dx)+1.f,width,c);return;}
 if(fabsf(dx)<.01f){rect(g,x-width*.5f,fminf(y,by),width,fabsf(dy)+1.f,c);return;}
 /* 2D diagonal segment has 2 triangles and one GL draw batch. */
 if(g->count>B24_NATIVE_HUD_VERTICES-6u){g->overflow=1;return;}
 B24NativeHudVertex *v=&g->vertices[g->count];
 uint32_t rgb=rgba(c);
 v[0]=(B24NativeHudVertex){x+rx,y+ry,rgb};
 v[1]=(B24NativeHudVertex){bx+rx,by+ry,rgb};
 v[2]=(B24NativeHudVertex){bx-rx,by-ry,rgb};
 v[3]=v[0];v[4]=v[2];
 v[5]=(B24NativeHudVertex){x-rx,y-ry,rgb};
 g->count+=6;g->quads++;
}
static void ring(B24NativeHudGeometry *g,float x,float y,float r,uint32_t c){
 for(int i=0;i<32;i++){
  float t=(float)i*0.19634954084936207f,tt=(float)(i+1)*0.19634954084936207f;
  line(g,x+cosf(t)*r,y+sinf(t)*r,x+cosf(tt)*r,y+sinf(tt)*r,1.f,c);
 }
}
static void bar(B24NativeHudGeometry *g,float x,float y,float w,float h,float pct,uint32_t color){
 float p=bound(pct,0.f,100.f);
 rect(g,x,y,w,h,0x253343u);
 if(p>0.f)rect(g,x,y,w*p*.01f,h,color);
 line(g,x-1.f,y-1.f,x+w+1.f,y-1.f,1.f,0x748a98u);
 line(g,x-1.f,y+h+1.f,x+w+1.f,y+h+1.f,1.f,0x748a98u);
}
static void corners(B24NativeHudGeometry *g,float x,float y,float rad,uint32_t color){
 const float t=7.f;
 line(g,x-rad,y-rad,x-rad+t,y-rad,1.2f,color);
 line(g,x-rad,y-rad,x-rad,y-rad+t,1.2f,color);
 line(g,x+rad,y-rad,x+rad-t,y-rad,1.2f,color);
 line(g,x+rad,y-rad,x+rad,y-rad+t,1.2f,color);
 line(g,x-rad,y+rad,x-rad+t,y+rad,1.2f,color);
 line(g,x-rad,y+rad,x-rad,y+rad-t,1.2f,color);
 line(g,x+rad,y+rad,x+rad-t,y+rad,1.2f,color);
 line(g,x+rad,y+rad,x+rad,y+rad-t,1.2f,color);
}
/* Existing B24 pause font uses 5-column bitmap. Reuse its A-Z glyph shapes. */
static const unsigned char alphabet[26][5]={
 {0x7e,0x11,0x11,0x11,0x7e},{0x7f,0x49,0x49,0x49,0x36},
 {0x3e,0x41,0x41,0x41,0x22},{0x7f,0x41,0x41,0x22,0x1c},
 {0x7f,0x49,0x49,0x49,0x41},{0x7f,0x09,0x09,0x09,0x01},
 {0x3e,0x41,0x49,0x49,0x7a},{0x7f,0x08,0x08,0x08,0x7f},
 {0x41,0x41,0x7f,0x41,0x41},{0x20,0x40,0x41,0x3f,0x01},
 {0x7f,0x08,0x14,0x22,0x41},{0x7f,0x40,0x40,0x40,0x40},
 {0x7f,0x02,0x0c,0x02,0x7f},{0x7f,0x04,0x08,0x10,0x7f},
 {0x3e,0x41,0x41,0x41,0x3e},{0x7f,0x09,0x09,0x09,0x06},
 {0x3e,0x41,0x51,0x21,0x5e},{0x7f,0x09,0x19,0x29,0x46},
 {0x46,0x49,0x49,0x49,0x31},{0x01,0x01,0x7f,0x01,0x01},
 {0x3f,0x40,0x40,0x40,0x3f},{0x1f,0x20,0x40,0x20,0x1f},
 {0x7f,0x20,0x18,0x20,0x7f},{0x63,0x14,0x08,0x14,0x63},
 {0x03,0x04,0x78,0x04,0x03},{0x61,0x51,0x49,0x45,0x43}
};
static void label(B24NativeHudGeometry *g,float x,float y,
                  const char *s,uint32_t color,float size){
 for(;s&&*s;s++,x+=6.f*size){
  if(*s<'A'||*s>'Z')continue;
  for(int col=0;col<5;col++){
   unsigned char bits=alphabet[(unsigned)(*s-'A')][col];
   int run=-1;
   for(int row=0;row<=7;row++){
    int on=row<7 && (bits&(1u<<row));
    if(on&&run<0)run=row;
    if(!on&&run>=0){
      rect(g,x+col*size,y+run*size,size,(row-run)*size,color);
      g->pause_glyph_quads++;
      run=-1;
    }
   }
  }
 }
}
static void core_hud(B24NativeHudGeometry *g,const B22UI *ui,
                     uint32_t main,uint32_t accent,uint32_t soft){
 line(g,17,20,160,20,1,0xd2ffffu);line(g,17,20,11,28,1,0xd2ffffu);
 bar(g,20,27,130,7,ui->armor,0x39cfeau);
 if(ui->show_objective)line(g,165,16,299,16,1,0x6b96a3u);
 if(ui->show_minimap){ring(g,44,222,31,0x247eaeu);ring(g,44,222,25,0x42c2e4u);}
 ring(g,442,224,23,0x247eaeu);ring(g,442,224,17,0x31b9e3u);
 bar(g,392,249,77,5,ui->charge,0x39cfeau);
 if(ui->mode==B22_ORIGINAL_LAYOUT)return;
 float side=ui->mode==B22_IMMERSIVE?91.f:43.f;
 line(g,4,50,4,50+side,1,main);line(g,4,50,14,50,1,main);
 line(g,475,50,475,50+side,1,main);line(g,464,50,475,50,1,main);
 line(g,10,258,90,258,1,soft);line(g,391,258,469,258,1,soft);
 bar(g,169,246,64,5,ui->shield,main);
 bar(g,246,246,64,5,ui->energy,accent);
 if(ui->suit==B22_WARMACHINE){
  line(g,397,79,465,79,1,accent);line(g,397,79,397,105,1,accent);
  for(int k=0;k<6;k++)rect(g,405.f+k*10.f,88,6,1,k<ui->ammo?accent:soft);
 }else{
  ring(g,444,94,14,main);line(g,444,85,444,103,1,accent);
  line(g,436,94,452,94,1,accent);
 }
 if(ui->damage_warning){
  line(g,4,18,29,18,1,0xfa6555u);line(g,4,18,4,37,1,0xfa6555u);
 }
 if(ui->mode==B22_IMMERSIVE){
  line(g,126,7,161,7,1,main);line(g,319,7,354,7,1,main);
 }
}
static void missile_ui(B24NativeHudGeometry *g,const B23Lock *s,
                       const B22UI *ui,uint32_t accent){
 if(ui->page!=B22_GAME||!s||s->weapon!=B23_MISSILE||
   !s->lock_button_held||s->phase==B23_IDLE||s->target_id<0)return;
 uint32_t active=s->phase==B23_LOCKED?
                (ui->suit==B22_WARMACHINE?0xffbd66u:0x70ffb0u):accent;
 float r=s->phase==B23_LOCKED?21.f:26.f;
 corners(g,(float)s->target_x,(float)s->target_y,r,active);
 corners(g,240,136,14,accent);
 g->missile_brackets=16;
 float p=s->phase==B23_LOCKED?1.f:
          (s->required_s>0.f?s->acquire_s/s->required_s:0.f);
 rect(g,217,159,46,1,0x36515bu);
 rect(g,217,159,46*bound(p,0.f,1.f),1,active);
 if(s->phase==B23_LOCKED)line(g,230,108,250,108,1,active);
 if(isfinite(s->target_health_percent)&&s->target_health_percent>=0.f)
  bar(g,(float)s->target_x-18,(float)s->target_y-r-6,36,1,
      s->target_health_percent,active);
}
int b24_native_hud_build(B24NativeHudGeometry *g,const B24Unified *game){
 if(!g||!game)return 0;
 g->count=g->quads=g->missile_brackets=g->reticle_quads=g->pause_glyph_quads=0;
 g->overflow=0;
 const B22UI *ui=&game->hud;
 const uint32_t main=ui->suit==B22_WARMACHINE?0xb6bf9du:0x55dff8u;
 const uint32_t accent=ui->suit==B22_WARMACHINE?0xf0a753u:0xe8bb5du;
 const uint32_t soft=ui->suit==B22_WARMACHINE?0x526c69u:0x477ba9u;
 if(ui->page==B22_GAME){
  core_hud(g,ui,main,accent,soft);
  /* Exact user promise: ONLY in RUSH, never Stage2, cheap edge streaks. */
  if(game->speed_fx.enabled && game->speed_fx.strength>.03f){
    uint32_t seed=0x1234567u^(game->speed_fx.ticks*2654435761u);
    int n=(int)(8.f+12.f*bound(game->speed_fx.strength,0.f,1.f));
    if(n>20)n=20;
    for(int k=0;k<n;k++){
      seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
      float x=6.f+(float)(seed%63u);
      if(k&1)x=479.f-x;
      seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
      float y=22.f+(float)(seed%221u);
      line(g,x,y,x+(x<240.f?-7.f:7.f),y+15.f,1.2f,soft);
    }
  }
  float t=bound(game->camera_base.shoulder_to_chase,0.f,1.f);
  float cx=278.f-38.f*t,cy=110.f+26.f*t;
  uint32_t reticle=game->missile.phase==B23_LOCKED?accent:main;
  line(g,cx-12,cy,cx-5,cy,1.3f,reticle);
  line(g,cx+5,cy,cx+12,cy,1.3f,reticle);
  line(g,cx,cy-12,cx,cy-5,1.3f,reticle);
  line(g,cx,cy+5,cx,cy+12,1.3f,reticle);
  g->reticle_quads=4;
  missile_ui(g,&game->missile,ui,accent);
 }else{
  /* Match readable B24-C2 menu, GPU-native quads: no bitmap upload. */
  rect(g,103,59,274,151,0x101b27u);
  line(g,103,59,377,59,1.5f,main);
  line(g,103,210,377,210,1.5f,main);
  line(g,103,59,103,210,1.5f,main);
  line(g,377,59,377,210,1.5f,main);
  label(g,169,69,"PAUSED",0x55dff8u,2.f);
  label(g,141,111,"START RESUME",0xe8bb5du,1.f);
  label(g,141,139,"CIRCLE RESUME",0xc8e5eeu,1.f);
  label(g,141,164,"CROSS OPTIONS",0xc8e5eeu,1.f);
  label(g,141,187,"BETA MENU",0x7cb2c5u,1.f);
  line(g,133,118,347,118,1,accent);
 }
 return !g->overflow && g->count>0u && g->count<=B24_NATIVE_HUD_VERTICES;
}
