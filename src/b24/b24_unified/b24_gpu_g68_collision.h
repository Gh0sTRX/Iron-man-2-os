#ifndef B24_G70_COLLISION_H
#define B24_G70_COLLISION_H
#include "b24_c1_original_collision.h"
/* Same B24 gameplay collider ABI; source faces replaced with the real G68
 * original 1910-triangle scene set. B14/G7 movement resolution remains one
 * engine; G68 standalone physics/update loop not linked. */
int b24_g70_g68_collision_load(B24C1OriginalCollision *dst,const char *file);

/* G74 grounded-only original source walkable triangle under actor feet.
 * Only allow surfaces within .5 source world units of current height,
 * never snap to a remote tower or overpass. Existing G9 B14 motor is
 * the SINGLE velocity/camera owner; function is a data query only. */
int b24_g74_near_original_floor(const B24C1OriginalCollision *c,
 float player_x,float player_y,float expected_foot_z,float *out_floor_z);
#endif
