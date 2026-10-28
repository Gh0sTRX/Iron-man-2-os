#ifndef B24_GPU_HUD_NATIVE_H
#define B24_GPU_HUD_NATIVE_H
#include <stdint.h>
#include "b24_unified.h"
/* 480x272 coordinates are projected to physical 960x544 by vitaGL.
   All UI is CPU-generated VERTEX COMMANDS, GPU-rasterized triangles:
   NO 480x272 bitmap/texture upload per frame. */
#define B24_NATIVE_HUD_VERTICES 16384u
typedef struct {float x,y;uint32_t rgba;} B24NativeHudVertex;
typedef struct {
 B24NativeHudVertex vertices[B24_NATIVE_HUD_VERTICES];
 uint32_t count,quads;
 uint32_t missile_brackets,reticle_quads,pause_glyph_quads;
 int overflow;
} B24NativeHudGeometry;
int b24_native_hud_build(B24NativeHudGeometry *geom,const B24Unified *game);
void b24_native_hud_test_opponent(B24NativeHudGeometry *geom,int loaded,int spawned,float target_hp,float player_hp);
int b24_native_hud_draw(const B24NativeHudGeometry *geom);
#endif
