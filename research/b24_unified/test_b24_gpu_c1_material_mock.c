#include "b24_gpu_c1_material.h"
#include <vitaGL.h>
#include <assert.h>
#include <stdio.h>
static unsigned draws=0,indices_total=0,tex_binds=0,texture_enables=0,
                uvptr=0,color_disables=0,color_enables=0;
void glEnable(GLenum p){assert(p==GL_DEPTH_TEST||p==GL_TEXTURE_2D);if(p==GL_TEXTURE_2D)texture_enables++;}
void glDisable(GLenum p){assert(p==GL_TEXTURE_2D);}
void glEnableClientState(GLenum p){
 assert(p==GL_VERTEX_ARRAY||p==GL_COLOR_ARRAY||p==GL_TEXTURE_COORD_ARRAY);
 if(p==GL_COLOR_ARRAY)color_enables++;
}
void glDisableClientState(GLenum p){
 assert(p==GL_VERTEX_ARRAY||p==GL_COLOR_ARRAY||p==GL_TEXTURE_COORD_ARRAY);
 if(p==GL_COLOR_ARRAY)color_disables++;
}
void glVertexPointer(int n,GLenum t,GLsizei stride,const void *p){
 assert(n==3&&t==GL_FLOAT&&stride==16&&p);
}
void glColorPointer(int n,GLenum t,GLsizei stride,const void *p){
 assert(n==4&&t==GL_UNSIGNED_BYTE&&stride==16&&p);
}
void glTexCoordPointer(int n,GLenum t,GLsizei stride,const void *p){
 assert(n==2&&t==GL_FLOAT&&stride==8&&p);uvptr++;
}
void glBindTexture(GLenum target,GLuint id){
 assert(target==GL_TEXTURE_2D&&id==1234u);tex_binds++;
}
void glColor4f(float a,float b,float c,float d){
 assert(a==1.f&&b==1.f&&c==1.f&&d==1.f);
}
void glDrawElements(GLenum type,GLsizei n,GLenum index,const void *p){
 assert(type==GL_TRIANGLES&&index==GL_UNSIGNED_SHORT&&n>0&&n%3==0&&p);
 draws++;indices_total+=(unsigned)n;
}
int main(int argc,char **argv){
 assert(argc==3);
 B24GpuC1Mesh mesh={0};B24C1UV uv={0};
 assert(b24_gpu_c1_load(&mesh,argv[1]));
 assert(b24_c1_uv_load(&uv,argv[2]));
 assert(!b24_gpu_c1_draw_material(NULL,&uv,1234u));
 assert(!b24_gpu_c1_draw_material(&mesh,NULL,1234u));
 assert(b24_gpu_c1_draw_material(&mesh,NULL,0u));
 assert(draws==4&&indices_total==68757u);
 assert(uvptr==0&&texture_enables==0&&tex_binds==0);
 assert(b24_gpu_c1_draw_material(&mesh,&uv,1234u));
 assert(draws==8&&indices_total==137514u);
 assert(uvptr==1&&texture_enables==1&&tex_binds==1);
 assert(color_disables>=1&&color_enables>=1);
 b24_c1_uv_free(&uv);b24_gpu_c1_free(&mesh);
 puts("PASS B24 original city GPU: 4 batched draws/scene, 22 vehicles UV textured ONLY with verified atlas, other 348 source models untouched, zero invented textures");
}
