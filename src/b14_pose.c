/* One authoritative pose per frame. B13 no longer overlays a fresh B7 base
 * pose and cannot snap to aimed-walk on the frame a state becomes unhandled. */
#include "b14_pose.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
int b14_pose_init(B14Pose *p,const IM2Model *m){
  memset(p,0,sizeof(*p));p->last_mode=-1;p->nverts=m->nv;
  p->from=(float*)malloc((size_t)m->nv*3*sizeof(float));return p->from!=NULL;
}
void b14_pose_free(B14Pose *p){if(!p)return;free(p->from);memset(p,0,sizeof(*p));}
B14Mode b14_pose_pick(const B13Motion *adv,int flying,int moving,int boost,int landing,unsigned rush_elapsed){
  if(!flying){if(landing)return B14_LAND;return !moving?B14_IDLE:(boost?B14_RUN:B14_WALK);}
  if(!moving)return B14_HOVER;
  if(boost && adv->armor!=2){
    if(rush_elapsed<250)return B14_RUSH1;
    if(rush_elapsed<500)return B14_RUSH6;
    if(rush_elapsed<750)return B14_RUSH12;
    return B14_RUSHFULL;
  }
  return B14_FLY;
}
/* Three distinct camera-relative flight stages. Character's actual velocity and
 * original pose are separate: no claim this is original Gameloft control code. */
B14Mode b15_pose_pick(const B13Motion *adv,int flying,int moving,int flight_stage,int boost,int landing,unsigned elapsed){
 if(!flying)return b14_pose_pick(adv,0,moving,boost,landing,elapsed);
 if(!moving || flight_stage==0)return B14_HOVER;
 if(flight_stage==1)return B14_DRIFT;
 if(flight_stage==2)return B14_FLY;
 if(elapsed<200)return B14_RUSH1;
 if(elapsed<400)return B14_RUSH6;
 if(elapsed<600)return B14_RUSH12;
 return B14_RUSHFULL;
}
static const B13Clip *get_adv(const B13Motion *a,int type){
 const B13Clip *p=type>=0&&type<B13_COUNT?&a->clips[type]:NULL;
 return p&&p->xyz?p:NULL;
}
static const B13Clip *select_adv(const B13Motion *a,B14Mode m){
 switch(m){
 case B14_IDLE:return get_adv(a,B13_GROUND_IDLE);
 case B14_WALK:return get_adv(a,B13_WALK);
 case B14_RUN:return get_adv(a,B13_RUN);
 case B14_DRIFT:return get_adv(a,a->armor==2?B13_FLOAT_MOVE:B13_AIR_MOVE);
 case B14_FLY:return get_adv(a,B13_FLY_NORMAL);
 case B14_RUSH1:return get_adv(a,B13_RUSH01);
 case B14_RUSH6:return get_adv(a,B13_RUSH06);
 case B14_RUSH12:return get_adv(a,B13_RUSH12);
 case B14_RUSHFULL:return get_adv(a,B13_RUSH_FULL);
 default:return NULL;
 }
}
int b14_pose_tick_ex(B14Pose *p,IM2Model *model,const B7Motion *base,const B13Motion *adv,B14Mode mode,unsigned now,const B13Clip *override){
 if(!p||!model||!base||!adv||!p->from||p->nverts!=model->nv||!base->rest)return 0;
 /* B7Clip and B13Clip share the same field layout; use data-only selection. */
 const float *xyz=NULL;unsigned frames=0,fps=0,duration=0;
 const B13Clip *newclip=override&&override->xyz?override:select_adv(adv,mode);
 if(newclip){xyz=newclip->xyz;frames=newclip->frames;fps=newclip->fps;duration=newclip->duration_ms;}
 else{
   const B7Clip *fallback=NULL;
   if(mode==B14_HOVER||mode==B14_DRIFT)fallback=&base->hover;
   if(mode==B14_FLY||(mode>=B14_RUSH1&&mode<=B14_RUSHFULL))fallback=&base->fly;
   if(mode==B14_WALK||mode==B14_RUN)fallback=&base->walk;
   if(mode==B14_LAND)fallback=adv->armor==2?&base->hover:&base->land;
   if(fallback&&fallback->xyz){xyz=fallback->xyz;frames=fallback->frames;fps=fallback->fps;duration=fallback->duration_ms;}
 }
 if((int)mode!=p->last_mode){
   for(unsigned i=0;i<model->nv;i++){
      p->from[3*i]=model->vertices[i].x;p->from[3*i+1]=model->vertices[i].y;p->from[3*i+2]=model->vertices[i].z;
   }
   p->last_mode=mode;p->fade_start=now;p->clip_start=now;p->changes++;
 }
 unsigned age=now-p->clip_start;
 int once=mode==B14_LAND;
 if(duration && xyz){
   unsigned ms=once?(age<duration?age:duration):(age%duration);
   unsigned idx=(unsigned)((uint64_t)ms*fps/1000u);if(idx>=frames)idx=frames-1;
   unsigned next=idx+1<frames?idx+1:idx;
   float alpha=(float)(ms-(idx*1000u/fps))*((float)fps/1000.f);
   if(alpha<0)alpha=0;
   if(alpha>1)alpha=1;
   float fade=(now-p->fade_start)/180.f;if(fade>1)fade=1;if(fade<0)fade=0;
   const float *a=xyz+(size_t)idx*p->nverts*3,*b=xyz+(size_t)next*p->nverts*3;
   for(unsigned i=0;i<model->nv;i++){
     const size_t k=(size_t)i*3;
     float v[3]={a[k]*(1-alpha)+b[k]*alpha,a[k+1]*(1-alpha)+b[k+1]*alpha,a[k+2]*(1-alpha)+b[k+2]*alpha};
     model->vertices[i].x=p->from[k]*(1-fade)+v[0]*fade;
     model->vertices[i].y=p->from[k+1]*(1-fade)+v[1]*fade;
     model->vertices[i].z=p->from[k+2]*(1-fade)+v[2]*fade;
   }
 }else{
   float fade=(now-p->fade_start)/180.f;if(fade>1)fade=1;if(fade<0)fade=0;
   for(unsigned i=0;i<model->nv;i++){
     size_t k=(size_t)i*3;
     model->vertices[i].x=p->from[k]*(1-fade)+base->rest[k]*fade;
     model->vertices[i].y=p->from[k+1]*(1-fade)+base->rest[k+1]*fade;
     model->vertices[i].z=p->from[k+2]*(1-fade)+base->rest[k+2]*fade;
   }
 }
 return 1;
}

int b14_pose_tick(B14Pose *p,IM2Model *model,const B7Motion *base,const B13Motion *adv,B14Mode mode,unsigned now){
 return b14_pose_tick_ex(p,model,base,adv,mode,now,NULL);
}
