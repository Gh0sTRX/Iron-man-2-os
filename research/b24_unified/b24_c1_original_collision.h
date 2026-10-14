#ifndef B24_C1_ORIGINAL_COLLISION_H
#define B24_C1_ORIGINAL_COLLISION_H
#include <stdint.h>
/* Actual 2010 iOS C1L1_col_01 + C1L1_building_col, not visual mesh boxes.
   CPU B14 physics only; graphics stays on GPU. Original world is Z UP.
   Intended as conservative wall sweep. C1L1_floor_001 source currently
   exposes ZERO indexed faces; existing floor semantics remain unresolved. */
#define B24_C1_COLLISION_MAX 2048u
typedef struct {
 float xyz[9],minx,maxx,miny,maxy,minz,maxz;
 uint32_t source;
 uint8_t wall;
} B24C1OriginalCollisionFace;
typedef struct {
 B24C1OriginalCollisionFace *faces;
 uint32_t count,wall_count;
 int ready;
} B24C1OriginalCollision;
int b24_c1_original_collision_load(B24C1OriginalCollision *c,const char *path);
void b24_c1_original_collision_free(B24C1OriginalCollision *c);
/* Reconcile one B14 world tick from (old x/y/z) to (new x/y/z).
   Only steep original source faces can block; never creates ground floors.
   Radius 0.12..0.9 original world units. Does not take/render VitaGL frames.
   Returns 0 ONLY on invalid input, never silently changes coordinates. */
int b24_c1_original_collision_resolve(const B24C1OriginalCollision *c,
 float oldx,float oldy,float oldz,float nextz,float radius,
 float *nextx,float *nexty);
#endif
