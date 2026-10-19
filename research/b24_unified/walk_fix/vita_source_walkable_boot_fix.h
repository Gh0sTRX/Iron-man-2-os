#ifndef IM2_VITA_SOURCE_WALKABLE_BOOT_FIX_H
#define IM2_VITA_SOURCE_WALKABLE_BOOT_FIX_H
#include "b24_gpu_g68_collision.h"
/* TEST-ONLY Vita B14 bootstrap from unchanged original 2010 G66C surfaces.
 * Not the original iOS mission start/world transform. Do not silently
 * ship as the native 2010 MC spawn; retains original G66C walls and B14.
 * Returns 1 only for an actual source floor allowing at least 6/8 moves.
 */
typedef struct {
 float x,y,z;
 unsigned accepted_directions;
 unsigned source_floor_candidates;
} Im2VitaGroundBootCandidate;
int im2_vita_source_walkable_boot(const B24C1OriginalCollision *original,
  float preferred_x,float preferred_y,float preferred_z,
  Im2VitaGroundBootCandidate *result);
#endif
