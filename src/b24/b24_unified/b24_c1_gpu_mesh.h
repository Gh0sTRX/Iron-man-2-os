#ifndef B24_C1_GPU_MESH_H
#define B24_C1_GPU_MESH_H
#include <stddef.h>
#include <stdint.h>
/* Private game-source C1G2 v2: original Z-up coordinates, NOT real UV/restored scene. */
#define B24_GPU_C1_BATCHES 4
#define B24_GPU_C1_VERTS 37946u
#define B24_GPU_C1_INDICES 68757u
typedef struct {float x,y,z;uint32_t rgba;} B24GpuC1Vertex;
typedef struct {
    uint32_t kind,first_index,index_count,source_meshes;
    float bbox[6];
} B24GpuC1Batch;
typedef struct {
    B24GpuC1Vertex *vertices;
    uint16_t *indices;
    B24GpuC1Batch batches[B24_GPU_C1_BATCHES];
    size_t vertex_count,index_count;
    int original_z_up;
} B24GpuC1Mesh;
int b24_gpu_c1_load(B24GpuC1Mesh *mesh,const char *path);
void b24_gpu_c1_free(B24GpuC1Mesh *mesh);
/* NO GL context ownership. Caller must have active graphics context,
   original B17 Z-up camera and full viewport projection bound. */
int b24_gpu_c1_draw_vitagl(const B24GpuC1Mesh *mesh);
#endif
