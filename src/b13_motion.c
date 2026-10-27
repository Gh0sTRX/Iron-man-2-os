#include "b13_motion.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static uint32_t u32(FILE *f,int *ok){unsigned char b[4];if(fread(b,1,4,f)!=4){*ok=0;return 0;}
 return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);}
static int load(B13Clip *dst,const char *name,uint32_t nv){
 char path[180];
#ifdef __vita__
 snprintf(path,sizeof(path),"app0:animations/%s.im2v",name);
#else
 snprintf(path,sizeof(path),"animations/%s.im2v",name);
#endif
 FILE *f=fopen(path,"rb");if(!f)return 0;
 int ok=1;char magic[4];
 if(fread(magic,1,4,f)!=4||memcmp(magic,"IM2V",4)){fclose(f);return 0;}
 uint32_t v=u32(f,&ok),frames=u32(f,&ok),fps=u32(f,&ok),ms=u32(f,&ok);
 if(!ok||v!=nv||frames<2||frames>256||fps!=20||ms<100||ms>60000){fclose(f);return 0;}
 size_t n=(size_t)v*3u*frames;
 if(n>1500000u){fclose(f);return 0;}
 float *samples=(float*)malloc(n*sizeof(float));if(!samples){fclose(f);return 0;}
 if(fread(samples,sizeof(float),n,f)!=n || fgetc(f)!=EOF){free(samples);fclose(f);return 0;}
 fclose(f);
 for(size_t i=0;i<n;i++)if(!isfinite(samples[i])){free(samples);return 0;}
 dst->xyz=samples;dst->verts=v;dst->frames=frames;dst->fps=fps;dst->duration_ms=ms;
 return 1;
}
void b13_release(B13Motion *s){if(!s)return;
 for(int i=0;i<B13_COUNT;i++)free(s->clips[i].xyz);
 free(s->transition_from);memset(s,0,sizeof(*s));s->previous_state=-1;}
int b13_prepare(B13Motion *s,int armor,const IM2Model *model){
 b13_release(s);
 if(!s||!model||!model->nv||!model->vertices)return 0;
 s->nverts=model->nv;s->armor=armor;
 const char *prefix=armor==4?"suitcase":armor==2?"warmachine":"mark6";
 const char *suffix[B13_COUNT]={"ground_idle","walk_normal","run","fly_normal",
   "rush01","rush06","rush12","rush_full","fly_start","fly_end","float_move","air_move"};
 int needs[B13_COUNT]={0};
 if(armor==2){needs[B13_FLOAT_MOVE]=1;needs[B13_FLY_END]=1;
    needs[B13_GROUND_IDLE]=1; needs[B13_RUN]=1;}
 else if(armor==4){
   needs[B13_GROUND_IDLE]=needs[B13_AIR_MOVE]=1;
   needs[B13_WALK]=needs[B13_RUN]=needs[B13_FLY_NORMAL]=1;
   needs[B13_RUSH01]=needs[B13_RUSH06]=needs[B13_RUSH12]=needs[B13_RUSH_FULL]=1;
 }else{
   for(int i=0;i<B13_COUNT;i++)needs[i]=(i!=B13_FLOAT_MOVE);
 }
 for(int i=0;i<B13_COUNT;i++)if(needs[i]){
   char name[96];snprintf(name,sizeof(name),"%s_%s",prefix,(armor==2 && i==B13_RUN)?"run_retarget":suffix[i]);
   if(!load(&s->clips[i],name,model->nv)){b13_release(s);return 0;}
 }
 s->transition_from=(float*)malloc((size_t)model->nv*3*sizeof(float));
 if(!s->transition_from){b13_release(s);return 0;}
 return 1;
}
static void apply_clip(B13Motion *s, IM2Model *model,const B13Clip *c,unsigned time,
                        unsigned now,int state){
 if(!c||!c->xyz || !c->duration_ms)return;
 unsigned elapsed=time>c->duration_ms?c->duration_ms:time;
 const unsigned idx=(unsigned)(((uint64_t)elapsed*c->fps)/1000u);
 unsigned f=idx>=c->frames?c->frames-1:idx;
 const unsigned f2=f+1<c->frames?f+1:f;
 float alpha=(float)(elapsed-(f*1000/c->fps))*((float)c->fps/1000.0f);
 if(alpha<0)alpha=0;
 if(alpha>1)alpha=1;
 const float *a=c->xyz+(size_t)f*c->verts*3;
 const float *b=c->xyz+(size_t)f2*c->verts*3;
 if(state!=s->previous_state){
  for(uint32_t i=0;i<model->nv;i++){
   s->transition_from[i*3]=model->vertices[i].x;
   s->transition_from[i*3+1]=model->vertices[i].y;
   s->transition_from[i*3+2]=model->vertices[i].z;
  }
  s->previous_state=state;s->state_started=now;
 }
 /* Soft transition: a discontinuity at state changes should not teleport joints. */
 float fade=(now-s->state_started)/150.0f;
 if(fade<0)fade=0;
 if(fade>1)fade=1;
 for(uint32_t i=0;i<model->nv;i++){
   const size_t k=(size_t)i*3;
   float x=(a[k]*(1-alpha)+b[k]*alpha);
   float y=(a[k+1]*(1-alpha)+b[k+1]*alpha);
   float z=(a[k+2]*(1-alpha)+b[k+2]*alpha);
   model->vertices[i].x=s->transition_from[k]*(1-fade)+x*fade;
   model->vertices[i].y=s->transition_from[k+1]*(1-fade)+y*fade;
   model->vertices[i].z=s->transition_from[k+2]*(1-fade)+z*fade;
 }
}
int b13_apply(B13Motion *s,IM2Model *model,int flying,int moving,int landing,int boost,
              int aiming,unsigned now,unsigned flight_begin){
 if(!s||!model||s->nverts!=model->nv ||!s->transition_from)return 0;
 int state=-1;unsigned t=now;
 if(s->armor==2){
    if(landing){s->previous_state=-1;return 0;} /* Do NOT label stop as landing */
    if(flying && moving && !boost)state=B13_FLOAT_MOVE;
    else {s->previous_state=-1;return 0;}
 }else if(landing){s->previous_state=-1;return 0;} /* Original B9 Air_land already good */
 else if(!flying){
    if(moving && !aiming)state=boost?B13_RUN:B13_WALK;
    else if(!moving && s->armor!=4)state=B13_GROUND_IDLE;
    else{s->previous_state=-1;return 0;} /* Aim walk goes to B9 base */
 }else if(moving){
    if(!boost)state=B13_FLY_NORMAL;
    else {
      const unsigned time_since=(now-flight_begin);
      if(time_since<250)state=B13_RUSH01;
      else if(time_since<500)state=B13_RUSH06;
      else if(time_since<750)state=B13_RUSH12;
      else state=B13_RUSH_FULL;
    }
 }else if(s->armor!=4 && now-flight_begin<300 && s->clips[B13_FLY_START].xyz){
      state=B13_FLY_START;t=now-flight_begin;
 }else {s->previous_state=-1;return 0;}
 const B13Clip *clip=&s->clips[state];
 if(!clip->xyz){s->previous_state=-1;return 0;}
 t%=clip->duration_ms;
 apply_clip(s,model,clip,t,now,state);
 return 1;
}
