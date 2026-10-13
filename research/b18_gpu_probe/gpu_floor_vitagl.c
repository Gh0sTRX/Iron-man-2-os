#include "gpu_floor_mesh.h"
#include <stddef.h>
/* Experimental B17 floor GPU draw adapter. A REAL active vitaGL context,
   correct camera view/projection and render pass MUST be provided by caller.
   This function does not call SDL_UpdateTexture and must not run in its context. */
#include <vitaGL.h>

int im2_gpu_floor_draw_vitagl(const Im2GpuFloorMesh *mesh) {
    if (!mesh||mesh->vertex_count!=IM2_GPU_FLOOR_VERTS||
        mesh->index_count!=IM2_GPU_FLOOR_INDICES)return 0;
    glEnable(GL_DEPTH_TEST);
    glDisable(GL_TEXTURE_2D);
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_COLOR_ARRAY);
    glVertexPointer(3,GL_FLOAT,(GLsizei)sizeof(Im2GpuFloorVertex),&mesh->vertices[0].x);
    glColorPointer(3,GL_FLOAT,(GLsizei)sizeof(Im2GpuFloorVertex),&mesh->vertices[0].r);
    glDrawElements(GL_TRIANGLES,(GLsizei)mesh->index_count,GL_UNSIGNED_SHORT,mesh->indices);
    glDisableClientState(GL_COLOR_ARRAY);
    glDisableClientState(GL_VERTEX_ARRAY);
    return 1;
}
