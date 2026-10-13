#include "b24_gpu_suit_im2_adapter.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 IM2Vertex v[4]={{0,0,0,0,0},{1,0,0,1,0},{1,1,0,1,1},{0,1,0,0,1}};
 IM2Triangle tri[2]={{0,1,2},{0,2,3}};
 unsigned char atlas[16]={255,0,0,255,0,255,0,255,0,0,255,255,255,255,255,255};
 IM2Model m={0};
 m.vertices=v;m.triangles=tri;m.texture=atlas;
 m.nv=4;m.nt=2;m.tw=2;m.th=2;m.center_z=.5f;
 B24GpuIM2Stream s={0};
 assert(b24_gpu_im2_stream_init(&s,&m));
 assert(s.source.nv==4&&s.source.nt==2&&s.source.texture_rgba==atlas);
 assert(s.source.vertices[1].u==1.f);
 assert(s.source.vertices[0].z==0.f);
 assert(!b24_gpu_im2_stream_init(&s,&m)); /* don't silently leak on suit reload */
 /* Both input copies and frame reuse: B14/B16 can mutate original model. */
 v[0].z=1.5f;
 assert(b24_gpu_im2_stream_update(&s,&m));
 assert(fabsf(s.source.vertices[0].z-1.5f)<.0001f);
 assert(s.source.vertices[1].u==1.f);
 assert(s.source.triangles[0].i1==1);
 m.nv=99;
 assert(!b24_gpu_im2_stream_update(&s,&m));
 m.nv=4;
 m.center_z=1.75f;
 assert(b24_gpu_im2_stream_update(&s,&m));
 assert(s.source.center_z==1.75f);
 unsigned char other[16]={0};m.texture=other;
 assert(!b24_gpu_im2_stream_update(&s,&m)); /* requires release/rebind on suit change */
 b24_gpu_im2_stream_free(&s);
 assert(!s.dynamic_vertices&&!s.static_triangles);
 assert(!b24_gpu_im2_stream_update(&s,&m));
 puts("PASS B24 actual IM2Model live animation -> textured GPU suit, UV/indices, 1 persistent staging buffer, guarded suit switch");
}
