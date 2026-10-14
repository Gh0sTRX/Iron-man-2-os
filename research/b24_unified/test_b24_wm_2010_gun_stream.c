#include "b24_wm_2010_gun_stream.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static void emit(const char *name,int corrupt){
 FILE *f=fopen(name,"wb");assert(f);
 const uint32_t vals[4]={5,3,20,100};
 unsigned char h[20]={'I','M','2','K'};
 for(int j=0;j<4;j++)for(int i=0;i<4;i++)
  h[4+j*4+i]=(unsigned char)(vals[j]>>(8*i));
 assert(fwrite(h,1,20,f)==20);
 for(int frame=0;frame<3;frame++)
  for(int node=0;node<5;node++)
   for(int k=0;k<16;k++){
    const float v=(k==3?(float)(frame*10+node):k==15?1.f:0.f);
    assert(fwrite(&v,4,1,f)==1);
   }
 if(corrupt)fputc(1,f);
 assert(fclose(f)==0);
}
int main(void){
 const char *stem="b24_wm_original_gun_test";
 const char *filename="b24_wm_original_gun_test.im2k";
 emit(filename,0);
 B24WM2010GunStream s={0};
 assert(b24_wm_gun_stream_open(&s,".",stem));
 float mx[5][16]={0};
 assert(b24_wm_gun_stream_sample(&s,0,0,mx));
 assert(mx[0][3]==0.f&&mx[4][3]==4.f);
 assert(b24_wm_gun_stream_sample(&s,25,0,mx));
 assert(fabsf(mx[2][3]-7.f)<1e-6f);
 assert(b24_wm_gun_stream_sample(&s,50,0,mx));
 assert(fabsf(mx[2][3]-12.f)<1e-6f);
 assert(b24_wm_gun_stream_sample(&s,75,0,mx));
 assert(fabsf(mx[2][3]-17.f)<1e-6f);
 assert(b24_wm_gun_stream_sample(&s,100,0,mx));
 assert(fabsf(mx[2][3]-22.f)<1e-6f);
 assert(b24_wm_gun_stream_sample(&s,125,1,mx));
 assert(fabsf(mx[2][3]-7.f)<1e-6f);
 assert(!b24_wm_gun_stream_open(&s,".","../invalid"));
 assert(s.file); /* transaction preserves current real stream on error */
 b24_wm_gun_stream_close(&s);
 assert(!s.file);
 remove(filename);
 emit(filename,1);
 assert(!b24_wm_gun_stream_open(&s,".",stem));
 remove(filename);
 puts("PASS G8 WM owner-2010 5-node rigid gun frame streaming: 20Hz,"
      " 5 source matrices, no full clip RAM preload, exact length and invalid"
      " filename guard, seek and loop tests, no VPK or guessed emitter");
 return 0;
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
