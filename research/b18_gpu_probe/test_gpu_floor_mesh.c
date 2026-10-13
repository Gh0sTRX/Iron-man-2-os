#include "gpu_floor_mesh.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static void check(const Im2GpuFloorMesh *m,float x,float y){
 assert(m->vertex_count==484 && m->index_count==726);
 for(unsigned i=0;i<m->index_count;i++)assert(m->indices[i]<m->vertex_count);
 for(unsigned i=0;i<m->vertex_count;i++){
   const Im2GpuFloorVertex *v=&m->vertices[i];
   assert(isfinite(v->x)&&isfinite(v->y)&&v->z==-1.f);
   assert(v->r>=0&&v->r<=1&&v->g>=0&&v->g<=1&&v->b>=0&&v->b<=1);
   assert(v->u>=0&&v->u<=1&&v->v>=0&&v->v<=1);
 }
 assert(m->tile_x==(int)floorf(x/2.f)*2 && m->tile_y==(int)floorf(y/2.f)*2);
}
int main(void){
 Im2GpuFloorMesh mesh;
 assert(im2_gpu_floor_build(&mesh,0,0));check(&mesh,0,0);
 assert(mesh.vertices[0].x==-10.f&&mesh.vertices[0].y==-10.f);
 assert(mesh.vertices[0].z==-1.f);
 const Im2GpuFloorVertex *center=&mesh.vertices[60u*4u];
 assert(center->r==73.f/255.f&&center->g==117.f/255.f&&center->b==91.f/255.f);
 assert(im2_gpu_floor_build(&mesh,2.1f,-.4f));check(&mesh,2.1f,-.4f);
 assert(mesh.tile_x==2&&mesh.tile_y==-2);
 assert(!im2_gpu_floor_build(NULL,0,0));
 assert(!im2_gpu_floor_build(&mesh,NAN,0));
 assert(!im2_gpu_floor_build(&mesh,INFINITY,0));
 assert(!im2_gpu_floor_build(&mesh,10000000.f,0));
 uint32_t rng=0x20261013u;
 for(int i=0;i<20000;i++){
   rng=rng*1664525u+1013904223u;
   float x=(float)((int)(rng%20000u)-10000)/10.f;
   rng=rng*1664525u+1013904223u;
   float y=(float)((int)(rng%20000u)-10000)/10.f;
   assert(im2_gpu_floor_build(&mesh,x,y));check(&mesh,x,y);
 }
 puts("PASS B18 GPU candidate: 484 vertices, 726 indices, 242 triangles, Z=-1, 20000 guard inputs");
 return 0;
}
