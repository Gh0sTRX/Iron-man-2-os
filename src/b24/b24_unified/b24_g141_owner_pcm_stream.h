#ifndef B24_G141_OWNER_PCM_STREAM_H
#define B24_G141_OWNER_PCM_STREAM_H
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
/* G141: read PCM decoded from real user-original 2010 RIFF/WAVE .www
 * to 48kHz / S16LE / interleaved stereo via FFmpeg offline. This IS
 * a new Vita backend format, NOT the original 2010 iOS sound mixer.
 * Lua ID88/320 identities are verified; other IDs require the external
 * native-table-validated catalog. Gameplay event binding is separate. */
typedef struct {
 FILE *file;
 uint32_t source_bytes;
 uint32_t bytes_read;
 int loop;
 int paused;
 int finished;
} B24G141PcmStream;
int b24_g141_pcm_open(B24G141PcmStream *s,const char *path,int loop);
size_t b24_g141_pcm_fill(B24G141PcmStream *s,void *buffer,size_t frame_count);
void b24_g141_pcm_pause(B24G141PcmStream *s,int pause);
void b24_g141_pcm_close(B24G141PcmStream *s);
#endif
