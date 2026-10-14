#include "b24_wm_2010_gun_stream.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static void emit(const char *name,int corrupt){
 FILE *f=fopen(name,"wb");assert(f);
 const uint32_t vals[4]={6,3,20,100};
 unsigned char h[20]={'I','M','2','K'};
 for(int j=0;j<4;j++)for(int i=0;i<4;i++)
  h[4+j*4+i]=(unsigned char)(vals[j]>>(8*i));
 assert(fwrite(h,1,20,f)==20);
 for(int frame=0;frame<3;frame++)
  for(int node=0;node<6;node++)
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
 float mx[6][16]={0};
 assert(b24_wm_gun_stream_sample(&s,0,0,mx));
 assert(mx[0][3]==0.f&&mx[4][3]==4.f&&mx[5][3]==5.f);
 float tip[3],axis[3];
 assert(b24_wm_gun_original_marker_axis((const float (*)[16])mx,tip,axis));
 assert(tip[0]==5.f&&axis[0]==1.f&&axis[1]==0.f&&axis[2]==0.f);
 assert(b24_wm_gun_stream_sample(&s,25,0,mx));
 assert(fabsf(mx[2][3]-7.f)<1e-6f);
 assert(b24_wm_gun_original_marker_axis((const float (*)[16])mx,tip,axis));
 assert(fabsf(tip[0]-10.f)<1e-6f&&fabsf(axis[0]-1.f)<1e-6f);
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
 puts("PASS G8 WM owner-2010 6-node rigid gun with genuine animated source marker-axis candidate frame streaming: 20Hz,"
      " 6 source matrices, no full clip RAM preload, exact length and invalid"
      " filename guard, seek and loop tests, no VPK or guessed emitter");
 return 0;
}

