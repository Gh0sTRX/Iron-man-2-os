#ifndef B24_G73_SOURCE_SKY_H
#define B24_G73_SOURCE_SKY_H
#include <stdint.h>
/* Genuine owner 2010 source BRES C1L1_sky_001 geometry and recovered
 * sky_02/sky_03 PVR pixels; source material ID->sampler link NOT YET PROVEN.
 * Render using same B24 GPU context, before original city, no physics. */
typedef struct {
 uint32_t vbo,tex[2],ready;
 uint32_t first[6],count[6],atlas[6];
} B24G73Sky;
int b24_g73_sky_open(B24G73Sky *sky);
int b24_g73_sky_draw(const B24G73Sky *sky);
void b24_g73_sky_close(B24G73Sky *sky);
#endif
