#ifndef B24_G108_VISIBLE_ORIGINAL_WALL_GRID_H
#define B24_G108_VISIBLE_ORIGINAL_WALL_GRID_H
#include "b24_c1_original_collision.h"
#include <stdint.h>
/* 2010 sourced C1L1 original 22,441 drawn triangles > 1,910 source
 * collider faces. Supplemental *visual-derived* steep faces are experimental
 * solid-surface candidates, NOT claimed as original CollisionEntity rules.
 * Single B14/G75 motor. Opaque source batch only, no sky/alpha cards.
 * Preindexed at startup, NOT a full 22k collision loop per physics step.
 */
typedef struct {
 float p[9];
 float minx,maxx,miny,maxy,minz,maxz;
 uint32_t source_batch;
} B24G108Wall;
typedef struct {
 B24G108Wall *walls;
 uint32_t count,capacity;
 uint32_t *cell_offsets,*cell_indices;
 uint32_t cell_index_count,ready;
 uint32_t skipped_alpha,skipped_duplicate,skipped_large;
 uint32_t skipped_not_steep;
} B24G108Grid;
int b24_g108_grid_load(B24G108Grid *g,const char *visual_g66m,
 const B24C1OriginalCollision *native_collider);
void b24_g108_grid_close(B24G108Grid *g);
int b24_g108_grid_clear(const B24G108Grid *g,float x,float y,float footz,
 float radius,float height);
/* QA only: find a true source visual wall for a self-intersection test. */
int b24_g108_grid_probe(const B24G108Grid *g,float *x,float *y,float *footz);
#endif
