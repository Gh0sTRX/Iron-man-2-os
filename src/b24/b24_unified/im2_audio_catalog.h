#ifndef IM2_AUDIO_CATALOG_H
#define IM2_AUDIO_CATALOG_H
#include <stddef.h>
int im2_audio_catalog_load(const char *path);
int im2_audio_catalog_decode(const void *data,size_t bytes);
const char *im2_audio_catalog_pcm(int original_lua_id);
void im2_audio_catalog_close(void);
#endif
