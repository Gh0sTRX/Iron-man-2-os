#ifndef G68_SUITCASE_RUNTIME_H
#define G68_SUITCASE_RUNTIME_H
/* Owns only animation playback for original Suitcase 629-vertex BRES; uses
 * original authored skinning frames pre-baked at 20 Hz by g68_pack_source_mark_v.
 * Not a claim to have ported original iOS engine animation state machine.
 * Include AFTER SourceMesh/Vertex and OpenGL headers.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#define G68_CLIPS 7
#define G68_ANIM_VERTS 629u
typedef struct {
 char name[16];
 uint32_t frames,duration;
 float *xyz;
} G68Clip;
typedef struct {
 uint16_t *mapping;
 G68Clip clips[G68_CLIPS];
 uint32_t packed_vertices;
 int ready;
 int last_clip,last_frame;
} G68Motion;
static G68Motion g68_motion={0};
static int g68_exact(FILE *fp,void *p,size_t bytes){
 return fp&&fread(p,1,bytes,fp)==bytes;
}
static int g68_load_motion(uint32_t packed_vertices){
 FILE *map=fopen("app0:assets/G68_armor_mapping.g68i","rb");
 if(!map)return 0;
 char magic[4];uint32_t meta[2]={0};
 if(!g68_exact(map,magic,4)||memcmp(magic,"G68I",4)||
    !g68_exact(map,meta,sizeof(meta))||meta[0]!=1||
    meta[1]!=packed_vertices||packed_vertices>65535||
    packed_vertices==0){fclose(map);return 0;}
 g68_motion.mapping=malloc((size_t)packed_vertices*sizeof(uint16_t));
 if(!g68_motion.mapping||
    !g68_exact(map,g68_motion.mapping,(size_t)packed_vertices*2)||
    fgetc(map)!=EOF){fclose(map);return 0;}
 fclose(map);
 for(uint32_t i=0;i<packed_vertices;i++)
  if(g68_motion.mapping[i]!=UINT16_MAX &&
     g68_motion.mapping[i]>=G68_ANIM_VERTS)return 0;
 FILE *fp=fopen("app0:assets/G68_suitcase_motion.g68a","rb");
 if(!fp)return 0;
 uint32_t hdr[3]={0};
 if(!g68_exact(fp,magic,4)||memcmp(magic,"G68A",4)||
    !g68_exact(fp,hdr,sizeof(hdr))||hdr[0]!=1||
    hdr[1]!=G68_ANIM_VERTS||hdr[2]!=G68_CLIPS){fclose(fp);return 0;}
 static const char * const labels[G68_CLIPS]={
  "idle","walk","fire","hover","rush","melee","land"};
 for(int i=0;i<G68_CLIPS;i++){
  G68Clip *c=&g68_motion.clips[i];
  if(!g68_exact(fp,c->name,16)||!g68_exact(fp,&c->frames,4)||
     !g68_exact(fp,&c->duration,4)||c->frames<2||c->frames>300||
     c->duration==0||c->duration>12000||
     memcmp(c->name,labels[i],strlen(labels[i])+1)){fclose(fp);return 0;}
  const size_t count=(size_t)c->frames*G68_ANIM_VERTS*3u;
  c->xyz=malloc(count*sizeof(float));
  if(!c->xyz||!g68_exact(fp,c->xyz,count*sizeof(float))){
   fclose(fp);return 0;
  }
  for(size_t j=0;j<count;j++)
   if(!isfinite(c->xyz[j])||fabsf(c->xyz[j])>1.e5f){
    fclose(fp);return 0;
   }
 }
 int eof=fgetc(fp)==EOF;fclose(fp);
 g68_motion.packed_vertices=packed_vertices;
 g68_motion.last_clip=-1;g68_motion.last_frame=-1;
 g68_motion.ready=eof;
 return eof;
}
/* Update only original skinned vertices, keeping authored UV/face winding.
 * 20Hz quantized poses; cached upload avoids CPU/GPU transfer on same frame. */
static void g68_pose(SourceMesh *suit,int clip,float local_time){
 if(!g68_motion.ready||!suit||!suit->v||
    clip<0||clip>=G68_CLIPS)return;
 G68Clip *c=&g68_motion.clips[clip];
 float duration=(float)c->duration*.001f;
 if(duration<=0)return;
 float t=fmodf(fmaxf(0.f,local_time),duration)/duration;
 int frame=(int)(t*(float)(c->frames-1));
 if(frame<0)frame=0;
 if(frame>=(int)c->frames)frame=(int)c->frames-1;
 if(clip==g68_motion.last_clip&&frame==g68_motion.last_frame)return;
 const float *points=c->xyz+(size_t)frame*G68_ANIM_VERTS*3u;
 for(uint32_t i=0;i<g68_motion.packed_vertices;i++){
  uint16_t src=g68_motion.mapping[i];
  if(src==UINT16_MAX)continue; /* true non-skinned source accessories */
  suit->v[i].p[0]=points[src*3];
  suit->v[i].p[1]=points[src*3+1];
  suit->v[i].p[2]=points[src*3+2];
 }
 glBindBuffer(GL_ARRAY_BUFFER,suit->vertex_buffer);
 glBufferData(GL_ARRAY_BUFFER,(GLsizeiptr)
    ((size_t)suit->nv*sizeof(Vertex)),suit->v,GL_DYNAMIC_DRAW);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 g68_motion.last_clip=clip;
 g68_motion.last_frame=frame;
}
#endif
