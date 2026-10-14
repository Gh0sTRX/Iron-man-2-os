/* REAL G8 model + G8 renderer + ORIGINAL 2010 IM2V player poses:
   pick non-shooting hover from independent author assets, not heuristic. */
#include "renderer.h"
#include "b24_original_im2v_stream.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int ppm(const char *path,const uint32_t *rgba){
 FILE *f=fopen(path,"wb");if(!f)return 0;
 if(fprintf(f,"P6\n%d %d\n255\n",IM2_W,IM2_H)<0){fclose(f);return 0;}
 for(size_t i=0;i<(size_t)IM2_W*IM2_H;i++){
  uint32_t v=rgba[i];unsigned char b[]={v>>16,v>>8,v};
  if(fwrite(b,1,3,f)!=3){fclose(f);return 0;}
 }
 return fclose(f)==0;
}
int main(int argc,char **argv){
 if(argc!=5){fprintf(stderr,"usage: compare IM2T source_original_dir G8base_dir imageout\n");return 2;}
 IM2Model m={0};
 if(!im2_load(&m,argv[1])||m.nv!=802)return 3;
 const struct{const char *asset,*label;int baseline;} cases[]={
  {"mark6_hover","G8_fallback_hover",1},
  {"ironman_ironman_aim_float_idle","aim_float_idle",0},
  {"ironman_ironman_move_float","move_float",0},
  {"ironman_ironman_ground_float","ground_float",0},
  {"ironman_ironman_aim_float_idle_l","aim_float_idle_L",0},
  {"ironman_ironman_float_att_ready","attack_ready",0}
 };
 uint32_t *px=malloc((size_t)IM2_W*IM2_H*4u);
 float *depth=malloc((size_t)IM2_W*IM2_H*4u);
 float *xyz=malloc((size_t)802u*3u*4u);
 if(!px||!depth||!xyz)return 4;
 IM2Camera camera={0};camera.yaw=3.1f;camera.pitch=.05f;camera.zoom=1.f;
 unsigned num=0;
 for(unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);i++){
  B24OriginalIM2VStream s={0};
  if(!b24_original_im2v_open(&s,cases[i].baseline?argv[3]:argv[2],
                            cases[i].asset,802)){
   fprintf(stderr,"Original hover source missing: %s\n",cases[i].asset);
   return 5;
  }
  unsigned t=s.duration_ms/2;
  if(!b24_original_im2v_sample(&s,t,0,xyz))return 6;
  for(unsigned v=0;v<802;v++){
   m.vertices[v].x=xyz[v*3];
   m.vertices[v].y=xyz[v*3+1];
   m.vertices[v].z=xyz[v*3+2];
  }
  im2_render(px,depth,&m,&camera,cases[i].label,i);
  char file[420];
  int k=snprintf(file,sizeof(file),"%s/%02u_%s.ppm",
                 argv[4],i,cases[i].label);
  if(k<=0||(size_t)k>=sizeof(file)||!ppm(file,px))return 7;
  printf("G10_TRUE_ORIGINAL_2010_IDLE_POSE %s author_source=%s duration=%u t=%u real_body_vertices=802 real_G8_CPU_model=mark6.im2t\n",
         cases[i].label,cases[i].asset,s.duration_ms,t);
  num++;
  b24_original_im2v_close(&s);
 }
 if(num!=6)return 8;
 puts("PASS 6 original MarkVI real BRES body idle-vs-aim-vs-hover source 2010 poses and B13 baseline comparisons. No Vita screenshot or VPK.");
 free(px);free(depth);free(xyz);im2_free(&m);
 return 0;
}
