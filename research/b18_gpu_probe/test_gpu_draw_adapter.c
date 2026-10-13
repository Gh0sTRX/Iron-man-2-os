#include "gpu_floor_mesh.h"
#include "vitaGL.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
static int calls=0;static unsigned nindices=0;
void glEnable(unsigned v){assert(v==GL_DEPTH_TEST);calls++;}
void glDisable(unsigned v){assert(v==GL_TEXTURE_2D);calls++;}
void glEnableClientState(unsigned v){assert(v==GL_VERTEX_ARRAY||v==GL_COLOR_ARRAY);calls++;}
void glDisableClientState(unsigned v){assert(v==GL_VERTEX_ARRAY||v==GL_COLOR_ARRAY);calls++;}
void glVertexPointer(int n,unsigned type,int stride,const void *ptr){assert(n==3&&type==GL_FLOAT&&stride==(int)sizeof(Im2GpuFloorVertex)&&ptr);calls++;}
void glColorPointer(int n,unsigned type,int stride,const void *ptr){assert(n==3&&type==GL_FLOAT&&stride==(int)sizeof(Im2GpuFloorVertex)&&ptr);calls++;}
void glDrawElements(unsigned what,int n,unsigned type,const void *ptr){assert(what==GL_TRIANGLES&&n==726&&type==GL_UNSIGNED_SHORT&&ptr);nindices+=(unsigned)n;calls++;}
extern int im2_gpu_floor_draw_vitagl(const Im2GpuFloorMesh*);
int main(void){static Im2GpuFloorMesh mesh;
assert(!im2_gpu_floor_draw_vitagl(NULL));
assert(im2_gpu_floor_build(&mesh,0.f,0.f));
assert(im2_gpu_floor_draw_vitagl(&mesh));
assert(nindices==726 && calls==9);
puts("PASS GL adapter with host-mocked API: glDrawElements(726), no per-tile pixel rasterizer");
}
