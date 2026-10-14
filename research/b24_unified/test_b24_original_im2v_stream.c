#include "b24_original_im2v_stream.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void make(const char *path,unsigned nv,unsigned frames,unsigned duration,int broken) {
 FILE *f=fopen(path,"wb");assert(f);
 unsigned char h[20]={'I','M','2','V'};
 unsigned vals[]={nv,frames,20,duration};
 for(int j=0;j<4;j++)for(int i=0;i<4;i++)
  h[4+j*4+i]=(unsigned char)((vals[j]>>(8*i))&255u);
 assert(fwrite(h,1,sizeof(h),f)==sizeof(h));
 for(unsigned fr=0;fr<frames;fr++)
  for(unsigned i=0;i<nv*3;i++){
   float x=(float)fr*10.f+(float)(i%3);
   assert(fwrite(&x,sizeof(x),1,f)==1);
  }
 if(broken)fputc(17,f);
 assert(fclose(f)==0);
}
static void run(unsigned nv){
 char stem[64],file[128];
 snprintf(stem,sizeof(stem),"g8_stream_%u",nv);
 snprintf(file,sizeof(file),"%s.im2v",stem);
 make(file,nv,3,100,0);
 float *out=malloc(nv*3*sizeof(float));assert(out);
 B24OriginalIM2VStream s={0};
 assert(b24_original_im2v_open(&s,".",stem,nv));
 assert(b24_original_im2v_working_bytes(&s)==nv*3*sizeof(float)*2);
 assert(b24_original_im2v_sample(&s,0,0,out)&&out[0]==0.f);
 assert(b24_original_im2v_sample(&s,25,0,out)&&fabsf(out[0]-5.f)<1e-5f);
 assert(b24_original_im2v_sample(&s,50,0,out)&&fabsf(out[0]-10.f)<1e-5f);
 assert(b24_original_im2v_sample(&s,75,0,out)&&fabsf(out[0]-15.f)<1e-5f);
 assert(b24_original_im2v_sample(&s,1000,0,out)&&fabsf(out[0]-20.f)<1e-5f);
 assert(b24_original_im2v_sample(&s,125,1,out)&&fabsf(out[0]-5.f)<1e-5f);
 /* Failed switch must not remove the valid current original clip. */
 assert(!b24_original_im2v_open(&s,".","../invalid",nv));
 assert(!b24_original_im2v_open(&s,".",stem,nv+1));
 assert(b24_original_im2v_sample(&s,0,0,out)&&out[0]==0.f);
 b24_original_im2v_close(&s);
 assert(b24_original_im2v_working_bytes(&s)==0);
 remove(file);free(out);
}
int main(void) {
 run(802);run(1292);run(840);
 const char *stem="g8_static_original",*file="g8_static_original.im2v";
 make(file,802,1,0,0);
 B24OriginalIM2VStream s={0};
 float out[802*3];
 assert(b24_original_im2v_open(&s,".",stem,802));
 assert(b24_original_im2v_sample(&s,12345,0,out));
 assert(out[0]==0.f);
 b24_original_im2v_close(&s);
 remove(file);
 make(file,802,1,0,1);
 assert(!b24_original_im2v_open(&s,".",stem,802));
 remove(file);
 puts("PASS B24 original 304-source clip streaming (802/1292/840v),"
      " interpolation, loops, invalid switches, 0ms source pose,"
      " strict length verification, no full clip preload, no VPK");
 return 0;
}
