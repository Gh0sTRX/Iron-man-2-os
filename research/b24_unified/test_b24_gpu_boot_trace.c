#include "b24_gpu_boot_trace.h"
#include <stdio.h>
#include <assert.h>
#include <string.h>
int main(void){
 assert(b24_gpu_boot_trace_reset());
 assert(b24_gpu_boot_trace_mark("10 SDL_INIT_BEGIN"));
 assert(b24_gpu_boot_trace_mark("20 C1G2_SCENE_LOADED"));
 assert(b24_gpu_boot_trace_mark("30 VGL_INIT_BEGIN"));
 FILE *f=fopen(B24_GPU_TRACE_PATH,"rb");assert(f);
 char line[180]; unsigned count=0;
 const char *expect[]={
 "000 B24 GPU EARLY BOOT - THIS IS NOT A CORE BACKTRACE\n",
 "001 10 SDL_INIT_BEGIN\n",
 "002 20 C1G2_SCENE_LOADED\n",
 "003 30 VGL_INIT_BEGIN\n"
 };
 while(fgets(line,sizeof(line),f)){
  assert(count<4&&strcmp(line,expect[count])==0);
  count++;
 }
 fclose(f);assert(count==4);
 assert(remove(B24_GPU_TRACE_PATH)==0);
 puts("PASS local opt-in Vita GPU crash breadcrumb file is durable and ordered");
 return 0;
}
