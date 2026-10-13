#include "b24_c1_gpu_mesh.h"
#include <vitaGL.h>
#include <stddef.h>
/* THIS IS THE GPU SUBMISSION ADAPTER ONLY.
 * vitaGL context/window ownership + z-up projection are supplied by caller.
 * It intentionally NEVER calls SDL_UpdateTexture or a second present/swap.
 */
int b24_gpu_c1_draw_vitagl(const B24GpuC1Mesh *m){
    if(!m || !m->vertices || !m->indices ||
       !m->original_z_up ||m->vertex_count!=B24_GPU_C1_VERTS ||
       m->index_count!=B24_GPU_C1_INDICES)return 0;
    glEnable(GL_DEPTH_TEST);
    glDisable(GL_TEXTURE_2D); /* original C1L1 UV not yet recovered */
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_COLOR_ARRAY);
    glVertexPointer(3,GL_FLOAT,sizeof(B24GpuC1Vertex),&m->vertices[0].x);
    glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(B24GpuC1Vertex),&m->vertices[0].rgba);
    for(unsigned i=0;i<B24_GPU_C1_BATCHES;i++){
        const B24GpuC1Batch *b=&m->batches[i];
        if(!b->index_count||b->first_index+b->index_count>m->index_count){
            glDisableClientState(GL_COLOR_ARRAY);
            glDisableClientState(GL_VERTEX_ARRAY);return 0;
        }
        glDrawElements(GL_TRIANGLES,(GLsizei)b->index_count,GL_UNSIGNED_SHORT,
                       (const void *)(m->indices+b->first_index));
    }
    glDisableClientState(GL_COLOR_ARRAY);
    glDisableClientState(GL_VERTEX_ARRAY);
    return 1;
}
