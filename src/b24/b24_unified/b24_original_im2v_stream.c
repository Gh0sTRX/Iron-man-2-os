#include "b24_original_im2v_stream.h"
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/* IM2V v1: 20 LE bytes: IM2V | uint32 vertices, frames, nominalFPS, duration.
   Followed by exactly frames*vertices*3 little-endian binary32 XYZ.
   Vita is LE binary32; keep explicit header reads to reject bad sources. */
static uint32_t rdle(const unsigned char *p) {
 return ((uint32_t)p[0])|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|
        ((uint32_t)p[3]<<24);
}
static int basename_ok(const char *s) {
 size_t n=0;
 if(!s)return 0;
 while(s[n]) {
  unsigned char c=(unsigned char)s[n];
  if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||
       (c>='0'&&c<='9')||c=='_'))return 0;
  if(++n>=120)return 0;
 }
 return n>0;
}
void b24_original_im2v_close(B24OriginalIM2VStream *s) {
 if(!s)return;
 if(s->file)fclose(s->file);
 free(s->frame_a);free(s->frame_b);
 memset(s,0,sizeof(*s));
}
static int read_frame(FILE *f,uint32_t index,uint32_t nv,float *dst) {
 uint64_t at=20ull+(uint64_t)index*(uint64_t)nv*12ull;
 size_t count=(size_t)nv*3u;
 if(at>LONG_MAX||fseek(f,(long)at,SEEK_SET)!=0||
    fread(dst,sizeof(float),count,f)!=count)return 0;
 for(size_t i=0;i<count;i++)if(!isfinite(dst[i]))return 0;
 return 1;
}
int b24_original_im2v_open(B24OriginalIM2VStream *s,
                           const char *root_dir,const char *basename,
                           uint32_t expected_vertices) {
 if(!s||!root_dir||!basename_ok(basename)||
    expected_vertices<3||expected_vertices>16000)return 0;
 char path[512];
 int nc=snprintf(path,sizeof(path),"%s/%s.im2v",root_dir,basename);
 if(nc<=0||(size_t)nc>=sizeof(path))return 0;
 FILE *f=fopen(path,"rb");
 if(!f)return 0;
 unsigned char h[20];
 if(fread(h,1,20,f)!=20||memcmp(h,"IM2V",4)!=0){fclose(f);return 0;}
 uint32_t nv=rdle(h+4),frames=rdle(h+8),fps=rdle(h+12),duration=rdle(h+16);
 uint64_t expected=20ull+(uint64_t)frames*(uint64_t)nv*12ull;
 if(nv!=expected_vertices||frames<1||frames>4000||fps!=20||
    duration>120000||expected>LONG_MAX||expected>100000000ull||
    ((duration==0)!=(frames==1))){fclose(f);return 0;}
 /* Source baker samples 0,50,... plus exact final duration (nonzero). */
 uint32_t samples=duration? (duration-1u)/50u+2u:1u;
 if(frames!=samples||fseek(f,0,SEEK_END)!=0||
    ftell(f)!=(long)expected){fclose(f);return 0;}
 float *a=malloc((size_t)nv*3*sizeof(float));
 float *b=malloc((size_t)nv*3*sizeof(float));
 if(!a||!b){free(a);free(b);fclose(f);return 0;}
 B24OriginalIM2VStream temp={0};
 temp.file=f;temp.frame_a=a;temp.frame_b=b;temp.nv=nv;
 temp.frames=frames;temp.fps=fps;temp.duration_ms=duration;
 temp.has_segment=0;temp.current_segment=0;
 memcpy(temp.asset,basename,strlen(basename)+1);
 /* Transactional: don't destroy currently playing clip on an invalid switch. */
 b24_original_im2v_close(s);
 *s=temp;
 return 1;
}
size_t b24_original_im2v_working_bytes(const B24OriginalIM2VStream *s) {
 if(!s||!s->file)return 0;
 return (size_t)s->nv*3*sizeof(float)*2;
}
int b24_original_im2v_sample(B24OriginalIM2VStream *s,
                            uint32_t time_ms,int looping,float *out_xyz) {
 if(!s||!s->file||!out_xyz||!s->frame_a||!s->frame_b)return 0;
 uint32_t time=0,seg=0;
 if(s->duration_ms) {
  time=(looping? time_ms%s->duration_ms :
        (time_ms>s->duration_ms?s->duration_ms:time_ms));
  seg=time/50u;
  if(seg>=s->frames-1u)seg=s->frames-2u;
 }
 if(!s->has_segment||s->current_segment!=seg) {
  if(!read_frame(s->file,seg,s->nv,s->frame_a)||
     (s->frames>1&&!read_frame(s->file,seg+1u,s->nv,s->frame_b)))
   return 0;
  s->current_segment=seg;s->has_segment=1;
 }
 float blend=0.f;
 if(s->frames>1) {
  uint32_t left=seg*50u;
  uint32_t right=(seg==s->frames-2u)?s->duration_ms:left+50u;
  if(right<=left)return 0;
  blend=(float)(time-left)/(float)(right-left);
  if(blend<0.f||blend>1.f)return 0;
 }
 size_t n=(size_t)s->nv*3u;
 for(size_t i=0;i<n;i++)
  out_xyz[i]=s->frame_a[i]+(s->frames>1?
                           (s->frame_b[i]-s->frame_a[i])*blend:0.f);
 return 1;
}
