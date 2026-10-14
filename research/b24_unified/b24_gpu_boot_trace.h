#ifndef B24_GPU_BOOT_TRACE_H
#define B24_GPU_BOOT_TRACE_H
/* Developer-only Vita crash breadcrumb, opt-in. Not a replacement for the
   authoritative ux0:data/psp2core-*.psp2dmp and corresponding app ELF.
   Each short stage is flushed/closed before unsafe GPU calls. No telemetry,
   no network, no game asset bytes. */
#ifdef B24_GPU_BOOT_TRACE
int b24_gpu_boot_trace_reset(void);
int b24_gpu_boot_trace_mark(const char *stage);
#else
static inline int b24_gpu_boot_trace_reset(void){return 1;}
static inline int b24_gpu_boot_trace_mark(const char *stage){
 (void)stage;return 1;
}
#endif
#endif
