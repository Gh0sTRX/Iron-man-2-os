#ifndef IM2_GPU_FLOOR_MESH_H
#define IM2_GPU_FLOOR_MESH_H
#include <stdint.h>
/* B17 uses Z-up world with floor z=-1; independent mesh builder, NOT a Vita renderer. */
#define IM2_GPU_FLOOR_SIDE 11
#define IM2_GPU_FLOOR_VERTS (IM2_GPU_FLOOR_SIDE * IM2_GPU_FLOOR_SIDE * 4)
#define IM2_GPU_FLOOR_INDICES (IM2_GPU_FLOOR_SIDE * IM2_GPU_FLOOR_SIDE * 6)
typedef struct { float x,y,z; float r,g,b; float u,v; } Im2GpuFloorVertex;
typedef struct {
    Im2GpuFloorVertex vertices[IM2_GPU_FLOOR_VERTS];
    uint16_t indices[IM2_GPU_FLOOR_INDICES];
    unsigned vertex_count,index_count;
    int tile_x,tile_y;
} Im2GpuFloorMesh;
/* 121 rectangular panels, 242 triangles, no framebuffer pixel loops. */
int im2_gpu_floor_build(Im2GpuFloorMesh *mesh,float player_x,float player_y);
#endif
