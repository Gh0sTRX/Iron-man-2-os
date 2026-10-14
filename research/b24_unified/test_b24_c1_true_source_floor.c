#include "b24_c1_true_source_floor.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
int main(void){
 B24GpuC1Mesh city={0};
 B24GpuC1Vertex v[6]={
   {0,0,2,0},{8,0,2,0},{0,8,2,0}, /* source TEST floor */
   {0,0,8,0},{8,0,8,0},{0,8,8,0}  /* source TEST high plane */
 };
 uint16_t ix[6]={0,1,2,3,4,5};
 city.vertices=v;city.indices=ix;city.original_z_up=1;
 city.vertex_count=6;city.index_count=6;
 city.batches[0]=(B24GpuC1Batch){0,0,6,2,{0,0,2,8,8,8}};
 float height=0.f;
 assert(b24_c1_true_floor_at(&city,2.f,2.f,1.2f,2.f,&height));
 assert(fabsf(height-2.f)<1e-5f);
 assert(b24_c1_true_floor_at(&city,2.f,2.f,7.7f,2.f,&height));
 assert(fabsf(height-8.f)<1e-5f);
 height=101.f;
 assert(!b24_c1_true_floor_at(&city,100.f,2.f,2.f,20.f,&height));
 assert(height==101.f); /* NO plane under missing source */
 assert(!b24_c1_true_floor_at(&city,2.f,2.f,-10.f,1.f,&height));
 assert(!b24_c1_true_floor_at(&city,2.f,2.f,0.f,200.f,&height));
 city.original_z_up=0;
 assert(!b24_c1_true_floor_at(&city,2.f,2.f,2.f,1.f,&height));
 puts("PASS G10 original 2010 C1L1 category-ground indexed triangle floor"
      " barycentric Z query, distinct height layers, missing-floor no synth"
      " and no graph/physics input ownership");
 return 0;
}
