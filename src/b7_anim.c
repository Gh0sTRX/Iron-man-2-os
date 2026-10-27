#include "b7_anim.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static uint32_t get32(FILE *f,int *ok){unsigned char x[4];if(fread(x,1,4,f)!=4){*ok=0;return 0;}return (uint32_t)x[0]|((uint32_t)x[1]<<8)|((uint32_t)x[2]<<16)|((uint32_t)x[3]<<24);}
static int readclip(B7Clip *dst,const char *name,uint32_t expected){
    char path[160];
#ifdef __vita__
    snprintf(path,sizeof(path),"app0:animations/%s.im2v",name);
#else
    snprintf(path,sizeof(path),"animations/%s.im2v",name);
#endif
    FILE *f=fopen(path,"rb");if(!f)return 0;
    char head[4];int ok=1;
    if(fread(head,1,4,f)!=4||memcmp(head,"IM2V",4)){fclose(f);return 0;}
    uint32_t verts=get32(f,&ok),frames=get32(f,&ok),fps=get32(f,&ok),duration=get32(f,&ok);
    if(!ok||verts!=expected||frames<2||frames>256||fps<1||fps>120||duration>60000){fclose(f);return 0;}
    const size_t elements=(size_t)verts*3u*frames;
    if(elements>1500000u){fclose(f);return 0;}
    float *data=(float*)malloc(elements*sizeof(float));
    if(!data){fclose(f);return 0;}
    if(fread(data,sizeof(float),elements,f)!=elements){free(data);fclose(f);return 0;}
    if(fgetc(f)!=EOF){free(data);fclose(f);return 0;}
    fclose(f);
    for(size_t i=0;i<elements;i++)if(!isfinite(data[i])){free(data);return 0;}
    dst->xyz=data;dst->verts=verts;dst->frames=frames;dst->fps=fps;dst->duration_ms=duration;
    return 1;
}
void b7_release(B7Motion *m){
    if(!m)return;
    free(m->hover.xyz);free(m->walk.xyz);free(m->land.xyz);free(m->fly.xyz);free(m->rest);
    memset(m,0,sizeof(*m));
}
int b7_prepare(B7Motion *m,unsigned armor,const IM2Model *model){
    b7_release(m);
    if(!model||!model->vertices||!model->nv)return 0;
    m->rest=(float*)malloc((size_t)model->nv*3*sizeof(float));
    if(!m->rest)return 0;
    m->nverts=model->nv;
    for(unsigned i=0;i<model->nv;i++){
      m->rest[3*i+0]=model->vertices[i].x;
      m->rest[3*i+1]=model->vertices[i].y;
      m->rest[3*i+2]=model->vertices[i].z;
    }
    /* B9: Mark IV and Stealth have byte-identical position/UV layout to Mark VI.
       Hence Mark VI's original-skinned vertex streams can be reused exactly.
       SuitCase is the authentic fifth playable suit, with unique 629-vertex rig. */
    if(armor==0 || armor==1 || armor==3){
      if(!readclip(&m->hover,"mark6_hover",model->nv)||
         !readclip(&m->walk,"mark6_walk",model->nv)||
         !readclip(&m->land,"mark6_land",model->nv)||
         !readclip(&m->fly,"mark6_fly",model->nv)){b7_release(m);return 0;}
    }else if(armor==2){
      if(!readclip(&m->hover,"warmachine_hover",model->nv)||
         !readclip(&m->walk,"warmachine_walk",model->nv)||
         !readclip(&m->fly,"warmachine_fly",model->nv)||
         !readclip(&m->land,"warmachine_land",model->nv)){b7_release(m);return 0;}
    }else if(armor==4){
      if(!readclip(&m->hover,"suitcase_hover",model->nv)||
         !readclip(&m->walk,"suitcase_walk",model->nv)||
         !readclip(&m->land,"suitcase_land",model->nv)||
         !readclip(&m->fly,"suitcase_fly",model->nv)){b7_release(m);return 0;}
    }else{b7_release(m);return 0;}
    return 1;
}
void b7_apply(B7Motion *m,IM2Model *model,int flying,int walking,int landing,
              unsigned frame_time_ms,unsigned elapsed_ms){
    if(!m||!m->rest||m->nverts!=model->nv)return;
    const B7Clip *clip=NULL;
    if(landing && m->land.xyz)clip=&m->land;
    else if(flying){
       if(walking && m->fly.xyz)clip=&m->fly;
       else if(m->hover.xyz)clip=&m->hover;
    }else if(walking && m->walk.xyz)clip=&m->walk;
    const float *points=m->rest;
    if(clip){
      unsigned t=landing?elapsed_ms:frame_time_ms;
      if(!landing){t%=clip->duration_ms?clip->duration_ms:1;}
      if(t>clip->duration_ms)t=clip->duration_ms;
      unsigned index=(unsigned)((uint64_t)t*clip->fps/1000u);
      if(index>=clip->frames)index=clip->frames-1;
      points=clip->xyz+(size_t)index*clip->verts*3;
    }
    for(unsigned i=0;i<model->nv;i++){
      model->vertices[i].x=points[3*i+0];
      model->vertices[i].y=points[3*i+1];
      model->vertices[i].z=points[3*i+2];
    }
}
