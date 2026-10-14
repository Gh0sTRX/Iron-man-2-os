#include "b24_g10_original_foot_contact.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
int main(void){
 B24GpuC1Vertex v[]={
  {0,0,-.2473f,0},{8,0,-.2473f,0},{0,8,-.2473f,0}
 };
 uint16_t ids[]={0,1,2};
 B24GpuC1Mesh scene={0};
 scene.vertices=v;scene.indices=ids;scene.vertex_count=3;scene.index_count=3;
 scene.original_z_up=1;
 scene.batches[0]=(B24GpuC1Batch){0,0,3,1,{0,0,-.25f,8,8,-.24f}};
 IM2Vertex verts[3]={{0}};
 verts[0].z=0.f;verts[1].z=.6f;verts[2].z=1.3f;
 IM2Model armor={0};
 armor.vertices=verts;armor.nv=3;armor.center_z=.75f;
 IM2Camera cam={0};cam.third_person=1;cam.player_x=2;cam.player_y=2;cam.player_z=0;
 float offset=100.f;
 assert(b24_g10_foot_visual_source_offset(&scene,&armor,&cam,&offset));
 /* Ground actual -.2473, lowest posed vertex 0, center .75, initial
    world sole is -.75 => raise actor .5277; no invented city floor. */
 assert(fabsf(offset-.5277f)<1.e-4f);
 cam.player_x=100;offset=888.f;
 assert(!b24_g10_foot_visual_source_offset(&scene,&armor,&cam,&offset));
 assert(offset==888.f);
 cam.player_x=2;cam.flying=1;
 assert(!b24_g10_foot_visual_source_offset(&scene,&armor,&cam,&offset));
 assert(offset==888.f);
 puts("PASS G10 true B11 C1L1 road original Z support and G9 avatar foot"
      " surface alignment, no fake flat ground, flight exempt, renderer only");
 return 0;
}
