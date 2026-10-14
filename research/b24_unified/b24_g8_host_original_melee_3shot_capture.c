/* Actual G8 IM2T textured model + original 2010 Combo_1/2/3 baked
   source clip poses through B24 live motion selection and G8 CPU renderer.
   This is source-only HOST playback: NO synthetic punch vertex deformation,
   no damage events, no VitaGL/PS Vita frame capture and no VPK. */
#include "renderer.h"
#include "b24_g8_live_original_motion.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int save_ppm(const char *path,const uint32_t *rgb){
 FILE *f=fopen(path,"wb");
 if(!f)return 0;
 if(fprintf(f,"P6\n%d %d\n255\n",IM2_W,IM2_H)<0){fclose(f);return 0;}
 for(size_t i=0;i<(size_t)IM2_W*IM2_H;i++){
  uint32_t px=rgb[i];
  unsigned char c[3]={(unsigned char)(px>>16),(unsigned char)(px>>8),
                      (unsigned char)px};
  if(fwrite(c,1,3,f)!=3){fclose(f);return 0;}
 }
 return fclose(f)==0;
}
static int tick(B24G8LiveOriginalMotion *s,IM2Model *m,
                const char *folder,uint32_t now){
 return b24_g8_motion_tick(s,folder,m->vertices,sizeof(IM2Vertex),
                          m->nv,0,B24M_IDLE,0.f,0.f,now);
}
int main(int argc,char **argv){
 if(argc!=4){fprintf(stderr,"usage: combo_renderer MODEL_PATH ANIMS_DIR SCREEN_DIR\n");return 2;}
 IM2Model m={0};
 if(!im2_load(&m,argv[1])||m.nv!=802u)return 3;
 B24G8LiveOriginalMotion chain={0};
 uint32_t *pixels=malloc((size_t)IM2_W*IM2_H*sizeof(uint32_t));
 float *depth=malloc((size_t)IM2_W*IM2_H*sizeof(float));
 if(!pixels||!depth)return 4;
 IM2Camera cam={0};cam.yaw=3.1f;cam.pitch=.05f;cam.zoom=1.f;
 const uint32_t start[]={1000u,1220u,1450u};
 const uint32_t mid[]={1070u,1300u,1600u};
 const uint32_t shot[]={1200u,1390u,1700u};
 const char *clips[]={
  "ironman_ironman_ground_combo_1",
  "ironman_ironman_ground_combo_2",
  "ironman_ironman_ground_combo_3"};
 if(!tick(&chain,&m,argv[2],900u))return 5;
 for(int i=0;i<3;i++){
  b24_g8_motion_melee_trigger(&chain,start[i]);
  if(!tick(&chain,&m,argv[2],mid[i])||
     !tick(&chain,&m,argv[2],shot[i]))return 6;
  if(chain.missing||!chain.active||
     strcmp(chain.selected,clips[i])!=0){
   fprintf(stderr,"Missing REAL original source melee clip %s got %s\n",
           clips[i],chain.selected);return 7;
  }
  im2_render(pixels,depth,&m,&cam,"2010 SOURCE MARK VI COMBO",(unsigned)(i+1));
  char name[350];int n=snprintf(name,sizeof(name),"%s/mark6_2010_original_melee_combo_%d.ppm",argv[3],i+1);
  if(n<=0||(size_t)n>=sizeof(name)||!save_ppm(name,pixels))return 8;
  printf("G8_REAL_ORIGINAL_MELEE_CPU_FRAME combo=%d filename=%s original_source=%s\n",
         i+1,name,chain.selected);
 }
 if(chain.melee.completed_attacks!=2u)return 9;
 printf("PASS 3 G8 actual original 2010 Mark VI combo pose textured host CPU rendered frames; NO fake hitboxes/no VPK\n");
 b24_g8_motion_release(&chain);im2_free(&m);free(pixels);free(depth);
 return 0;
}
