#include "b24_gpu_g68_city.h"
#include <vitaGL.h>
#include <math.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Original G68 VPK G66M/G66T GPU ABI, not original private .bdae serialized
 * format. Exactly the SAME already hardware-tested first level batches.
 * Keep source world coordinates and UVs intact; no map recenter or re-bake. */
typedef struct {float xyz[3],uv[2];unsigned char rgba[4];} G68Vtx;
_Static_assert(sizeof(G68Vtx)==24,"G68 genuine map vertex layout changed");
_Static_assert(sizeof(B24G68Batch)==16,"G68 16-byte material batch changed");
static int exact(FILE *f,void *dst,size_t n) {
 return f && fread(dst,1,n,f)==n;
}
static int texture_load(uint32_t *tex,const char *filename){
 FILE *f=fopen(filename,"rb");
 if(!f)return 0;
 unsigned char magic[4];uint32_t data[3];
 if(!exact(f,magic,4)||memcmp(magic,"G66T",4)||
    !exact(f,data,12)||data[0]!=1u||
    data[1]<8||data[2]<8||data[1]>1024||data[2]>1024){
   fclose(f);return 0;
 }
 const size_t bytes=(size_t)data[1]*data[2]*4u;
 unsigned char *rgba=malloc(bytes);
 if(!rgba||!exact(f,rgba,bytes)||fgetc(f)!=EOF){
   free(rgba);fclose(f);return 0;
 }
 fclose(f);
 GLuint id=0;glGenTextures(1,&id);
 if(!id){free(rgba);return 0;}
 glBindTexture(GL_TEXTURE_2D,id);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT);
 glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,(GLsizei)data[1],
              (GLsizei)data[2],0,GL_RGBA,GL_UNSIGNED_BYTE,rgba);
 free(rgba);
 if(glGetError()!=GL_NO_ERROR){glDeleteTextures(1,&id);return 0;}
 *tex=(uint32_t)id;return 1;
}
void b24_g68_city_close(B24G68City *m){
 if(!m)return;
 if(m->vbo){GLuint id=(GLuint)m->vbo;glDeleteBuffers(1,&id);}
 for(unsigned i=0;i<m->texture_count&&i<B24_G68_TEX_MAX;i++)
   if(m->texture_ids[i]){GLuint id=(GLuint)m->texture_ids[i];glDeleteTextures(1,&id);}
 memset(m,0,sizeof(*m));
}
int b24_g68_city_open(B24G68City *m,
                     const char *mesh_path,const char *texture_prefix){
 if(!m||m->ready||!mesh_path||!texture_prefix)return 0;
 FILE *f=fopen(mesh_path,"rb");if(!f)return 0;
 unsigned char magic[4];uint32_t hdr[4];
 int ok=exact(f,magic,4)&&memcmp(magic,"G66M",4)==0&&exact(f,hdr,16)
   &&hdr[0]==1u&&hdr[1]==67323u&&hdr[2]==32u&&hdr[3]==31u;
 if(!ok){fclose(f);return 0;}
 m->vertices=hdr[1];m->batch_count=hdr[2];m->texture_count=hdr[3];
 if(!exact(f,m->batches,sizeof(B24G68Batch)*m->batch_count)){
   fclose(f);memset(m,0,sizeof(*m));return 0;
 }
 uint32_t running=0;
 for(unsigned i=0;i<m->batch_count;i++){
   const B24G68Batch *b=&m->batches[i];
   if(b->first!=running||b->count==0||b->count%3!=0||
      b->count>m->vertices-running||
      (b->tex!=UINT32_MAX&&b->tex>=m->texture_count)){
     fclose(f);memset(m,0,sizeof(*m));return 0;
   }
   running+=b->count;
 }
 if(running!=m->vertices){fclose(f);memset(m,0,sizeof(*m));return 0;}
 const size_t bytes=(size_t)m->vertices*sizeof(G68Vtx);
 G68Vtx *geometry=malloc(bytes);
 if(!geometry||!exact(f,geometry,bytes)||fgetc(f)!=EOF){
   free(geometry);fclose(f);memset(m,0,sizeof(*m));return 0;
 }
 fclose(f);
 for(size_t i=0;i<m->vertices;i++){
   for(int j=0;j<3;j++)if(!isfinite(geometry[i].xyz[j])){
     free(geometry);memset(m,0,sizeof(*m));return 0;
   }
 }
 /* Renderer owner already created the one VitaGL context. */
 GLuint buffer=0;glGenBuffers(1,&buffer);
 if(!buffer){free(geometry);memset(m,0,sizeof(*m));return 0;}
 m->vbo=buffer;
 glBindBuffer(GL_ARRAY_BUFFER,buffer);
 glBufferData(GL_ARRAY_BUFFER,(GLsizeiptr)bytes,geometry,GL_STATIC_DRAW);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 free(geometry);
 if(glGetError()!=GL_NO_ERROR){b24_g68_city_close(m);return 0;}
 for(unsigned i=0;i<m->texture_count;i++){
   char name[256];
   if(snprintf(name,sizeof(name),"%s_tex_%02u.g66t",texture_prefix,i)
      >=(int)sizeof(name)||!texture_load(&m->texture_ids[i],name)){
     b24_g68_city_close(m);return 0;
   }
 }
 m->ready=1;return 1;
}
int b24_g68_city_draw(const B24G68City *m){
 if(!m||!m->ready||!m->vbo)return 0;
 glEnable(GL_DEPTH_TEST);glDepthFunc(GL_LESS);
 /* Preserve G68 photographed blending baseline until alpha A/B test.
  * Native 2010 original shader/sort isn't recovered yet. */
 glEnable(GL_BLEND);
 glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
 glColor4f(1.f,1.f,1.f,1.f);
 glBindBuffer(GL_ARRAY_BUFFER,(GLuint)m->vbo);
 glEnableClientState(GL_VERTEX_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(G68Vtx),(const void *)(uintptr_t)0);
 glEnableClientState(GL_TEXTURE_COORD_ARRAY);
 glTexCoordPointer(2,GL_FLOAT,sizeof(G68Vtx),(const void *)(uintptr_t)12);
 glEnableClientState(GL_COLOR_ARRAY);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(G68Vtx),(const void *)(uintptr_t)20);
 for(unsigned i=0;i<m->batch_count;i++){
   const B24G68Batch *b=&m->batches[i];
   if(b->tex!=UINT32_MAX){
     glEnable(GL_TEXTURE_2D);
     glBindTexture(GL_TEXTURE_2D,(GLuint)m->texture_ids[b->tex]);
   }else glDisable(GL_TEXTURE_2D);
   glDrawArrays(GL_TRIANGLES,(GLint)b->first,(GLsizei)b->count);
 }
 glDisableClientState(GL_COLOR_ARRAY);
 glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);
 glDisable(GL_TEXTURE_2D);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 glColor4f(1.f,1.f,1.f,1.f);
 return glGetError()==GL_NO_ERROR;
}
/* The old B24 owner still dictates scene -> animated armor -> B24 HUD -> ONE
 * swap. The G68 standalone Player/update loop is deliberately excluded. */
int b24_gpu_owner_scene_g68(B24GpuOwner *o,const B24G68City *m){
 if(!o||!o->initialized||!o->frame_open||o->pass!=0||
    !b24_g68_city_draw(m))return 0;
 o->pass=1;o->scene_draws++;return 1;
}
