/* G298 HOST-ONLY runtime test of ACTUAL VitaGL G68 scene renderer source.
 * Synthetic G66M/G66T fixture is deliberately NOT an original iOS asset.
 * Checks correct G95 four-Sun *experimental* RGB modulation of opaque
 * source-like vertex streams, preservation of every RGBA alpha byte,
 * GL_MODULATE while drawing and restoration for HUD/armor afterward.
 * Only VitaSDK ELF + physical device can check actual hardware output.
 */
#define _POSIX_C_SOURCE 200809L
#include "b24_gpu_g68_city.h"
#include <vitaGL.h>
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

typedef struct {float xyz[3],uv[2];unsigned char rgba[4];} G298Vertex;
_Static_assert(sizeof(G298Vertex)==24,"G68 original runtime ABI must remain 24 bytes");

static GLuint next_texture=11u, gpu_buffer_id=401u, active_texture=0;
static GLint env_mode=GL_REPLACE;
static unsigned env_read=0, env_write=0, draws=0, uploads=0;
static unsigned alpha_pass_draws=0, color_enable=0, color_disable=0;
static int color_state=0, blend_state=0, depth_write=1, vertex_state=0;
static G298Vertex *gpu_copy;
static size_t gpu_n;

void glGenTextures(GLsizei n,GLuint *v){assert(n==1&&v);*v=next_texture++;}
void glDeleteTextures(GLsizei n,const GLuint *v){assert(n==1&&v&&*v>=11u);}
void glBindTexture(GLenum t,GLuint id){assert(t==GL_TEXTURE_2D);active_texture=id;}
void glTexParameteri(GLenum t,GLenum p,GLint v){assert(t==GL_TEXTURE_2D);(void)p;(void)v;}
void glTexImage2D(GLenum t,GLint l,GLint in,GLsizei w,GLsizei h,
 GLint border,GLenum format,GLenum type,const void *src){
 assert(t==GL_TEXTURE_2D&&l==0&&in==GL_RGBA&&w==8&&h==8&&border==0);
 assert(format==GL_RGBA&&type==GL_UNSIGNED_BYTE&&src);
 uploads++;
}
GLenum glGetError(void){return GL_NO_ERROR;}
void glGenBuffers(GLsizei n,GLuint *v){assert(n==1&&v);*v=gpu_buffer_id;}
void glDeleteBuffers(GLsizei n,const GLuint *v){assert(n==1&&v&&*v==gpu_buffer_id);}
void glBindBuffer(GLenum t,GLuint id){
 assert(t==GL_ARRAY_BUFFER&&(id==0||id==gpu_buffer_id));
}
void glBufferData(GLenum t,GLsizeiptr n,const void *data,GLenum usage){
 assert(t==GL_ARRAY_BUFFER&&usage==GL_STATIC_DRAW&&data);
 assert(n==67323*(GLsizeiptr)sizeof(G298Vertex));
 gpu_n=(size_t)n/sizeof(G298Vertex);gpu_copy=malloc((size_t)n);
 assert(gpu_copy);memcpy(gpu_copy,data,(size_t)n);
}
void glEnable(GLenum t){
 assert(t==GL_DEPTH_TEST||t==GL_BLEND||t==GL_TEXTURE_2D);
 if(t==GL_BLEND)blend_state=1;
}
void glDisable(GLenum t){
 assert(t==GL_BLEND||t==GL_TEXTURE_2D);
 if(t==GL_BLEND)blend_state=0;
}
void glDepthFunc(GLenum t){assert(t==GL_LESS);}
void glDepthMask(GLboolean t){assert(t==0||t==1);depth_write=t;}
void glBlendFunc(GLenum a,GLenum b){
 assert(a==GL_SRC_ALPHA&&b==GL_ONE_MINUS_SRC_ALPHA);
}
void glColor4f(GLfloat a,GLfloat b,GLfloat c,GLfloat d){
 assert(a==1.f&&b==1.f&&c==1.f&&d==1.f);
}
void glEnableClientState(GLenum t){
 assert(t==GL_VERTEX_ARRAY||t==GL_COLOR_ARRAY||t==GL_TEXTURE_COORD_ARRAY);
 if(t==GL_COLOR_ARRAY){color_state=1;color_enable++;}
 if(t==GL_VERTEX_ARRAY)vertex_state=1;
}
void glDisableClientState(GLenum t){
 assert(t==GL_VERTEX_ARRAY||t==GL_COLOR_ARRAY||t==GL_TEXTURE_COORD_ARRAY);
 if(t==GL_COLOR_ARRAY){color_state=0;color_disable++;}
 if(t==GL_VERTEX_ARRAY)vertex_state=0;
}
void glVertexPointer(GLint n,GLenum t,GLsizei stride,const void *p){
 assert(n==3&&t==GL_FLOAT&&stride==24&&(uintptr_t)p==0);
}
void glTexCoordPointer(GLint n,GLenum t,GLsizei stride,const void *p){
 assert(n==2&&t==GL_FLOAT&&stride==24&&(uintptr_t)p==12);
}
void glColorPointer(GLint n,GLenum t,GLsizei stride,const void *p){
 assert(n==4&&t==GL_UNSIGNED_BYTE&&stride==24&&(uintptr_t)p==20);
}
void glGetTexEnviv(GLenum t,GLenum p,GLint *value){
 assert(t==GL_TEXTURE_ENV&&p==GL_TEXTURE_ENV_MODE&&value);
 *value=env_mode;env_read++;
}
void glTexEnvi(GLenum t,GLenum p,GLint value){
 assert(t==GL_TEXTURE_ENV&&p==GL_TEXTURE_ENV_MODE);
 assert(value==GL_MODULATE||value==GL_REPLACE);
 env_mode=value;env_write++;
}
void glDrawArrays(GLenum t,GLint start,GLsizei count){
 assert(t==GL_TRIANGLES&&start>=0&&count>0&&count%3==0);
 assert(env_mode==GL_MODULATE); /* actual G95 vertex RGB reaches texture */
 assert(color_state && vertex_state);
 assert(gpu_n==67323u&&(unsigned)start+(unsigned)count<=gpu_n);
 if(active_texture==12u){ /* texture atlas1 has real alpha in fixture */
  assert(blend_state&&!depth_write);alpha_pass_draws++;
 }
 draws++;
}

static void write_texture(const char *prefix,unsigned idx){
 char path[256];
 assert(snprintf(path,sizeof(path),"%s_tex_%02u.g66t",prefix,idx)>0);
 FILE *f=fopen(path,"wb");assert(f);
 const uint32_t hdr[3]={1,8,8};
 assert(fwrite("G66T",1,4,f)==4);
 assert(fwrite(hdr,sizeof(hdr),1,f)==1);
 unsigned char pixels[8*8*4];
 for(unsigned k=0;k<8u*8u;k++){
  pixels[k*4]=200u;pixels[k*4+1]=150u;pixels[k*4+2]=100u;
  pixels[k*4+3]=(idx==1u&&k==0u)?0u:255u;
 }
 assert(fwrite(pixels,sizeof(pixels),1,f)==1);
 assert(fclose(f)==0);
}
static void write_city(const char *path){
 FILE *f=fopen(path,"wb");assert(f);
 const uint32_t hdr[4]={1u,67323u,32u,31u};
 assert(fwrite("G66M",1,4,f)==4);
 assert(fwrite(hdr,sizeof(hdr),1,f)==1);
 B24G68Batch b[32]={0};
 unsigned running=0;
 for(unsigned i=0;i<32u;i++){
  b[i].first=running;b[i].count=i==0?67230u:3u;
  b[i].tex=i<31u?i:UINT32_MAX;
  running+=b[i].count;
 }
 assert(running==67323u);
 assert(fwrite(b,sizeof(b),1,f)==1);
 const G298Vertex v[3]={
  {{-23.170f,-21.477f,1.f},{0.f,0.f},{200,150,100,173}},
  {{-22.170f,-21.477f,1.f},{1.f,0.f},{200,150,100,173}},
  {{-23.170f,-20.477f,1.f},{0.f,1.f},{200,150,100,173}}
 };
 for(unsigned i=0;i<67323u;i++)assert(fwrite(&v[i%3u],sizeof(G298Vertex),1,f)==1);
 assert(fclose(f)==0);
}
int main(void){
 const char *dir="g298_generated_mock_fixture";
 const char *prefix="g298_generated_mock_fixture/city";
 const char *mesh="g298_generated_mock_fixture/city.g66m";
 assert(mkdir(dir,0700)==0);
 write_city(mesh);
 for(unsigned i=0;i<31u;i++)write_texture(prefix,i);
 B24G68City city={0};
 assert(b24_g68_city_open(&city,mesh,prefix));
 assert(city.ready&&city.vertices==67323u&&city.batch_count==32u);
 assert(city.material_has_alpha[1]==1u);
 assert(city.material_has_alpha[0]==0u&&uploads==31u);
 assert(gpu_n==67323u);
 /* G95 changes opaque vertex RGB, but alpha-bearing texture is exempt. */
 const G298Vertex *opaque=&gpu_copy[0],*translucent=&gpu_copy[67230u];
 assert(opaque->rgba[3]==173u&&translucent->rgba[3]==173u);
 assert(opaque->rgba[0]!=200u||opaque->rgba[1]!=150u||opaque->rgba[2]!=100u);
 assert(translucent->rgba[0]==200u&&translucent->rgba[1]==150u&&translucent->rgba[2]==100u);
 for(unsigned i=0;i<gpu_n;i++)assert(gpu_copy[i].rgba[3]==173u);
 /* Another renderer previously used GL_REPLACE. G298 MUST NOT inherit it
  * for the city, and MUST restore it for the upcoming suit/HUD draw. */
 assert(env_mode==GL_REPLACE);
 assert(b24_g68_city_draw(&city));
 assert(env_read==1u&&env_write==2u&&env_mode==GL_REPLACE);
 assert(draws==32u&&alpha_pass_draws==1u);
 assert(!color_state&&!vertex_state&&!blend_state&&depth_write);
 assert(color_enable==1u&&color_disable==1u);
 b24_g68_city_close(&city);
 free(gpu_copy);
 for(unsigned i=0;i<31u;i++){
  char file[256];
  assert(snprintf(file,sizeof(file),"%s_tex_%02u.g66t",prefix,i)>0);
  assert(unlink(file)==0);
 }
 assert(unlink(mesh)==0&&rmdir(dir)==0);
 puts("G298 PASS true G68 Vita renderer source: G95 authored-light candidate vertex RGB modulates all textured opaque city batches, translucent source atlas untouched, native RGBA alpha preserved, G71 depth blend retained, HUD GL_REPLACE restored. Synthetic assets only. NO VPK, Vita hardware untested.");
 return 0;
}
