#include "b24_gpu_g72_sky.h"
#include <vitaGL.h>
#include <math.h>
#include <stddef.h>
/* Color vertex array; no texture, VBO, heap, second GL context or scene
 * geometry. Camera-relative horizon. The skyline is explicitly synthetic,
 * isolated behind B24_G72_DIAGNOSTIC_SKYLINE. */
typedef struct {float p[2];unsigned char color[4];} SkyVtx;
_Static_assert(sizeof(SkyVtx)==12,"G72 small sky vertices ABI changed");
static void put(SkyVtx *v,float x,float y,unsigned char r,
                unsigned char g,unsigned char b){
 v->p[0]=x;v->p[1]=y;
 v->color[0]=r;v->color[1]=g;v->color[2]=b;v->color[3]=255u;
}
static void tri(SkyVtx *v,unsigned *count, float x0,float x1,
                float low,float high,const unsigned char a[3],
                const unsigned char b[3]){
 put(&v[(*count)++],x0,low,a[0],a[1],a[2]);
 put(&v[(*count)++],x1,low,a[0],a[1],a[2]);
 put(&v[(*count)++],x0,high,b[0],b[1],b[2]);
 put(&v[(*count)++],x1,low,a[0],a[1],a[2]);
 put(&v[(*count)++],x1,high,b[0],b[1],b[2]);
 put(&v[(*count)++],x0,high,b[0],b[1],b[2]);
}
int b24_g72_draw_dusk_atmosphere(float pitch,float yaw){
 if(!isfinite(pitch)||!isfinite(yaw))return 0;
 /* Keep old game's camera and player framing: just add background. */
 float h=.01f-pitch*.58f;
 if(h<-.72f)h=-.72f;
 if(h>.64f)h=.64f;
 const unsigned char ground[3]={67,66,94};
 const unsigned char horizon[3]={84,81,125};
 const unsigned char upper[3]={27,43,88};
 const unsigned char zenith[3]={8,16,40};
 SkyVtx gradient[18];unsigned n=0;
 tri(gradient,&n,-1,1,-1.f,h-.18f,ground,horizon);
 tri(gradient,&n,-1,1,h-.18f,h+.34f,horizon,upper);
 tri(gradient,&n,-1,1,h+.34f,1.f,upper,zenith);
 glMatrixMode(GL_PROJECTION);glPushMatrix();glLoadIdentity();
 glMatrixMode(GL_MODELVIEW);glPushMatrix();glLoadIdentity();
 glDisable(GL_DEPTH_TEST);glDepthMask(GL_FALSE);
 glDisable(GL_TEXTURE_2D);glDisable(GL_BLEND);
 glDisable(GL_LIGHTING);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 glEnableClientState(GL_VERTEX_ARRAY);glEnableClientState(GL_COLOR_ARRAY);
 glVertexPointer(2,GL_FLOAT,sizeof(SkyVtx),&gradient[0].p[0]);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(SkyVtx),&gradient[0].color[0]);
 glDrawArrays(GL_TRIANGLES,0,(GLsizei)n);
#ifdef B24_G72_DIAGNOSTIC_SKYLINE
 /* Inexpensive single-batch silhouette of the distant city horizon.
  * Intentionally NOT the genuine authored C1L1_sky_001 and can be disabled.
  * Deterministic orientation scrolling means no perspective sprite. */
 SkyVtx blocks[34*6];unsigned m=0;
 const unsigned char silhouette[3]={16,30,59};
 const float shift=fmodf(yaw*.22f,2.f);
 for(int i=0;i<34;i++){
  float x=-1.1f+(float)i*(2.2f/34.f)-shift*.02f;
  float xr=x+.035f+(float)((i*7)%5)*.004f;
  float roof=h+.015f+(float)((i*13)%9)*.018f;
  if(roof>h+.2f)roof=h+.2f;
  tri(blocks,&m,x,xr,h-.08f,roof,silhouette,silhouette);
 }
 glVertexPointer(2,GL_FLOAT,sizeof(SkyVtx),&blocks[0].p[0]);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(SkyVtx),&blocks[0].color[0]);
 glDrawArrays(GL_TRIANGLES,0,(GLsizei)m);
#else
 (void)yaw;
#endif
 glDisableClientState(GL_COLOR_ARRAY);glDisableClientState(GL_VERTEX_ARRAY);
 glDepthMask(GL_TRUE);glEnable(GL_DEPTH_TEST);
 glMatrixMode(GL_PROJECTION);glPopMatrix();
 glMatrixMode(GL_MODELVIEW);glPopMatrix();
 glColor4f(1.f,1.f,1.f,1.f);
 return glGetError()==GL_NO_ERROR;
}
