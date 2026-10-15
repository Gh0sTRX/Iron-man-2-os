#include "mapviewer_m2_gpu.h"
#include <vitaGL.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int load_one(GLuint *id,GLenum target,const void *data,size_t n){
 glGenBuffers(1,id);
 if(!*id)return 0;
 glBindBuffer(target,*id);
 glBufferData(target,(GLsizeiptr)n,data,GL_STATIC_DRAW);
 return 1;
}
void m2_gpu_release(M2Gpu *g){
 if(!g)return;
 GLuint b[4]={(GLuint)g->vbo,(GLuint)g->uvbo,
              (GLuint)g->ebo_original,(GLuint)g->ebo_material};
 for(unsigned i=0;i<4;i++)if(b[i])glDeleteBuffers(1,&b[i]);
 memset(g,0,sizeof(*g));
}
int m2_gpu_load(M2Gpu *g,const B24GpuC1Mesh *mesh,
                const B24C1UV *uv,const B24C1MaterialBatchPlan *batches){
 if(!g||!mesh||!uv||!batches||!mesh->original_z_up||
     !mesh->vertices||!mesh->indices||!uv->loaded||!uv->uv||
     !batches->ready||!batches->indices||
     mesh->vertex_count!=37946u||mesh->index_count!=68757u||
     uv->nverts!=37946u||batches->index_count!=68757u)return 0;
 /* All original VitaGL source buffers static: no pointers into CPU RAM on draw. */
 M2Gpu t={0};
 int good=load_one((GLuint *)&t.vbo,GL_ARRAY_BUFFER,mesh->vertices,
                   mesh->vertex_count*sizeof(*mesh->vertices));
 if(good)good=load_one((GLuint *)&t.uvbo,GL_ARRAY_BUFFER,uv->uv,
                       uv->nverts*sizeof(*uv->uv));
 if(good)good=load_one((GLuint *)&t.ebo_original,GL_ELEMENT_ARRAY_BUFFER,
                       mesh->indices,mesh->index_count*sizeof(*mesh->indices));
 if(good)good=load_one((GLuint *)&t.ebo_material,GL_ELEMENT_ARRAY_BUFFER,
                       batches->indices,batches->index_count*sizeof(*batches->indices));
 glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 if(!good){m2_gpu_release(&t);g->upload_failed=1;return 0;}
 t.ready=1;
 m2_gpu_release(g);*g=t;
 return 1;
}
static void setup_xyz_and_colors(const M2Gpu *g,int with_color){
 glBindBuffer(GL_ARRAY_BUFFER,(GLuint)g->vbo);
 glEnableClientState(GL_VERTEX_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(B24GpuC1Vertex),(const void *)(uintptr_t)0);
 if(with_color){
  glEnableClientState(GL_COLOR_ARRAY);
  glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(B24GpuC1Vertex),(const void *)(uintptr_t)12u);
 }else{
  glDisableClientState(GL_COLOR_ARRAY);
  glColor4f(1.f,1.f,1.f,1.f);
 }
}
static void teardown(void){
 glDisableClientState(GL_COLOR_ARRAY);
 glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);
 glDisable(GL_TEXTURE_2D);
 glBindTexture(GL_TEXTURE_2D,0);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0);
}
/* group_filter 0=ALL; 1=ground 2=urban 3=vehicles 4=light polygon. */
int m2_gpu_draw(M2Gpu *g,const B24GpuC1Mesh *mesh,
       const B24C1MaterialBatchPlan *batches,
       const B24C1OriginalDiffuseBank *bank,
       int use_texture,int group_filter){
 if(!g||!g->ready||!mesh||!mesh->original_z_up||
    !batches||!batches->ready||group_filter<0||group_filter>4)return 0;
 g->submitted_draws=g->submitted_triangles=g->submitted_original_atlas_draws=0;
 glEnable(GL_DEPTH_TEST);
 glDisable(GL_CULL_FACE); /* don't hide reversed original source triangles */
 if(!use_texture){
  glDisable(GL_TEXTURE_2D);glDisableClientState(GL_TEXTURE_COORD_ARRAY);
  setup_xyz_and_colors(g,1);
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,(GLuint)g->ebo_original);
  for(unsigned i=0;i<4;i++){
   const B24GpuC1Batch *q=&mesh->batches[i];
   if(group_filter&&q->kind!=(unsigned)(group_filter-1))continue;
   glDrawElements(GL_TRIANGLES,(GLsizei)q->index_count,GL_UNSIGNED_SHORT,
                 (const void *)(uintptr_t)((size_t)q->first_index*sizeof(uint16_t)));
   g->submitted_draws++;
   g->submitted_triangles+=q->index_count/3u;
  }
  teardown();
  return 1;
 }
 if(!bank||!bank->loaded||!batches->indices)return 0;
 setup_xyz_and_colors(g,1);
 glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,(GLuint)g->ebo_material);
 int last_tex=-1,last_mode=0;
 for(unsigned i=0;i<batches->nbuckets;i++){
  const B24C1MaterialBucket *q=&batches->buckets[i];
  if(group_filter&&q->group!=(unsigned)(group_filter-1))continue;
  int index=b24_c1_2010_diffuse_bank_lookup(bank,q->material_id);
  GLuint tex=(q->group!=3u&&index>=0)?(GLuint)bank->gl_texture_ids[index]:0;
  int texmode=tex!=0;
  if(last_mode!=texmode){
   if(texmode){
    glDisableClientState(GL_COLOR_ARRAY);
    glColor4f(1.f,1.f,1.f,1.f);
    glEnable(GL_TEXTURE_2D);
    glBindBuffer(GL_ARRAY_BUFFER,(GLuint)g->uvbo);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glTexCoordPointer(2,GL_FLOAT,sizeof(B24C1UVPair),(const void *)(uintptr_t)0);
    glBindBuffer(GL_ARRAY_BUFFER,(GLuint)g->vbo);
   }else{
    glDisableClientState(GL_TEXTURE_COORD_ARRAY);
    glDisable(GL_TEXTURE_2D);
    glEnableClientState(GL_COLOR_ARRAY);
   }
   last_mode=texmode;
  }
  if(texmode&&index!=last_tex){
    glBindTexture(GL_TEXTURE_2D,tex);last_tex=index;
  }
  if(!texmode)last_tex=-1;
  glDrawElements(GL_TRIANGLES,(GLsizei)q->index_count,GL_UNSIGNED_SHORT,
       (const void *)(uintptr_t)((size_t)q->first_index*sizeof(uint16_t)));
  g->submitted_draws++;
  g->submitted_triangles+=q->index_count/3u;
  if(texmode)g->submitted_original_atlas_draws++;
 }
 teardown();
 return glGetError()==GL_NO_ERROR;
}
