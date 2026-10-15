#include "b24_gpu_c1_2010_textured_material.h"
#include <vitaGL.h>
#include <stddef.h>
int b24_gpu_c1_draw_original_2010_world(const B24GpuC1Mesh *m,
 const B24C1UV *uv,const B24C1MaterialBatchPlan *plan,
 const B24C1OriginalDiffuseBank *bank){
 if(!m||!uv||!plan||!bank||!m->vertices||!m->indices||
    !uv->uv||!uv->loaded||!plan->ready||!plan->indices||
    !bank->loaded||bank->source_verified_count==0||
    !m->original_z_up||m->vertex_count!=B24_GPU_C1_VERTS||
    m->index_count!=B24_GPU_C1_INDICES||
    uv->nverts!=m->vertex_count||uv->nmeshes!=B24_C1_UV_MESHES||
    plan->index_count!=m->index_count||plan->nbuckets==0||
    plan->nbuckets>B24_C1_MAX_MATERIAL_BUCKETS)return 0;
 glEnable(GL_DEPTH_TEST);
 glEnableClientState(GL_VERTEX_ARRAY);
 glEnableClientState(GL_COLOR_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(B24GpuC1Vertex),&m->vertices[0].x);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(B24GpuC1Vertex),&m->vertices[0].rgba);
 glDisable(GL_TEXTURE_2D);
 glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 unsigned next=0;
 int last_tex=-1;int textured=0;
 for(unsigned b=0;b<plan->nbuckets;b++){
  const B24C1MaterialBucket *q=&plan->buckets[b];
  if(q->group>=B24_GPU_C1_BATCHES||
     q->material_id>=B24_C1_2010_MATERIALS||
     q->first_index!=next||q->index_count==0||
     q->index_count%3u||q->index_count>m->index_count-next){
    glDisableClientState(GL_TEXTURE_COORD_ARRAY);
    glDisable(GL_TEXTURE_2D);
    glDisableClientState(GL_COLOR_ARRAY);
    glDisableClientState(GL_VERTEX_ARRAY);
    return 0;
  }
  next+=q->index_count;
  int texidx=q->group==3u?-1:b24_c1_2010_diffuse_bank_lookup(bank,q->material_id);
  GLuint tex=texidx>=0?(GLuint)bank->gl_texture_ids[texidx]:0;
  if(tex){
   if(!textured){
    glDisableClientState(GL_COLOR_ARRAY);
    glColor4f(1.f,1.f,1.f,1.f);
    glEnable(GL_TEXTURE_2D);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glTexCoordPointer(2,GL_FLOAT,sizeof(B24C1UVPair),&uv->uv[0].u);
   }
   if(last_tex!=(int)tex)glBindTexture(GL_TEXTURE_2D,tex);
   textured=1;last_tex=(int)tex;
  }else{
   if(textured){
    glDisableClientState(GL_TEXTURE_COORD_ARRAY);
    glDisable(GL_TEXTURE_2D);
    glEnableClientState(GL_COLOR_ARRAY);
   }
   textured=0;last_tex=-1;
  }
  /* Exactly the source-authored triangle references, stable original winding,
     same vertex streams as G10. No second scene rendering pass. */
  glDrawElements(GL_TRIANGLES,(GLsizei)q->index_count,GL_UNSIGNED_SHORT,
                 plan->indices+q->first_index);
 }
 glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glDisable(GL_TEXTURE_2D);
 glDisableClientState(GL_COLOR_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);
 glBindTexture(GL_TEXTURE_2D,0);
 return next==m->index_count;
}
