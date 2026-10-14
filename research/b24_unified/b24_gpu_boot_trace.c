#include "b24_gpu_boot_trace.h"
#ifdef B24_GPU_BOOT_TRACE
#include <stdio.h>
#include <string.h>
#ifndef B24_GPU_TRACE_PATH
#define B24_GPU_TRACE_PATH "ux0:data/IronMan2_GPU_BOOT.txt"
#endif
/* Explicit buffered file CLOSE on each boot-critical phase. No file system
   background thread, no allocations, no real-time per-frame recording. */
static unsigned b24_trace_sequence=0;
static int trace_write(const char *mode,const char *stage){
 if(!stage||!stage[0]||strlen(stage)>88u)return 0;
 FILE *f=fopen(B24_GPU_TRACE_PATH,mode);
 if(!f)return 0;
 int ok=fprintf(f,"%03u %s\n",b24_trace_sequence,stage)>0;
 if(fflush(f)!=0)ok=0;
 if(fclose(f)!=0)ok=0;
 return ok;
}
int b24_gpu_boot_trace_reset(void){
 b24_trace_sequence=0;
 return trace_write("wb","B24 GPU EARLY BOOT - THIS IS NOT A CORE BACKTRACE");
}
int b24_gpu_boot_trace_mark(const char *stage){
 if(!stage||b24_trace_sequence>=999u)return 0;
 b24_trace_sequence++;
 return trace_write("ab",stage);
}
#endif
