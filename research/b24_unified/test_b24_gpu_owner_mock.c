#include "b24_gpu_owner.h"
#include <vitaGL.h>
#include <assert.h>
#include <stdint.h>
#include <math.h>
#include <stdio.h>
static unsigned ctx=0,swap=0,clears=0,draws=0,indices=0,matrices=0;
static int simulate_fail=0;
unsigned b24_mock_draws=0,b24_mock_indices=0,b24_mock_vertex_calls=0,b24_mock_color_calls=0;
/* Upstream vitaGL returns GL_FALSE on NORMAL native 960x544 init. */
GLboolean vglInit(int bytes){assert(bytes==0x1000000);ctx++;return GL_FALSE;}
void vglSwapBuffers(GLboolean common){assert(common==GL_FALSE);swap++;}
void glViewport(int x,int y,GLsizei w,GLsizei h){
 assert(x==0&&y==0&&w==960&&h==544);
}
void glDepthFunc(GLenum x){assert(x==GL_LESS);}
void glEnable(GLenum x){assert(x==GL_DEPTH_TEST);}
void glDisable(GLenum x){assert(x==GL_TEXTURE_2D);}
void glClearColor(float r,float g,float b,float a){
 assert(r>=0&&g>=0&&b>=0&&a==1.f);
}
void glClear(GLbitfield x){assert(x==(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT));clears++;}
void glMatrixMode(GLenum x){assert(x==GL_PROJECTION||x==GL_MODELVIEW);}
void glLoadMatrixf(const float *m){assert(m);for(int i=0;i<16;i++)assert(isfinite(m[i]));matrices++;}
void glEnableClientState(GLenum x){assert(x==GL_VERTEX_ARRAY||x==GL_COLOR_ARRAY);}
void glDisableClientState(GLenum x){assert(x==GL_VERTEX_ARRAY||x==GL_COLOR_ARRAY);}
void glVertexPointer(int n,GLenum type,GLsizei stride,const void *ptr){
 assert(n==3&&type==GL_FLOAT&&stride==sizeof(B24GpuC1Vertex)&&ptr);
 b24_mock_vertex_calls++;
}
void glColorPointer(int n,GLenum type,GLsizei stride,const void *ptr){
 assert(n==4&&type==GL_UNSIGNED_BYTE&&stride==sizeof(B24GpuC1Vertex)&&ptr);
 b24_mock_color_calls++;
}
void glDrawElements(GLenum type,GLsizei n,GLenum indices_type,const void *ptr){
 assert(type==GL_TRIANGLES&&indices_type==GL_UNSIGNED_SHORT&&n%3==0&&ptr);
 draws++;indices+=(unsigned)n;
}
static int fake_armor(void *user){assert(user);return !simulate_fail;}
static int fake_hud(void *user){assert(user);return !simulate_fail;}
int main(int argc,char **argv){
 assert(argc==2);
 B24GpuC1Mesh scene={0};assert(b24_gpu_c1_load(&scene,argv[1]));
 B24GpuCamera c={{0,-12,6},{0,2,2},{0,0,1},
        72.f,960.f/544.f,.2f,5000.f};
 B24GpuCameraMatrices camera={0};
 assert(b24_gpu_camera_matrices(&c,&camera));
 B24GpuOwner owner={0},bad={0};
 assert(!b24_gpu_owner_init(&bad,1));assert(ctx==0);
 assert(b24_gpu_owner_init(&owner,0));assert(ctx==1);
 assert(!b24_gpu_owner_init(&owner,0));
 assert(!b24_gpu_owner_present(&owner));
 assert(b24_gpu_owner_begin(&owner,&camera));
 assert(!b24_gpu_owner_begin(&owner,&camera));
 assert(!b24_gpu_owner_present(&owner));
 assert(!b24_gpu_owner_hud(&owner,fake_hud,&owner));
 assert(b24_gpu_owner_scene(&owner,&scene));assert(draws==4);
 assert(!b24_gpu_owner_scene(&owner,&scene));
 assert(!b24_gpu_owner_present(&owner));
 simulate_fail=1;
 assert(!b24_gpu_owner_armor(&owner,fake_armor,&owner));
 assert(!b24_gpu_owner_present(&owner));
 simulate_fail=0;
 assert(b24_gpu_owner_armor(&owner,fake_armor,&owner));
 assert(!b24_gpu_owner_hud(&owner,NULL,&owner));
 assert(b24_gpu_owner_hud(&owner,fake_hud,&owner));
 assert(b24_gpu_owner_present(&owner));
 assert(!b24_gpu_owner_present(&owner));
 assert(owner.frames_presented==1&&swap==1&&clears==1&&matrices==2);
 assert(indices==68757u);
 assert(b24_gpu_owner_begin(&owner,&camera));
 assert(b24_gpu_owner_scene(&owner,&scene));
 assert(b24_gpu_owner_armor(&owner,fake_armor,&owner));
 assert(b24_gpu_owner_hud(&owner,fake_hud,&owner));
 assert(b24_gpu_owner_present(&owner));
 assert(ctx==1&&swap==2&&draws==8);
 b24_gpu_c1_free(&scene);
 puts("PASS B24 single-GPU owner: SDL coexistence rejected, z-up matrices, real 4-batch scene, required armor+HUD, one swap/frame");
}
