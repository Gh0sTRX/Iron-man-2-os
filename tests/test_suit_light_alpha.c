/* G299 synthetic source fixture of ACTUAL animated PS Vita armor renderer.
 * No original game assets, Vita screenshots or original-light-shader claims.
 */
#include "b24_gpu_suit.h"
#include <vitaGL.h>
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static GLint mode=GL_REPLACE;
static int upload_error;
static unsigned deleted;
GLenum glGetError(void){return upload_error?GL_OUT_OF_MEMORY:GL_NO_ERROR;}
static unsigned uploaded=0u,drawn=0u,reads=0u,writes=0u,alpha_ok=0u;
static unsigned depth_on=0u,texture_on=0u,pushed=0u,vertex_on=0u,uv_on=0u;
static const unsigned char *color_pointer;
static unsigned color_on,expect_color_array=1;
static float draw_rgb[3]={0.f,0.f};
static float col[4]={1.f,1.f,1.f,1.f};
void glGenTextures(GLsizei n,GLuint *id){assert(n==1&&id);*id=17u;}
void glDeleteTextures(GLsizei n,const GLuint *id){assert(n==1&&id&&*id==17u);deleted++;}
void glBindTexture(GLenum t,GLuint id){assert(t==GL_TEXTURE_2D&&(id==17u||id==0u));}
void glTexParameteri(GLenum t,GLenum p,GLint v){
 assert(t==GL_TEXTURE_2D);(void)p;(void)v;
}
void glTexImage2D(GLenum t,GLint level,GLint internal,GLsizei w,GLsizei h,
 GLint border,GLenum format,GLenum type,const void *pixels){
 assert(t==GL_TEXTURE_2D&&level==0&&internal==GL_RGBA);
 assert(w==8&&h==8&&border==0&&format==GL_RGBA&&type==GL_UNSIGNED_BYTE);
 const unsigned char *src=pixels;assert(src&&src[3]==91u&&src[7]==231u);
 alpha_ok++;uploaded++;
}
void glMatrixMode(GLenum p){assert(p==GL_MODELVIEW);}
void glPushMatrix(void){pushed++;}
void glPopMatrix(void){assert(pushed);pushed--;}
void glMultMatrixf(const GLfloat *m){assert(m&&isfinite(m[12]));}
void glEnable(GLenum p){
 assert(p==GL_DEPTH_TEST||p==GL_TEXTURE_2D);
 if(p==GL_DEPTH_TEST)depth_on++;else texture_on++;
}
void glDisable(GLenum p){assert(p==GL_TEXTURE_2D&&texture_on);texture_on--;}
void glColor4f(GLfloat r,GLfloat g,GLfloat b,GLfloat a){
 assert(isfinite(r)&&isfinite(g)&&isfinite(b)&&isfinite(a));
 col[0]=r;col[1]=g;col[2]=b;col[3]=a;
}
void glEnableClientState(GLenum p){
 assert(p==GL_VERTEX_ARRAY||p==GL_TEXTURE_COORD_ARRAY||p==GL_COLOR_ARRAY);
 if(p==GL_VERTEX_ARRAY)vertex_on++;else if(p==GL_TEXTURE_COORD_ARRAY)uv_on++;else color_on++;
}
void glDisableClientState(GLenum p){
 assert(p==GL_VERTEX_ARRAY||p==GL_TEXTURE_COORD_ARRAY||p==GL_COLOR_ARRAY);
 if(p==GL_VERTEX_ARRAY){assert(vertex_on);vertex_on--;}
 else if(p==GL_TEXTURE_COORD_ARRAY){assert(uv_on);uv_on--;}
 else {assert(color_on);color_on--;}
}
void glVertexPointer(GLint n,GLenum type,GLsizei stride,const void *p){
 assert(n==3&&type==GL_FLOAT&&stride==20&&p);
}
void glTexCoordPointer(GLint n,GLenum type,GLsizei stride,const void *p){
 assert(n==2&&type==GL_FLOAT&&stride==20&&p);
}
void glColorPointer(GLint n,GLenum type,GLsizei stride,const void *p){
 assert(n==4&&type==GL_UNSIGNED_BYTE&&stride==0&&p);color_pointer=p;
}
void glGetTexEnviv(GLenum target,GLenum param,GLint *value){
 assert(target==GL_TEXTURE_ENV&&param==GL_TEXTURE_ENV_MODE&&value);
 *value=mode;reads++;
}
void glTexEnvi(GLenum target,GLenum param,GLint value){
 assert(target==GL_TEXTURE_ENV&&param==GL_TEXTURE_ENV_MODE);
 assert(value==GL_REPLACE||value==GL_MODULATE);mode=value;writes++;
}
void glDrawElements(GLenum kind,GLsizei n,GLenum type,const void *tri){
 assert(kind==GL_TRIANGLES&&n==3&&type==GL_UNSIGNED_SHORT&&tri);
 assert(mode==GL_MODULATE&&pushed==1u&&depth_on>=1u&&texture_on==1u);
 assert(vertex_on==1u&&uv_on==1u&&col[3]==1.f);
 assert(fabsf(col[0]-col[1])<1.e-6f&&fabsf(col[1]-col[2])<1.e-6f);
 if(expect_color_array){assert(color_on==1&&color_pointer&&color_pointer[3]==255);}
 else assert(color_on==0);
 assert(drawn<3u);draw_rgb[drawn++]=expect_color_array?(float)color_pointer[0]/255.f:col[0];
}
int main(void){
 B24GpuSuitVertex vertex[3]={
  {0.f,0.f,0.f,0.f,0.f},
  {1.f,0.f,0.f,1.f,0.f},
  {0.f,1.f,0.f,0.f,1.f}};
 B24GpuSuitTriangle tri[1]={{0,1,2}};
 unsigned char original_rgba[8u*8u*4u];
 memset(original_rgba,200,sizeof(original_rgba));
 original_rgba[3]=91u;original_rgba[7]=231u;
 B24GpuSuitSource src={vertex,tri,original_rgba,3u,1u,8u,8u,0.f,0.f};
 B24GpuSuit gpu={0};
 assert(b24_gpu_suit_validate(&src));
 upload_error=1;
 assert(!b24_gpu_suit_prepare(&gpu,&src));
 assert(!gpu.prepared&&gpu.texture_id==0&&deleted==1);
 upload_error=0;uploaded=alpha_ok=0;
 assert(b24_gpu_suit_prepare(&gpu,&src));
 assert(uploaded==1u&&alpha_ok==1u&&original_rgba[3]==91u);
 B24GpuSuitPose near={-23.170f,-21.477f,0.f,0.f,0.f,0.f};
 B24GpuSuitPose far={500.f,500.f,0.f,0.f,0.f,0.f};
 assert(mode==GL_REPLACE);
 assert(b24_gpu_suit_draw(&gpu,&src,&near));
 assert(mode==GL_REPLACE&&pushed==0u&&vertex_on==0u&&uv_on==0u);
 assert(col[0]==1.f&&col[1]==1.f&&col[2]==1.f&&col[3]==1.f);
 assert(b24_gpu_suit_draw(&gpu,&src,&far));
 assert(draw_rgb[0]>draw_rgb[1]&&draw_rgb[0]<=1.f&&draw_rgb[1]>0.f);
 assert(drawn==2u&&reads==2u&&writes==4u&&original_rgba[3]==91u);
 assert(mode==GL_REPLACE&&texture_on==0u&&pushed==0u&&color_on==0);
 /* Optional CPU scratch failure retains the old uniform-light renderer. */
 free(gpu.light_normals);free(gpu.light_rgba);gpu.light_normals=NULL;gpu.light_rgba=NULL;gpu.light_capacity=0;
 expect_color_array=0;assert(b24_gpu_suit_draw(&gpu,&src,&near));
 assert(drawn==3&&mode==GL_REPLACE&&color_on==0);
 b24_gpu_suit_release(&gpu);
 assert(!gpu.light_normals&&!gpu.light_rgba&&!gpu.light_capacity);
 puts("G299 PASS real source animated armor GPU: experimental current-pose geometry RGB with bounded scratch and uniform fallback; atlas alpha untouched; GL_MODULATE while drawing, previous GL_REPLACE and white suit/HUD state restored; NO VPK, no device claim");
 return 0;
}
