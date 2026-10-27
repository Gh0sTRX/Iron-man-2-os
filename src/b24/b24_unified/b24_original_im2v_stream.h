#ifndef B24_ORIGINAL_IM2V_STREAM_H
#define B24_ORIGINAL_IM2V_STREAM_H
#include <stdint.h>
int b24_original_im2v_name_valid(const char *name);
#include <stdio.h>
#include <stddef.h>
/* Streaming original 2010 owner-source frames for G8+ motion bank.
   No full-304 RAM preload. NOT wired into G8 executable yet.
   Keep B14/B16 original 59 clip player unchanged until gameplay QA. */
typedef struct {
 FILE *file;
 float *frame_a, *frame_b;
 uint32_t nv, frames, fps, duration_ms, current_segment;
 int has_segment;
 char asset[192];
} B24OriginalIM2VStream;
int b24_original_im2v_open(B24OriginalIM2VStream *s,
                           const char *root_dir,const char *basename,
                           uint32_t expected_vertices);
int b24_original_im2v_sample(B24OriginalIM2VStream *s,
                            uint32_t time_ms,int looping,float *out_xyz);
void b24_original_im2v_close(B24OriginalIM2VStream *s);
size_t b24_original_im2v_working_bytes(const B24OriginalIM2VStream *s);
#endif
