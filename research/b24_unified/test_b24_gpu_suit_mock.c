#include "b24_gpu_suit.h"
#include <vitaGL.h>
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
static int newtex=0,uploads=0,draws=0,dels=0,verts=0,uvs=0;
static const void *last_vertex=NULL;
void glGenTextures(GLsizei n,GLuint *out){assert(n==1&&out);*out=7;newtex++;}
void glBindTexture(GLenum t,GLuint id){assert(t==GL_TEXTURE_2D&&id==7);}
void glTexParameteri(GLenum target,GLenum id,int value){
 assert(target==GL_TEXTURE_2D);
 assert(id==GL_TEXTURE_MIN_FILTER||id==GL_TEXTURE_MAG_FILTER||
        id==GL_TEXTURE_WRAP_S||id==GL_TEXTURE_WRAP_T);
 assert(value==GL_LINEAR||value==GL_CLAMP_TO_EDGE);
}
void glTexImage2D(GLenum target,int level,int fmt,GLsizei w,GLsizei h,
 int border,GLenum src,GLenum type,const void *pixels){
 assert(target==GL_TEXTURE_2D&&level==0&&fmt==GL_RGBA);
 assert(w==2&&h==2&&border==0&&src==GL_RGBA&&type==GL_UNSIGNED_BYTE&&pixels);uploads++;
}
void glDeleteTextures(GLsizei n,const GLuint *p){assert(n==1&&p&&*p==7);dels++;}
void glMatrixMode(GLenum mode){assert(mode==GL_MODELVIEW);}
void glPushMatrix(void){}
void glPopMatrix(void){}
void glMultMatrixf(const float *m){assert(m&&isfinite(m[12])&&isfinite(m[14]));}
void glEnable(GLenum id){assert(id==GL_TEXTURE_2D||id==GL_DEPTH_TEST);}
void glDisable(GLenum id){assert(id==GL_TEXTURE_2D);}
void glColor4f(float a,float b,float c,float d){assert(a==1&&b==1&&c==1&&d==1);}
void glEnableClientState(GLenum id){assert(id==GL_VERTEX_ARRAY||id==GL_TEXTURE_COORD_ARRAY);}
void glDisableClientState(GLenum id){assert(id==GL_VERTEX_ARRAY||id==GL_TEXTURE_COORD_ARRAY);}
void glVertexPointer(int n,GLenum type,GLsizei stride,const void *p){
 assert(n==3&&type==GL_FLOAT&&stride==sizeof(B24GpuSuitVertex)&&p);
 last_vertex=p;verts++;
}
void glTexCoordPointer(int n,GLenum type,GLsizei stride,const void *p){
 assert(n==2&&type==GL_FLOAT&&stride==sizeof(B24GpuSuitVertex)&&p);uvs++;
}
void glDrawElements(GLenum mode,GLsizei count,GLenum type,const void *p){
 assert(mode==GL_TRIANGLES&&count==6&&type==GL_UNSIGNED_SHORT&&p);draws++;
}
int main(void){
 B24GpuSuitVertex v[4]={{0,0,0,0,0},{1,0,0,1,0},
                         {1,1,0,1,1},{0,1,0,0,1}};
 B24GpuSuitTriangle t[2]={{0,1,2},{0,2,3}};
 unsigned char rgba[16]={255,0,0,255,0,255,0,255,
                          0,0,255,255,255,255,255,255};
 B24GpuSuitSource src={v,t,rgba,4,2,2,2,.5f};
 B24GpuSuit cache={0};
 assert(b24_gpu_suit_validate(&src));
 assert(b24_gpu_suit_prepare(&cache,&src));
 assert(newtex==1&&uploads==1);
 assert(!b24_gpu_suit_prepare(&cache,&src));
 B24GpuSuitPose pose={5,6,2,0,0,0};
 float mat[16];
 assert(b24_gpu_suit_matrix(mat,&pose,.5f));
 assert(fabsf(mat[0]+1.f)<.001f&&fabsf(mat[5]+1.f)<.001f);
 assert(fabsf(mat[12]-5.f)<.001f&&fabsf(mat[14]-1.5f)<.001f);

 /* B17 yaw remains original; cruise/rush applies actual GPU root Rx/Ry.
    Local model forward is -Y; negative pitch raises the nose in Z-up. */
 pose.pitch=-.3f;pose.roll=.2f;
 assert(b24_gpu_suit_matrix(mat,&pose,.5f));
 assert(fabsf(mat[6]-sinf(-.3f))<.001f);
 assert(fabsf(mat[2]+cosf(-.3f)*sinf(.2f))<.001f);
 assert(fabsf(mat[12]-5.f)<.001f&&fabsf(mat[14]-1.5f)<.001f);
 assert(b24_gpu_suit_draw(&cache,&src,&pose));
 v[1].z=2.f; /* live B14 original animation output in RAM */
 assert(b24_gpu_suit_draw(&cache,&src,&pose));
 assert(uploads==1&&draws==2&&verts==2&&uvs==2);
 assert(last_vertex==&v[0].x);
 t[0].i2=99;
 assert(!b24_gpu_suit_validate(&src));
 t[0].i2=2;
 assert(b24_gpu_suit_validate(&src));
 b24_gpu_suit_release(&cache);
 assert(dels==1&&!b24_gpu_suit_draw(&cache,&src,&pose));
 puts("PASS GPU SUIT B24: original IM2T RGBA+UV, live IM2V vertex stream, B17 world transform, texture only once");
}
