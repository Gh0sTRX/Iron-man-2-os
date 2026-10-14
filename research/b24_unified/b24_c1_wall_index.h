#ifndef B24_C1_WALL_INDEX_H
#define B24_C1_WALL_INDEX_H
#include "b24_c1_gpu_mesh.h"
#include <stdint.h>
#include <stddef.h>
/* Source-validated C1G2 wall candidate spatial index. CPU-ONLY, no GL calls.
   Coordinates = original B17 Z-up (not screen), source triangle identity
   preserved. This module PREPARES collision, it does not yet change physics.
   Query is broadphase only: candidates are not confirmed contacts! */
#define B24_C1_WALL_CELL_SIZE 12.f
#define B24_C1_WALL_MAX_REFS 262144u
typedef struct {
 float xyz[9],minz,maxz;
 uint32_t original_face,source_group;
} B24C1WallFace;
typedef struct {
 int32_t cx,cy;
 uint32_t wall;
} B24C1WallRef;
typedef struct {
 B24C1WallFace *walls;
 B24C1WallRef *refs;
 uint32_t wall_count,ref_count,rejected_degenerate;
 uint32_t rejected_nonground,scanned_faces;
} B24C1WallIndex;
int b24_c1_wall_index_build(B24C1WallIndex *dst,const B24GpuC1Mesh *scene);
void b24_c1_wall_index_free(B24C1WallIndex *dst);
/* Returns 0 on invalid input OR overflow. Caller must never ignore failure.
   Output contains unique candidate wall IDs within neighboring 2D grid cells
   and overlapping the supplied torso Z. Narrowphase still required. */
int b24_c1_wall_index_query(const B24C1WallIndex *index,
  float x,float y,float torso_z,float radius,
  uint32_t *ids,size_t capacity,size_t *count);
#endif
