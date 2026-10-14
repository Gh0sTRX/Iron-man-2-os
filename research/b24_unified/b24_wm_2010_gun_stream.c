#include "b24_wm_2010_gun_stream.h"
#include <math.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

static uint32_t le32(const unsigned char *p) {
 return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
        ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static int stem_safe(const char *s) {
 size_t n=0;
 if(!s)return 0;
 while(s[n]) {
  unsigned char c=(unsigned char)s[n];
  if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||
        (c>='0'&&c<='9')||c=='_'))return 0;
  if(++n>120)return 0;
 }
 return n>0;
}
void b24_wm_gun_stream_close(B24WM2010GunStream *s) {
 if(!s)return;
 if(s->file)fclose(s->file);
 memset(s,0,sizeof(*s));
}
int b24_wm_gun_stream_open(B24WM2010GunStream *s,const char *root,
                           const char *basename) {
 if(!s||!root||!stem_safe(basename))return 0;
 char path[512];
 int n=snprintf(path,sizeof(path),"%s/%s.im2k",root,basename);
 if(n<1||(size_t)n>=sizeof(path))return 0;
 FILE *f=fopen(path,"rb");
 if(!f)return 0;
 unsigned char header[20];
 if(fread(header,1,20,f)!=20||memcmp(header,"IM2K",4)!=0){
  fclose(f);return 0;
 }
 uint32_t nodes=le32(header+4),frames=le32(header+8);
 uint32_t fps=le32(header+12),duration=le32(header+16);
 uint64_t len=20ull+(uint64_t)frames*B24_WM_GUN_FRAME_FLOATS*4ull;
 uint32_t expected_frames=duration?(duration-1u)/50u+2u:1u;
 if(nodes!=B24_WM_GUN_NODES||fps!=20||duration>120000||
    frames!=expected_frames||frames<1||frames>3000||
    len>LONG_MAX||len>3000000||fseek(f,0,SEEK_END)!=0||
    ftell(f)!=(long)len){
  fclose(f);return 0;
 }
 B24WM2010GunStream new_stream={0};
 new_stream.file=f;new_stream.frames=frames;new_stream.duration_ms=duration;
 b24_wm_gun_stream_close(s);*s=new_stream;
 return 1;
}
static int fetch(B24WM2010GunStream *s,uint32_t i,float *dst){
 uint64_t pos=20ull+(uint64_t)i*B24_WM_GUN_FRAME_FLOATS*4ull;
 if(pos>LONG_MAX||fseek(s->file,(long)pos,SEEK_SET)!=0||
    fread(dst,sizeof(float),B24_WM_GUN_FRAME_FLOATS,s->file)!=
       B24_WM_GUN_FRAME_FLOATS)return 0;
 for(size_t k=0;k<B24_WM_GUN_FRAME_FLOATS;k++)
  if(!isfinite(dst[k])||fabsf(dst[k])>100000.f)return 0;
 return 1;
}
int b24_wm_gun_stream_sample(B24WM2010GunStream *s,uint32_t ms,
                             int loop,float out[6][16]){
 if(!s||!s->file||!out)return 0;
 uint32_t time=s->duration_ms?
   (loop?ms%s->duration_ms:
    (ms>s->duration_ms?s->duration_ms:ms)):0u;
 uint32_t frame=time/50u;
 if(s->frames==1)frame=0;
 else if(frame>=s->frames-1u)frame=s->frames-2u;
 if(!s->segment_valid||frame!=s->segment){
  if(!fetch(s,frame,s->frame_a)||
     (s->frames>1&&!fetch(s,frame+1u,s->frame_b)))return 0;
  s->segment=frame;s->segment_valid=1;
 }
 float weight=0.f;
 if(s->frames>1){
  uint32_t start=frame*50u;
  uint32_t end=frame==s->frames-2u?s->duration_ms:start+50u;
  if(end<=start)return 0;
  weight=(float)(time-start)/(float)(end-start);
  if(weight<0.f||weight>1.f)return 0;
 }
 /* Matrix element lerp is an APPROXIMATION between exact source frames.
    Use only as a diagnostic pose stream until a proper quaternion
    interpolation and the real game-world parent/root transform are wired. */
 for(size_t k=0;k<B24_WM_GUN_FRAME_FLOATS;k++)
  out[k/16][k%16]=s->frame_a[k]+
     (s->frames>1?(s->frame_b[k]-s->frame_a[k])*weight:0.f);
 return 1;
}

int b24_wm_gun_original_marker_axis(const float m[6][16],
                                   float tip[3],float dir[3]){
 if(!m||!tip||!dir)return 0;
 /* The two source markers are distinct Gun03 children in original BRES.
    Matrix layout is row-major and position is column 3. */
 float delta[3];
 float sq=0.f;
 for(int k=0;k<3;k++){
   const float a=m[4][k*4+3],b=m[5][k*4+3];
   if(!isfinite(a)||!isfinite(b))return 0;
   delta[k]=b-a;sq+=delta[k]*delta[k];
 }
 if(!isfinite(sq)||sq<1e-12f||sq>1e8f)return 0;
 const float inv=1.f/sqrtf(sq);
 for(int k=0;k<3;k++){
   tip[k]=m[5][k*4+3];
   dir[k]=delta[k]*inv;
 }
 return 1;
}
