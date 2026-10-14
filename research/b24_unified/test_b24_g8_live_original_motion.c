#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {float x,y,z,u,v;} Vertex;
static void author_file(const char *stem,unsigned nv,int offset) {
 char name[256];snprintf(name,sizeof(name),"%s.im2v",stem);
 FILE *f=fopen(name,"wb");assert(f);
 unsigned char h[20]={'I','M','2','V'};
 unsigned fields[]={nv,5,20,200};
 for(unsigned j=0;j<4;j++)for(unsigned k=0;k<4;k++)
  h[4+j*4+k]=(unsigned char)((fields[j]>>(8*k))&255u);
 assert(fwrite(h,1,20,f)==20);
 for(unsigned t=0;t<5;t++)for(unsigned i=0;i<nv;i++)
  for(int axis=0;axis<3;axis++){
   float val=(float)offset+(float)t+0.01f*(float)(i%11)+(float)axis*.1f;
   assert(fwrite(&val,sizeof(float),1,f)==1);
  }
 fclose(f);
}
static void run_source(int suit,unsigned nv,const char *left,const char *right){
 author_file(left,nv,2);
 author_file(right,nv,12);
 Vertex *verts=calloc(nv,sizeof(Vertex));assert(verts);
 B24G8LiveOriginalMotion live={0};
 for(unsigned i=0;i<nv;i++){verts[i].u=.26f;verts[i].v=.74f;}
 /* Existing B14 already computed another pose: use it as first blend source. */
 assert(b24_g8_motion_tick(&live,".",verts,sizeof(*verts),nv,suit,
                          B24M_DRIFT,-.8f,0.f,1000));
 assert(live.active&&live.transitions==1);
 assert(strcmp(live.selected,left)==0);
 assert(fabsf(verts[0].x)<.0001f);
 assert(b24_g8_motion_tick(&live,".",verts,sizeof(*verts),nv,suit,
                          B24M_DRIFT,-.8f,0.f,1100));
 assert(verts[0].x>0.f&&verts[0].x<10.f);
 float previous=verts[0].x;
 /* B14 would rewrite legacy pose every frame. New source switch must not
    reset to that intermediary, and the 1st original transition frame
    must start from last original rendered pose. */
 for(unsigned i=0;i<nv;i++)verts[i].x=-777.f;
 assert(b24_g8_motion_tick(&live,".",verts,sizeof(*verts),nv,suit,
                          B24M_DRIFT,.9f,0.f,1116));
 assert(fabsf(verts[0].x-previous)<1.e-4f);
 assert(live.transitions==2);
 assert(b24_g8_motion_tick(&live,".",verts,sizeof(*verts),nv,suit,
                          B24M_DRIFT,.9f,0.f,1220));
 assert(verts[0].x>previous);
 assert(fabsf(verts[0].u-.26f)<1.e-5f);
 assert(live.successful_frames==4);
 b24_g8_motion_release(&live);
 assert(!live.stream.file);
 free(verts);
 char file[256];snprintf(file,sizeof(file),"%s.im2v",left);remove(file);
 snprintf(file,sizeof(file),"%s.im2v",right);remove(file);
}
int main(void){
 assert(!strcmp(b24_g8_motion_route(0,B24M_RUSH,0,1),
                "ironman_ironman_fly_f_rush"));
 assert(!strcmp(b24_g8_motion_route(0,B24M_CRUISE,-.8f,0),
                "ironman_ironman_fly_l"));
 assert(!strcmp(b24_g8_motion_route(2,B24M_CRUISE,1,0),
                "warmachine_warmachine_aim_fly_m"));
 assert(!strcmp(b24_g8_motion_route(0,B24M_WALK,0,-.9f),
                "ironman_ironman_walk_b"));
 assert(b24_g8_motion_route(2,B24M_RUN,0,1)==NULL);
 assert(b24_g8_motion_route(1,B24M_HOVER,0,0)==NULL);
 assert(b24_g8_motion_route(0,B24M_LAND,0,0)==NULL);
 run_source(0,802,"ironman_ironman_aim_float_move_l",
                     "ironman_ironman_aim_float_move_r");
 run_source(2,1292,"warmachine_warmachine_aim_float_move_l",
                      "warmachine_warmachine_aim_float_move_r");
 B24G8LiveOriginalMotion missing={0};
 Vertex v[802];memset(v,0,sizeof(v));
 v[0].x=99.f;
 assert(b24_g8_motion_tick(&missing,".",v,sizeof(Vertex),802,0,
                          B24M_RUSH,0,1,1000));
 assert(v[0].x==99.f&&missing.misses==1&&!missing.active);
 assert(b24_g8_motion_tick(&missing,".",v,sizeof(Vertex),802,0,
                          B24M_RUSH,0,1,1016));
 assert(missing.misses==1); /* avoid retry per frame */
 b24_g8_motion_release(&missing);
 puts("PASS G8 B14 source-motion integration 802/1292: real routed source"
      " stream, no snap on L/R interrupt, unchanged UV, unchanged 59 fallback,"
      " unsupported suit preserved, no VPK");
 return 0;
}
