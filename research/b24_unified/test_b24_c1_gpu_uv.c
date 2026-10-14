#include "b24_c1_gpu_uv.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static void invalid_file(const char *filename,int mode){
 FILE *in=fopen(filename,"rb");
 assert(in);
 assert(fseek(in,0,SEEK_END)==0);
 long n=ftell(in);assert(n>100000);
 rewind(in);
 unsigned char *b=malloc((size_t)n);assert(b);
 assert(fread(b,1,(size_t)n,in)==(size_t)n);fclose(in);
 if(mode==0)b[0]='X'; /* corrupt magic */
 if(mode==1)b[16]=99; /* original mesh flag must be 0 or 1 */
 if(mode==2){
    float value=NAN;
    memcpy(b+16+B24_C1_UV_MESHES+24,&value,sizeof(value));
 }
 if(mode==3)b[4]=88; /* invalid version */
 FILE *out=fopen("/tmp/b24-c1uv-malformed.bin","wb");assert(out);
 size_t size=mode==4?(size_t)n-1u:(size_t)n;
 assert(fwrite(b,1,size,out)==size);fclose(out);free(b);
 B24C1UV uv={0};
 assert(!b24_c1_uv_load(&uv,"/tmp/b24-c1uv-malformed.bin"));
 assert(!uv.loaded&&!uv.uv);
 remove("/tmp/b24-c1uv-malformed.bin");
}
int main(int argc,char **argv){
 assert(argc==2);
 B24C1UV uv={0};
 assert(!b24_c1_uv_load(&uv,"/tmp/never-created-C1UV.data"));
 assert(b24_c1_uv_load(&uv,argv[1]));
 assert(uv.loaded&&uv.nverts==37946u&&uv.nmeshes==370u);
 assert(uv.recognized_uv_meshes==169u);
 unsigned nonzero=0;
 for(unsigned i=0;i<B24_C1_UV_VERTS;i++){
  assert(isfinite(uv.uv[i].u)&&isfinite(uv.uv[i].v));
  if(fabsf(uv.uv[i].u)+fabsf(uv.uv[i].v)>.001f)nonzero++;
 }
 assert(nonzero>5000u);
 B24C1UV stale=uv;
 assert(!b24_c1_uv_load(&uv,"/tmp/never-created-C1UV.data"));
 assert(uv.uv==stale.uv&&uv.loaded); /* preserve prior valid UV on fail */
 b24_c1_uv_free(&uv);
 assert(!uv.loaded&&!uv.uv);
 for(int i=0;i<5;i++)invalid_file(argv[1],i);
 printf("PASS B24 original UV loader: 37946 coordinates, 169 verified-layout meshes, %u nonzero vertices, five corruption guards; NO VPK\n",nonzero);
}
