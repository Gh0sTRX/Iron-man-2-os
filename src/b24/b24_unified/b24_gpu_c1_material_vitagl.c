#include "b24_gpu_c1_material.h"
#include <vitaGL.h>
#include <stddef.h>
static int good(const B24GpuC1Mesh *m,const B24C1UV *uv,uint32_t tex){
 if(!m||!m->vertices||!m->indices||m->vertex_count!=B24_GPU_C1_VERTS||
    m->index_count!=B24_GPU_C1_INDICES||!m->original_z_up)return 0;
 if(!tex)return 1;
 return uv&&uv->loaded&&uv->uv&&uv->nverts==m->vertex_count&&
        uv->nmeshes==B24_C1_UV_MESHES&&
        uv->recognized_uv_meshes==169u;
}
int b24_gpu_c1_draw_material(const B24GpuC1Mesh *m,const B24C1UV *uv,
                            uint32_t vehicle_atlas){
 if(!good(m,uv,vehicle_atlas))return 0;
 glEnable(GL_DEPTH_TEST);
 glEnableClientState(GL_VERTEX_ARRAY);
 glEnableClientState(GL_COLOR_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(B24GpuC1Vertex),&m->vertices[0].x);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(B24GpuC1Vertex),&m->vertices[0].rgba);
 unsigned index_end=0;
 for(unsigned i=0;i<B24_GPU_C1_BATCHES;i++){
  const B24GpuC1Batch *b=&m->batches[i];
  if(b->kind!=i||b->first_index!=index_end||!b->index_count||
     b->index_count%3||b->first_index+b->index_count>m->index_count){
      glDisableClientState(GL_COLOR_ARRAY);
      glDisableClientState(GL_VERTEX_ARRAY);
      return 0;
  }
  index_end=b->first_index+b->index_count;
  if(i==2 && vehicle_atlas){
    /* The ONLY texture assigned here is independently validated original
       C1L1 vehicle atlas. Not an automatic guess for ground or buildings. */
    glDisableClientState(GL_COLOR_ARRAY);
    glColor4f(1.f,1.f,1.f,1.f);
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D,(GLuint)vehicle_atlas);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glTexCoordPointer(2,GL_FLOAT,sizeof(B24C1UVPair),&uv->uv[0].u);
  }else{
    glDisable(GL_TEXTURE_2D);
  }
  glDrawElements(GL_TRIANGLES,(GLsizei)b->index_count,GL_UNSIGNED_SHORT,
                 m->indices+b->first_index);
  if(i==2 && vehicle_atlas){
    glDisableClientState(GL_TEXTURE_COORD_ARRAY);
    glDisable(GL_TEXTURE_2D);
    glEnableClientState(GL_COLOR_ARRAY);
  }
 }
 glDisableClientState(GL_COLOR_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);
 return index_end==m->index_count;
}
