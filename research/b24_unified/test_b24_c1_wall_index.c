#include "b24_c1_wall_index.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv){
 B24GpuC1Mesh mesh={0};B24C1WallIndex wall={0};
 if(argc==2){
  assert(b24_gpu_c1_load(&mesh,argv[1]));
  assert(b24_c1_wall_index_build(&wall,&mesh));
  assert(wall.scanned_faces==22919u);
  assert(wall.wall_count>0u&&wall.wall_count<=22919u);
  assert(wall.ref_count>=wall.wall_count&&wall.ref_count<=B24_C1_WALL_MAX_REFS);
  printf("AUTHENTIC C1L1 collision broadphase: %u real steep triangles, %u sparse refs from 22919 true faces\n",
        wall.wall_count,wall.ref_count);
  b24_c1_wall_index_free(&wall);b24_gpu_c1_free(&mesh);
 }
 mesh.vertices=calloc(B24_GPU_C1_VERTS,sizeof(*mesh.vertices));
 mesh.indices=calloc(B24_GPU_C1_INDICES,sizeof(*mesh.indices));
 assert(mesh.vertices&&mesh.indices);
 mesh.vertex_count=B24_GPU_C1_VERTS;mesh.index_count=B24_GPU_C1_INDICES;
 mesh.original_z_up=1;
 const uint32_t counts[4]={3,6,3,B24_GPU_C1_INDICES-12u};
 unsigned start=0;
 for(unsigned i=0;i<4;i++){
  mesh.batches[i].kind=i;mesh.batches[i].source_meshes=1;
  mesh.batches[i].first_index=start;mesh.batches[i].index_count=counts[i];
  start+=counts[i];
 }
 /* Two actual vertical wall facets in STRUCTURES source category.
    Pure side test; never fabricate a collision in the user game. */
 mesh.vertices[1]=(B24GpuC1Vertex){0.f,-2.f,0.f,0};
 mesh.vertices[2]=(B24GpuC1Vertex){0.f, 2.f,0.f,0};
 mesh.vertices[3]=(B24GpuC1Vertex){0.f,-2.f,3.f,0};
 mesh.vertices[4]=(B24GpuC1Vertex){0.f, 2.f,3.f,0};
 mesh.indices[3]=1;mesh.indices[4]=2;mesh.indices[5]=3;
 mesh.indices[6]=2;mesh.indices[7]=4;mesh.indices[8]=3;
 assert(b24_c1_wall_index_build(&wall,&mesh));
 assert(wall.wall_count==2&&wall.scanned_faces==22919u);
 uint32_t matches[16]={0};size_t n=0;
 assert(b24_c1_wall_index_query(&wall,.25f,0.f,1.4f,.45f,matches,16,&n));
 assert(n==2u);
 assert(b24_c1_wall_index_query(&wall,100.f,0.f,1.4f,.45f,matches,16,&n));
 assert(n==0u);
 assert(b24_c1_wall_index_query(&wall,.25f,0.f,5.f,.45f,matches,16,&n));
 assert(n==0u);
 assert(!b24_c1_wall_index_query(&wall,.25f,0.f,1.4f,2.4f,matches,16,&n));
 assert(!b24_c1_wall_index_query(&wall,.25f,0.f,1.4f,.45f,matches,1,&n));
 mesh.indices[3]=65535u;
 assert(!b24_c1_wall_index_build(&wall,&mesh));
 assert(wall.wall_count==2u); /* transactional failure preserves old index */
 puts("PASS C1G2 source wall index: original Z-up, category/slope filters, sparse local queries, strict capacity, transaction rollback");
 b24_c1_wall_index_free(&wall);b24_gpu_c1_free(&mesh);
 return 0;
}
