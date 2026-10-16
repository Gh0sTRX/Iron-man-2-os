#ifndef B24_G70_COLLISION_H
#define B24_G70_COLLISION_H
#include "b24_c1_original_collision.h"
/* Same B24 gameplay collider ABI; source faces replaced with the real G68
 * original 1910-triangle scene set. B14/G7 movement resolution remains one
 * engine; G68 standalone physics/update loop not linked. */
int b24_g70_g68_collision_load(B24C1OriginalCollision *dst,const char *file);
#endif
