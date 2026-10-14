#include "b24_c1_material_batches.h"
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

void b24_c1_material_batches_free(B24C1MaterialBatchPlan *p){
 if(!p)return;
 free(p->indices);
 memset(p,0,sizeof(*p));
}
int b24_c1_material_batches_build(B24C1MaterialBatchPlan *dst,
                                  const B24GpuC1Mesh *scene,
                                  const B24C1MaterialSource *src){
 if(!dst||!scene||!src||!src->loaded||!src->triangle_material||
    !scene->indices||!scene->vertices||!scene->original_z_up||
    scene->index_count!=B24_GPU_C1_INDICES||
    scene->vertex_count!=B24_C1_MAT_NVERT||
    src->nmaterials!=B24_C1_MAT_NLABEL)return 0;
 /* C1MA is original submesh-ordered: group, vertex and triangle boundaries
    must agree with all four C1G2 group draws before any reordering. */
 uint32_t counts[B24_C1_MAX_MATERIAL_BUCKETS]={0};
 uint32_t cursors[B24_C1_MAX_MATERIAL_BUCKETS]={0};
 uint32_t group_tri[4]={0},group_vert[4]={0};
 uint32_t next_vert=0,next_tri=0;
 for(uint32_t g=0;g<4;g++){
  const B24GpuC1Batch *batch=&scene->batches[g];
  if(batch->kind!=g||batch->first_index!=next_tri*3u||
     batch->index_count%3u||batch->source_meshes==0)return 0;
  group_tri[g]=batch->index_count/3u;
 }
 for(uint32_t k=0;k<B24_C1_MAT_NMESH;k++){
  const B24C1MatMesh *m=&src->meshes[k];
  if(m->group>=4||!m->triangle_count||!m->vertex_count||
     m->first_vertex!=next_vert||m->first_triangle!=next_tri||
     m->vertex_count>B24_C1_MAT_NVERT-next_vert||
     m->triangle_count>B24_C1_MAT_NTRI-next_tri)return 0;
  group_vert[m->group]+=m->vertex_count;
  for(uint32_t t=0;t<m->triangle_count;t++){
   uint32_t ti=next_tri+t;
   uint16_t mat=src->triangle_material[ti];
   if(mat>=src->nmaterials)return 0;
   const uint16_t *idx=scene->indices+3u*ti;
   for(int j=0;j<3;j++){
    if(idx[j]<next_vert||idx[j]>=next_vert+m->vertex_count)return 0;
   }
   counts[m->group*B24_C1_MAT_NLABEL+mat]++;
  }
  next_vert+=m->vertex_count;
  next_tri+=m->triangle_count;
 }
 if(next_vert!=B24_C1_MAT_NVERT||next_tri!=B24_C1_MAT_NTRI)return 0;
 /* Category membership is proven from mesh records, not inferred from
    material names or nearby source strings. */
 uint32_t sum=0;
 for(uint32_t g=0;g<4;g++){
  uint32_t n=0;
  for(uint32_t mat=0;mat<B24_C1_MAT_NLABEL;mat++)
   n+=counts[g*B24_C1_MAT_NLABEL+mat];
  if(n!=group_tri[g])return 0;
  sum+=n;
 }
 if(sum!=B24_C1_MAT_NTRI)return 0;
 B24C1MaterialBatchPlan tmp={0};
 tmp.indices=malloc(sizeof(uint16_t)*B24_GPU_C1_INDICES);
 if(!tmp.indices)return 0;
 for(uint32_t g=0;g<4;g++){
  for(uint32_t mat=0;mat<B24_C1_MAT_NLABEL;mat++){
   uint32_t slot=g*B24_C1_MAT_NLABEL+mat;
   uint32_t n=counts[slot];
   if(!n)continue;
   if(tmp.nbuckets>=B24_C1_MAX_MATERIAL_BUCKETS||
      n>(B24_GPU_C1_INDICES-tmp.index_count)/3u){
    b24_c1_material_batches_free(&tmp);return 0;
   }
   tmp.buckets[tmp.nbuckets++]=(B24C1MaterialBucket){
     g,mat,tmp.index_count,n*3u
   };
   cursors[slot]=tmp.index_count;
   tmp.index_count+=n*3u;
  }
 }
 if(tmp.index_count!=B24_GPU_C1_INDICES){
  b24_c1_material_batches_free(&tmp);return 0;
 }
 /* Stable material partition: within each original (category, material)
    bucket triangles are copied in their source order, never rewound. */
 for(uint32_t t=0;t<B24_C1_MAT_NTRI;t++){
  uint32_t g=0;
  while(g<4&&t>=scene->batches[g].first_index/3u+
                        scene->batches[g].index_count/3u)g++;
  if(g>=4){b24_c1_material_batches_free(&tmp);return 0;}
  uint32_t slot=g*B24_C1_MAT_NLABEL+src->triangle_material[t];
  uint32_t to=cursors[slot];
  if(to+3u>tmp.index_count){
   b24_c1_material_batches_free(&tmp);return 0;
  }
  memcpy(tmp.indices+to,scene->indices+t*3u,3u*sizeof(uint16_t));
  cursors[slot]+=3u;
 }
 for(uint32_t i=0;i<tmp.nbuckets;i++){
  const B24C1MaterialBucket *b=&tmp.buckets[i];
  uint32_t slot=b->group*B24_C1_MAT_NLABEL+b->material_id;
  if(cursors[slot]!=b->first_index+b->index_count){
   b24_c1_material_batches_free(&tmp);return 0;
  }
 }
 tmp.ready=1;
 b24_c1_material_batches_free(dst);
 *dst=tmp;
 (void)group_vert;
 return 1;
}
