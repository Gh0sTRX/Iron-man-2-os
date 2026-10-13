#include "b24_c1_gpu_mesh.h"
#include <vitaGL.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>
unsigned b24_mock_draws=0,b24_mock_indices=0,b24_mock_vertex_calls=0,b24_mock_color_calls=0;
static unsigned flag=0,enabled=0,disabled=0;
void glEnable(GLenum id){assert(id==GL_DEPTH_TEST);flag++; }
void glDisable(GLenum id){assert(id==GL_TEXTURE_2D);flag++;}
void glEnableClientState(GLenum id){assert(id==GL_VERTEX_ARRAY||id==GL_COLOR_ARRAY);enabled++;}
void glDisableClientState(GLenum id){assert(id==GL_VERTEX_ARRAY||id==GL_COLOR_ARRAY);disabled++;}
void glVertexPointer(int n,GLenum t,GLsizei stride,const void *p){
    assert(n==3&&t==GL_FLOAT&&stride==sizeof(B24GpuC1Vertex)&&p);b24_mock_vertex_calls++;
}
void glColorPointer(int n,GLenum t,GLsizei stride,const void *p){
    assert(n==4&&t==GL_UNSIGNED_BYTE&&stride==sizeof(B24GpuC1Vertex)&&p);b24_mock_color_calls++;
}
void glDrawElements(GLenum mode,GLsizei n,GLenum it,const void *indices){
    assert(mode==GL_TRIANGLES && it==GL_UNSIGNED_SHORT && indices && n%3==0);
    b24_mock_draws++;b24_mock_indices+=(unsigned)n;
}
int main(int argc,char **argv){
    assert(argc==2);
    B24GpuC1Mesh s={0};
    assert(!b24_gpu_c1_load(&s,"/tmp/there-is-no-b24-c1g2.mesh"));
    assert(b24_gpu_c1_load(&s,argv[1]));
    assert(s.vertex_count==B24_GPU_C1_VERTS);
    assert(s.index_count==B24_GPU_C1_INDICES);
    assert(s.original_z_up==1);
    assert(!b24_gpu_c1_draw_vitagl(NULL));
    assert(b24_gpu_c1_draw_vitagl(&s));
    assert(b24_mock_draws==4&&b24_mock_indices==68757);
    assert(flag==2&&enabled==2&&disabled==2);
    assert(b24_mock_vertex_calls==1&&b24_mock_color_calls==1);
    const size_t old=s.vertex_count;
    assert(!b24_gpu_c1_load(&s,"/tmp/there-is-no-b24-c1g2.mesh"));
    assert(s.vertex_count==old); /* failed load preserves valid scene */
    b24_gpu_c1_free(&s);
    assert(!b24_gpu_c1_draw_vitagl(&s));
    puts("PASS B24 source-only 4-batch GPU submission: 37946 original vertices, 68757 indices, 22919 triangles");
    return 0;
}
