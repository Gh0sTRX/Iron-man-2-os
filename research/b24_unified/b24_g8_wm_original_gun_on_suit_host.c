/* G8 ORIGINAL SUIT + ORIGINAL 2010 GUN NODE WORLD MARKERS.
 * Uses actual reconstructed G8 renderer.c/IM2T, and source-baked WM
 * IM2V+IM2K pose at EXACT SAME timeline keyframe. Diagnostic overlay ONLY.
 * Gun03 DummyGreen->DummyEGreen axis is NOT verified weapon muzzle or FX.
 * No fabricated vertices/projectiles; 20 Hz original key poses only; NO VPK.
 */
#include "renderer.h"
#include "b24_original_im2v_stream.h"
#include "b24_wm_2010_gun_stream.h"
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void put(uint32_t *pixels,int x,int y,uint32_t c){
 if(x>=0&&x<IM2_W&&y>=0&&y<IM2_H)pixels[(size_t)y*IM2_W+(size_t)x]=c;
}
static void stroke(uint32_t *pixels,int x0,int y0,int x1,int y1,uint32_t c){
 int dx=abs(x1-x0),dy=abs(y1-y0),sx=x0<x1?1:-1,sy=y0<y1?1:-1,err=dx-dy;
 for(int k=0;k<600;k++){
  put(pixels,x0,y0,c);
  if(x0==x1&&y0==y1)break;
  int e=err*2;
  if(e>-dy){err-=dy;x0+=sx;}
  if(e<dx){err+=dx;y0+=sy;}
 }
}
static int screen(const IM2Camera *c,const IM2Model *m,const float source[3],int *x,int *y){
 if(!isfinite(source[0])||!isfinite(source[1])||!isfinite(source[2])||c->zoom<=0.f)return 0;
 /* EXACT G8 renderer.c non-third-person model projection lines 405-417,
    429-434. No independently invented projection. */
 float sy=sinf(c->yaw),cy=cosf(c->yaw);
 float sp=sinf(c->pitch),cp=cosf(c->pitch);
 float distance=3.70f/c->zoom+(c->flying?.65f:0.f);
 float rx=source[0]*cy-source[1]*sy+c->move_x;
 float ry=source[0]*sy+source[1]*cy+c->move_y;
 float rz=source[2]-m->center_z+c->altitude*.50f+c->hover_bob;
 float yy=ry*cp-rz*sp;
 float zz=ry*sp+rz*cp;
 float depth=distance-yy;
 if(depth<=.15f)return 0;
 float sx=IM2_W*.50f+350.f*rx/depth;
 float py=IM2_H*.52f-350.f*zz/depth;
 if(!isfinite(sx)||!isfinite(py)||fabsf(sx)>50000.f||fabsf(py)>50000.f)return 0;
 *x=(int)lroundf(sx);*y=(int)lroundf(py);
 return 1;
}
static void spot(uint32_t *rgb,int x,int y,uint32_t color){
 for(int i=-4;i<=4;i++){put(rgb,x+i,y,color);put(rgb,x,y+i,color);}
 for(int k=-2;k<=2;k++){put(rgb,x-4,y+k,color);put(rgb,x+4,y+k,color);}
}
static int ppm(const char *path,const uint32_t *rgb){
 FILE *f=fopen(path,"wb");if(!f)return 0;
 if(fprintf(f,"P6\n%d %d\n255\n",IM2_W,IM2_H)<0){fclose(f);return 0;}
 for(size_t i=0;i<(size_t)IM2_W*IM2_H;i++){
  uint32_t pixel=rgb[i];
  unsigned char c[3]={(unsigned char)(pixel>>16),(unsigned char)(pixel>>8),(unsigned char)pixel};
  if(fwrite(c,1,3,f)!=3){fclose(f);return 0;}
 }
 return fclose(f)==0;
}
static int capture(const char *im2v_root,const char *im2k_root,
                   const char *output,const char *stem,const char *tag,
                   IM2Model *model,uint32_t *pixels,float *depth,
                   unsigned *screens){
 B24OriginalIM2VStream body={0};
 B24WM2010GunStream gun={0};
 char file[180];
 const int n=snprintf(file,sizeof(file),"warmachine_%s",stem);
 if(n<=0||(size_t)n>=sizeof(file))return 0;
 if(!b24_original_im2v_open(&body,im2v_root,file,1292u)||
    !b24_wm_gun_stream_open(&gun,im2k_root,stem)){
  fprintf(stderr,"No matching source IM2V and IM2K stream %s\n",stem);
  b24_original_im2v_close(&body);b24_wm_gun_stream_close(&gun);
  return 0;
 }
 if(body.duration_ms!=gun.duration_ms||body.frames!=gun.frames){
  fprintf(stderr,"SOURCE GUN/BODY TIME SYNC MISMATCH %s\n",stem);
  b24_original_im2v_close(&body);b24_wm_gun_stream_close(&gun);
  return 0;
 }
 const uint32_t idxs[]={0u,(gun.frames-1u)/2u,gun.frames-1u};
 const uint32_t colors[]={0xffff5670u,0xff52d6ffu,0xffeac24au,0xff93ea9eu};
 float *xyz=(float *)malloc((size_t)1292u*3u*sizeof(float));
 if(!xyz){b24_original_im2v_close(&body);b24_wm_gun_stream_close(&gun);return 0;}
 IM2Camera camera={0};
 camera.yaw=3.1f;camera.pitch=.05f;camera.zoom=1.0f;
 int ok=1;
 for(int i=0;i<3;i++){
  uint32_t frame=idxs[i];
  uint32_t ms=(frame==gun.frames-1u)?gun.duration_ms:frame*50u;
  float m[6][16];
  if(!b24_original_im2v_sample(&body,ms,0,xyz)||
     !b24_wm_gun_stream_sample(&gun,ms,0,m)){ok=0;break;}
  for(size_t j=0;j<1292u;j++){
   model->vertices[j].x=xyz[j*3u];
   model->vertices[j].y=xyz[j*3u+1u];
   model->vertices[j].z=xyz[j*3u+2u];
  }
  im2_render(pixels,depth,model,&camera,"WM 2010 ORIGINAL RIG",frame);
  int px[6],py[6];
  unsigned valid=0;
  for(unsigned j=0;j<6;j++){
   const float pt[]={m[j][3],m[j][7],m[j][11]};
   if(!screen(&camera,model,pt,&px[j],&py[j])){
    fprintf(stderr,"Original 2010 gun marker projection rejected %s %u\n",stem,j);
    ok=0;break;
   }
   if(px[j]>=0&&px[j]<IM2_W&&py[j]>=0&&py[j]<IM2_H)valid++;
   spot(pixels,px[j],py[j],colors[j<4?j:2u]);
  }
  if(!ok)break;
  /* Marker source positions must be on/near model frame, never 2D HUD coords.
     These are distinct rig objects, so allow protruding 0.75 model units. */
  float lo[3]={1e30f,1e30f,1e30f},hi[3]={-1e30f,-1e30f,-1e30f};
  for(size_t k=0;k<1292u;k++){
   const float vals[]={xyz[k*3u],xyz[k*3u+1u],xyz[k*3u+2u]};
   for(int axis=0;axis<3;axis++){
    if(vals[axis]<lo[axis])lo[axis]=vals[axis];
    if(vals[axis]>hi[axis])hi[axis]=vals[axis];
   }
  }
  for(unsigned j=0;j<6;j++)for(int axis=0;axis<3;axis++){
   float pos=m[j][axis*4+3];
   if(pos<lo[axis]-1.1f||pos>hi[axis]+1.1f){
    fprintf(stderr,"G8 ORIGINAL GUN MARKER OUTSIDE MODEL bounds %s j=%u axis=%d pos=%.3f [%.3f %.3f]\n",stem,j,axis,pos,lo[axis],hi[axis]);
    ok=0;
   }
  }
  if(!ok)break;
  /* Plot marker-to-marker direction with EXAGGERATED line length for human
     visibility. Original source marker separation is only ~.013923 units. */
  float tip[3],direction[3];
  if(!b24_wm_gun_original_marker_axis((const float (*)[16])m,tip,direction)){
   fprintf(stderr,"Original Green Gun marker direction invalid %s\n",stem);
   ok=0;break;
  }
  float extended[]={tip[0]+direction[0]*.45f,
                    tip[1]+direction[1]*.45f,
                    tip[2]+direction[2]*.45f};
  int ax,ay;
  if(!screen(&camera,model,extended,&ax,&ay)){ok=0;break;}
  stroke(pixels,px[5],py[5],ax,ay,0xffffffffu);
  spot(pixels,ax,ay,0xffffffffu);
  char fname[440];
  int sz=snprintf(fname,sizeof(fname),"%s/%s_k%02u_%ums.ppm",
                  output,tag,frame,ms);
  if(sz<=0||(size_t)sz>=sizeof(fname)||!ppm(fname,pixels)){ok=0;break;}
  (*screens)++;
  printf("G8_GUN_ON_ORIGINAL_SUIT %s t=%ums 2010_GPU_MODEL=warmachine.im2t 2010_AUTHORED_SOURCE=%s nodes_in_view=%u marker_axis=[%.4f %.4f %.4f] diagnostic=%s\n",
         tag,ms,file,valid,direction[0],direction[1],direction[2],fname);
 }
 free(xyz);b24_wm_gun_stream_close(&gun);b24_original_im2v_close(&body);
 return ok;
}
int main(int argc,char **argv){
 if(argc!=5){fprintf(stderr,"Usage: g8wm SOURCE_MODEL.im2t ORIGINAL_BODY_IM2V_DIR ORIGINAL_GUN_IM2K_DIR OUTPUT_DIR\n");return 2;}
 IM2Model model={0};if(!im2_load(&model,argv[1])||model.nv!=1292u)return 3;
 uint32_t *rgb=(uint32_t*)malloc((size_t)IM2_W*IM2_H*sizeof(uint32_t));
 float *z=(float*)malloc((size_t)IM2_W*IM2_H*sizeof(float));
 if(!rgb||!z)return 4;
 const struct {const char *stem,*tag;} tests[]={
  {"warmachine_aim_float_idle","hover_idle"},
  {"warmachine_aim_float_move_r_att","hover_right_attack"},
  {"warmachine_aim_m_float_move_l_att","alternate_left_attack"},
  {"warmachine_aim_fly_m","aim_flight"},
  {"warmachine_attack_float_move_r","hover_right_weapon"},
  {"warmachine_aim_ground_move_r_att","ground_right_attack"},
 };
 unsigned count=0;int all=1;
 for(size_t i=0;i<sizeof(tests)/sizeof(tests[0]);i++){
  if(!capture(argv[2],argv[3],argv[4],tests[i].stem,tests[i].tag,
              &model,rgb,z,&count)){all=0;break;}
 }
 if(count!=18u){fprintf(stderr,"Expected 18 authentic model/gun source diagnostic frames, got %u\n",count);all=0;}
 if(all)puts("PASS 18 TRUE G8 ORIGINAL SUIT + 2010 ORIGINAL WM BODY AND GUN RIG TIME-SYNCED MARKER FRAMES. Diagnostic marker only; NOT proven weapon muzzle, no VitaGL or VPK.");
 free(rgb);free(z);im2_free(&model);
 return all?0:5;
}
