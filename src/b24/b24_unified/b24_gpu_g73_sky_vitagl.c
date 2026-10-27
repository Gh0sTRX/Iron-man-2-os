#include "b24_gpu_g73_sky.h"
#include <vitaGL.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float p[3],uv[2];unsigned char color[4];} G73Vertex;
_Static_assert(sizeof(G73Vertex)==24,"Original source world sky packed vertex ABI");
static int exact(FILE *f,void *dst,size_t n){
 return f&&fread(dst,1,n,f)==n;
}
static int load_sky_tex(uint32_t *id,const char *name){
 FILE *f=fopen(name,"rb");if(!f)return 0;
 char magic[4];uint32_t fields[3];
 if(!exact(f,magic,4)||memcmp(magic,"G66T",4)||
    !exact(f,fields,12)||fields[0]!=1||fields[1]!=256||fields[2]!=256){
    fclose(f);return 0;
 }
 size_t bytes=256u*256u*4u;
 unsigned char *pixels=malloc(bytes);
 if(!pixels||!exact(f,pixels,bytes)||fgetc(f)!=EOF){
  free(pixels);fclose(f);return 0;
 }
 fclose(f);
 GLuint tex=0;glGenTextures(1,&tex);
 if(!tex){free(pixels);return 0;}
 glBindTexture(GL_TEXTURE_2D,tex);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
 glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,256,256,0,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
 free(pixels);
 if(glGetError()!=GL_NO_ERROR){glDeleteTextures(1,&tex);return 0;}
 *id=tex;return 1;
}
void b24_g73_sky_close(B24G73Sky *s){
 if(!s)return;
 if(s->vbo){GLuint id=s->vbo;glDeleteBuffers(1,&id);}
 for(int i=0;i<2;i++)if(s->tex[i]){GLuint id=s->tex[i];glDeleteTextures(1,&id);}
 memset(s,0,sizeof(*s));
}
int b24_g73_sky_open(B24G73Sky *s){
 if(!s||s->ready)return 0;
 FILE *f=fopen("app0:assets/G73_original_sky_mesh.g73m","rb");
 if(!f)return 0;
 char magic[4];uint32_t header[4];
 if(!exact(f,magic,4)||memcmp(magic,"G73M",4)||
    !exact(f,header,sizeof(header))||header[0]!=1||
    header[1]!=288||header[2]!=6||header[3]!=2){
   fclose(f);return 0;
 }
 uint32_t cursor=0;
 for(int i=0;i<6;i++){
  uint32_t row[4];
  if(!exact(f,row,sizeof(row))||row[0]!=cursor||row[1]==0||
     row[1]%3!=0||row[1]>288-cursor||row[2]>=2){
   fclose(f);return 0;
  }
  cursor+=row[1];s->first[i]=row[0];s->count[i]=row[1];s->atlas[i]=row[2];
 }
 if(cursor!=288){fclose(f);return 0;}
 G73Vertex geometry[288];
 if(!exact(f,geometry,sizeof(geometry))||fgetc(f)!=EOF){
   fclose(f);return 0;
 }
 fclose(f);
 GLuint vertex=0;glGenBuffers(1,&vertex);
 if(!vertex)return 0;
 s->vbo=vertex;
 glBindBuffer(GL_ARRAY_BUFFER,vertex);
 glBufferData(GL_ARRAY_BUFFER,sizeof(geometry),geometry,GL_STATIC_DRAW);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 if(glGetError()!=GL_NO_ERROR){b24_g73_sky_close(s);return 0;}
 for(int i=0;i<2;i++){
  char path[96];
  snprintf(path,sizeof(path),"app0:assets/G73_original_sky_tex_%02d.g66t",i);
  if(!load_sky_tex(&s->tex[i],path)){b24_g73_sky_close(s);return 0;}
 }
 s->ready=1;return 1;
}
int b24_g73_sky_draw(const B24G73Sky *s){
 if(!s||!s->ready||!s->vbo)return 0;
 /* Genuine spherical source geometry with provisional PVR atlas assignment.
  * This pass writes NO depth; main true city remains opaque in front. */
 glDisable(GL_DEPTH_TEST);glDepthMask(GL_FALSE);
 glDisable(GL_CULL_FACE);glEnable(GL_BLEND);
 glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
 glColor4f(1,1,1,1);
 glBindBuffer(GL_ARRAY_BUFFER,s->vbo);
 glEnableClientState(GL_VERTEX_ARRAY);glEnableClientState(GL_TEXTURE_COORD_ARRAY);
 glEnableClientState(GL_COLOR_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(G73Vertex),(void *)(uintptr_t)0);
 glTexCoordPointer(2,GL_FLOAT,sizeof(G73Vertex),(void *)(uintptr_t)12);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(G73Vertex),(void *)(uintptr_t)20);
 glEnable(GL_TEXTURE_2D);
 for(int i=0;i<6;i++){
  glBindTexture(GL_TEXTURE_2D,s->tex[s->atlas[i]]);
  glDrawArrays(GL_TRIANGLES,(GLint)s->first[i],(GLsizei)s->count[i]);
 }
 glDisableClientState(GL_COLOR_ARRAY);glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);glDisable(GL_TEXTURE_2D);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 glDepthMask(GL_TRUE);glEnable(GL_DEPTH_TEST);
 glDisable(GL_BLEND);
 return glGetError()==GL_NO_ERROR;
}
