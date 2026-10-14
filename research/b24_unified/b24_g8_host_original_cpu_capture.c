/* OFF-VITA source-to-render test. Uses G8's actual IM2T textures,
 * renderer.c CPU fallback, the G8 original on-demand motion router,
 * and the existing B16 right-arm combat overlay (not a mock mesh pose).
 * Diagnostic screen grabs are NOT hardware VitaGL screenshots.
 * No GPU/VPK compilation and no modification to G8 runtime. */
#include "renderer.h"
#include "b16_action.h"
#include "b24_g8_live_original_motion.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
 const char *tag;
 B24MotionStage stage;
 float x,y;
 int fire;
} Scene;
static const Scene iron[]={
 {"ground_walk_forward",B24M_WALK,0.f,.9f,0},
 {"ground_walk_left",B24M_WALK,-.9f,.02f,0},
 {"hover_left",B24M_DRIFT,-.9f,.02f,0},
 {"hover_right",B24M_DRIFT,.9f,.02f,0},
 {"cruise_fly",B24M_CRUISE,0.f,1.f,0},
 {"rush_fly",B24M_RUSH,0.f,1.f,0},
 {"hover_left_repulsor",B24M_DRIFT,-.9f,0.f,1},
 {"hover_right_repulsor",B24M_DRIFT,.9f,0.f,1}
};
static const Scene wm[]={
 {"hover_idle",B24M_HOVER,0.f,0.f,0},
 {"hover_left",B24M_DRIFT,-.9f,0.f,0},
 {"hover_right",B24M_DRIFT,.9f,0.f,0},
 {"hover_forward",B24M_DRIFT,0.f,.9f,0},
 {"cruise",B24M_CRUISE,0.f,.9f,0},
 {"hover_left_repulsor",B24M_DRIFT,-.9f,0.f,1},
 {"hover_right_repulsor",B24M_DRIFT,.9f,0.f,1}
};
static int ppm(const char *filename,const uint32_t *pixels){
 FILE *f=fopen(filename,"wb");
 if(!f)return 0;
 if(fprintf(f,"P6\n%d %d\n255\n",IM2_W,IM2_H)<0){fclose(f);return 0;}
 for(size_t i=0;i<(size_t)IM2_W*IM2_H;i++){
  const uint32_t pixel=pixels[i];
  const unsigned char rgb[3]={(unsigned char)(pixel>>16),
                              (unsigned char)(pixel>>8),
                              (unsigned char)pixel};
  if(fwrite(rgb,1,3,f)!=3){fclose(f);return 0;}
 }
 return fclose(f)==0;
}
static int capture(const char *dir,const char *armor,int suit,
                   const char *model_path,const char *animation_root,
                   const Scene *scenes,size_t count){
 IM2Model model={0};
 if(!im2_load(&model,model_path)){fprintf(stderr,"Cannot load real G8 IM2T model: %s\n",model_path);return 0;}
 unsigned expected=suit==0?802u:1292u;
 if(model.nv!=expected){fprintf(stderr,"Mismatch original model topology %u != %u\n",model.nv,expected);im2_free(&model);return 0;}
 B16Action attack={0};
 if(!b16_action_load(&attack,suit,&model)){fprintf(stderr,"B16 right-arm pose missing for %s\n",armor);im2_free(&model);return 0;}
 B24G8LiveOriginalMotion live={0};
 uint32_t *pixels=malloc((size_t)IM2_W*IM2_H*sizeof(uint32_t));
 float *depth=malloc((size_t)IM2_W*IM2_H*sizeof(float));
 if(!pixels||!depth){free(pixels);free(depth);b16_action_release(&attack);im2_free(&model);return 0;}
 IM2Camera camera={0};
 camera.yaw=3.1f;camera.pitch=.05f;camera.zoom=1.f;
 camera.wireframe=0;camera.flying=0;
 int good=1;
 for(size_t i=0;i<count;i++){
  const Scene *sc=&scenes[i];
  /* Simulated gameplay INPUTS / stage; source-driven body and authentic
     B16 firing overlay, then G8 CPU preview renderer, same model instance. */
  uint32_t t=1000u+(uint32_t)(i*500);
  if(!b24_g8_motion_tick(&live,animation_root,model.vertices,
                          sizeof(IM2Vertex),model.nv,suit,sc->stage,
                          sc->x,sc->y,t)){
   fprintf(stderr,"Stream failed at %s\n",sc->tag);good=0;break;
  }
  /* Test an ACCEPTED repulsor event (original G8 main calls this only
     when B16 combat fire succeeds). Real _Att should supersede B16 arm. */
  if(sc->fire)b24_g8_motion_repulsor_trigger(&live,t+1u);
  if(!b24_g8_motion_tick(&live,animation_root,model.vertices,
                          sizeof(IM2Vertex),model.nv,suit,sc->stage,
                          sc->x,sc->y,t+200u)){
   fprintf(stderr,"Pose sampling failed at %s\n",sc->tag);good=0;break;
  }
  if(sc->fire&&!b24_g8_motion_whole_body_fire(&live)){
   fprintf(stderr,"G8 missing original full-body repulsor source animation: %s\n",sc->tag);
   good=0;break;
  }
  if(live.missing||!live.active){
   fprintf(stderr,"MISSING EXACT REAL 2010 ORIGINAL IM2V for %s: %s\n",
                  sc->tag,live.selected);good=0;break;
  }
  if(sc->fire){
   if(b24_g8_motion_whole_body_fire(&live)){
    /* Exact source contains arms; avoid applying B16 a second time. */
    attack.attack_active=0;
   }else{
    /* Safe legacy G8 fallback when new _Att resource is missing. */
    b16_attack_begin(&attack,t+200u,1,0,0);
    b16_apply_attack(&attack,&model,t+300u);
    if(!attack.attack_active){fprintf(stderr,"B16 fallback shot unavailable\n");good=0;break;}
   }
  }
  camera.flying=(sc->stage>=B24M_HOVER);
  im2_render(pixels,depth,&model,&camera,armor,(unsigned)(i+1));
  char out[384];
  int n=snprintf(out,sizeof(out),"%s/%s_%s.ppm",dir,armor,sc->tag);
  if(n<=0||(size_t)n>=sizeof(out)||!ppm(out,pixels)){
   fprintf(stderr,"Host rendered frame not saved\n");good=0;break;
  }
  printf("REAL_G8_HOST_CPU_RENDER %s %s ORIGINAL_SOURCE=%s %s\n",
         armor,sc->tag,live.selected,sc->fire?(b24_g8_motion_whole_body_fire(&live)?"REAL_2010_DIRECTIONAL_FULL_BODY_ATT":"B16_RIGHT_ARM_FALLBACK"):"BASE");
 }
 if(live.successful_frames!=count*2u){
  fprintf(stderr,"Original sample frame count wrong: %u vs %zu\n",
          live.successful_frames,count*2u);good=0;
 }
 if(live.misses){
  fprintf(stderr,"Real original source pose files missing: %u\n",live.misses);good=0;
 }
 b24_g8_motion_release(&live);
 b16_action_release(&attack);
 im2_free(&model);
 free(pixels);free(depth);
 return good;
}
int main(int argc,char **argv){
 if(argc!=4){fprintf(stderr,"Usage: host_motion_capture MODELS_DIR ANIMATIONS_DIR OUTPUT_DIR\n");return 2;}
 char model[384];
 int n=snprintf(model,sizeof(model),"%s/mark6.im2t",argv[1]);
 if(n<=0||(size_t)n>=sizeof(model))return 2;
 if(!capture(argv[3],"mark6",0,model,argv[2],
             iron,sizeof(iron)/sizeof(iron[0])))return 3;
 n=snprintf(model,sizeof(model),"%s/warmachine.im2t",argv[1]);
 if(n<=0||(size_t)n>=sizeof(model))return 2;
 if(!capture(argv[3],"warmachine",2,model,argv[2],
             wm,sizeof(wm)/sizeof(wm[0])))return 4;
 puts("PASS G8 ACTUAL HOST CPU DRAW 15 model-textured snapshots,"
      " original stream time progression plus B16 repulsor, no VPK.");
 return 0;
}
