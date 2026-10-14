#include "b24_c1_material_batches.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc,char **argv){
 assert(argc==3);
 B24GpuC1Mesh scene={0};
 B24C1MaterialSource mat={0};
 B24C1MaterialBatchPlan plan={0};
 assert(b24_gpu_c1_load(&scene,argv[1]));
 assert(b24_c1_material_source_load(&mat,argv[2]));
 assert(b24_c1_material_batches_build(&plan,&scene,&mat));
 assert(plan.ready&&plan.index_count==68757u);
 assert(plan.nbuckets>4u&&plan.nbuckets<=376u);
 uint32_t original_group[4]={0},sorted_group[4]={0};
 /* Verify a STRICT stable partition, not just matching triangle totals:
    each original triangle is present once with identical original winding. */
 uint32_t positions[4*B24_C1_MAT_NLABEL]={0};
 for(uint32_t i=0;i<plan.nbuckets;i++){
  B24C1MaterialBucket b=plan.buckets[i];
  assert(b.group<4&&b.material_id<94&&b.index_count%3u==0);
  assert(b.first_index+b.index_count<=plan.index_count);
  positions[b.group*94u+b.material_id]=b.first_index;
  sorted_group[b.group]+=b.index_count;
 }
 for(uint32_t k=0;k<370u;k++){
  const B24C1MatMesh *m=&mat.meshes[k];
  for(uint32_t j=0;j<m->triangle_count;j++){
   uint32_t triangle=m->first_triangle+j;
   uint32_t slot=m->group*94u+mat.triangle_material[triangle];
   uint32_t at=positions[slot];positions[slot]+=3u;
   assert(at+3u<=plan.index_count);
   assert(memcmp(plan.indices+at,scene.indices+triangle*3u,
                 3u*sizeof(uint16_t))==0);
   original_group[m->group]+=3u;
  }
 }
 for(int g=0;g<4;g++){
  assert(original_group[g]==scene.batches[g].index_count);
  assert(sorted_group[g]==original_group[g]);
 }
 uint16_t old=mat.triangle_material[0];
 mat.triangle_material[0]=65535u;
 assert(!b24_c1_material_batches_build(&plan,&scene,&mat));
 assert(plan.ready&&plan.index_count==68757u);
 mat.triangle_material[0]=old;
 uint16_t first=scene.indices[0];scene.indices[0]=65535u;
 assert(!b24_c1_material_batches_build(&plan,&scene,&mat));
 scene.indices[0]=first;
 assert(b24_c1_material_batches_build(&plan,&scene,&mat));
 printf("PASS source C1MA->C1G2 GPU draw schedule: %u material buckets, "
        "22919/22919 unchanged original triangles, four groups; "
        "fail-closed corruption and rollback; NO atlas claims/VPK\\n",
        plan.nbuckets);
 b24_c1_material_batches_free(&plan);
 b24_c1_material_source_free(&mat);
 b24_gpu_c1_free(&scene);
 return 0;
}
