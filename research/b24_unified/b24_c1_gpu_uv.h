#ifndef B24_C1_GPU_UV_H
#define B24_C1_GPU_UV_H
#include <stddef.h>
#include <stdint.h>
/* C1UV v1: exactly B24 C1G2 vertex order, original BDAE UV candidate pairs,
 * per-source-mesh flags; source atlas/UV interpretation is NOT uniformly
 * material-validated. 22 vehicle meshes already B12 atlas-verified separately.
 * No private original media shipped in C source. */
#define B24_C1_UV_VERTS 37946u
#define B24_C1_UV_MESHES 370u
typedef struct{float u,v;} B24C1UVPair;
typedef struct{
 B24C1UVPair *uv;
 unsigned char flags[B24_C1_UV_MESHES];
 size_t nverts,nmeshes;
 unsigned recognized_uv_meshes;
 int loaded;
} B24C1UV;
int b24_c1_uv_load(B24C1UV *dest,const char *path);
void b24_c1_uv_free(B24C1UV *dest);
#endif
