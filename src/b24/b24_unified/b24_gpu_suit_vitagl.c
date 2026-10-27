#include "b24_gpu_suit.h"
#include <vitaGL.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE
/* G299: only original four Sun positions are sourced, NOT the original
 * GameLoft shading equation. Strictly experimental per-actor ambient. */
#ifndef B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE
#error "G299 only with G75 shared original CLARA four-Sun source and its candidate"
#endif
#include "b24_g75_original_sun_lighting_candidate.h"
#endif
_Static_assert(sizeof(B24GpuSuitVertex)==20,"IM2T GPU animated vertex ABI");
_Static_assert(sizeof(B24GpuSuitTriangle)==6,"IM2T GPU triangle ABI");

int b24_gpu_suit_validate(const B24GpuSuitSource *s){
 if(!s||!s->vertices||!s->triangles||!s->texture_rgba||
    !s->nv||s->nv>16000||!s->nt||s->nt>24000||
    !s->tw||!s->th||s->tw>2048||s->th>2048||
    !isfinite(s->center_z))return 0;
 for(uint32_t i=0;i<s->nv;i++){
    const B24GpuSuitVertex *v=&s->vertices[i];
    if(!isfinite(v->x)||!isfinite(v->y)||!isfinite(v->z)||
       !isfinite(v->u)||!isfinite(v->v))return 0;
 }
 for(uint32_t i=0;i<s->nt;i++){
    const B24GpuSuitTriangle *t=&s->triangles[i];
    if(t->i0>=s->nv||t->i1>=s->nv||t->i2>=s->nv)return 0;
 }
 return 1;
}
int b24_gpu_suit_matrix(float m[16],const B24GpuSuitPose *p,float center_z){
 if(!m||!p||!isfinite(p->x)||!isfinite(p->y)||!isfinite(p->z)||
    !isfinite(p->heading)||!isfinite(p->pitch)||!isfinite(p->roll)||
    !isfinite(center_z)||fabsf(p->pitch)>1.05f||fabsf(p->roll)>1.05f)return 0;
 /* Authoritative B17 original Z-up model basis B, then B * Rx(pitch) *
    Ry(bank): heading remains the physical collision/world heading. The
    bank is about original model forward (-Y), NOT world vertical Z.
    This affects visible armor ONLY; B14 physics remains CPU-authoritative.
    Do not claim pitch-based flight acceleration or muzzle sockets fixed. */
 float c=cosf(p->heading),s=sinf(p->heading);
 float cp=cosf(p->pitch),sp=sinf(p->pitch);
 float cr=cosf(p->roll),sr=sinf(p->roll);
 memset(m,0,16*sizeof(float));
 m[0]=-c*cr+s*sp*sr;
 m[1]= s*cr+c*sp*sr;
 m[2]=-cp*sr;
 m[4]=-s*cp;
 m[5]=-c*cp;
 m[6]=sp;
 m[8]=-c*sr+s*sp*cr;
 m[9]= s*sr+c*sp*cr;
 m[10]=cp*cr;
 m[15]=1.f;
 m[12]=p->x;m[13]=p->y;m[14]=p->z-center_z;
 return 1;
}
int b24_gpu_suit_prepare(B24GpuSuit *s,const B24GpuSuitSource *src){
 if(!s||s->prepared||!b24_gpu_suit_validate(src))return 0;
 GLuint texture=0;
 glGenTextures(1,&texture);
 if(!texture)return 0;
 glBindTexture(GL_TEXTURE_2D,texture);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
 /* Upload original recovered IM2T RGBA atlas ONCE on armor switch,
    never upload the entire CPU-rendered 480x272 framebuffer per frame. */
 glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,(GLsizei)src->tw,(GLsizei)src->th,
             0,GL_RGBA,GL_UNSIGNED_BYTE,src->texture_rgba);
 /* A generated texture ID does not prove atlas storage succeeded. In
  * particular, do not claim a prepared original suit after VRAM exhaustion. */
 if(glGetError()!=GL_NO_ERROR){glDeleteTextures(1,&texture);return 0;}
 s->texture_id=texture;s->nv=src->nv;s->nt=src->nt;
 s->tw=src->tw;s->th=src->th;s->prepared=1;
 return 1;
}
int b24_gpu_suit_draw(const B24GpuSuit *s,const B24GpuSuitSource *src,
                      const B24GpuSuitPose *pose){
 if(!s||!s->prepared||!src||!src->vertices||!src->triangles||
    !pose||src->nv!=s->nv||src->nt!=s->nt||
    src->tw!=s->tw||src->th!=s->th)return 0;
 float root[16];
#ifdef B24_G168_ORIGINAL_SUIT_RENDER_FOOT
 /* B14 world.z is a source G75 verified collision FOOT, not a model
  * midpoint. The old GPU matrix subtracted model.center_z and buried
  * original Iron Man rest minZ below the road/vehicle world plane.
  * Native bind source minimum is loaded once from the 2010 .im2t
  * BEFORE original animation mutations. Zero mesh/unit scaling.
  * This corrects ONLY the suit-to-world translation on GPU. */
 if(!isfinite(src->native_bind_min_z))return 0;
 if(!b24_gpu_suit_matrix(root,pose,src->native_bind_min_z))return 0;
#else
 if(!b24_gpu_suit_matrix(root,pose,src->center_z))return 0;
#endif
 glMatrixMode(GL_MODELVIEW);
 glPushMatrix();
 glMultMatrixf(root);
 glEnable(GL_DEPTH_TEST);
 glEnable(GL_TEXTURE_2D);
 glBindTexture(GL_TEXTURE_2D,s->texture_id);
#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE
 /* G299 research candidate: reuse G95's four SOURCE-LOCAL Sun coords,
  * never guess original 2010 dynamic light type/shader or rig normals.
  * Uniform actor color follows B14/G75 actual WORLD root each frame,
  * with alpha=1 so original recovered IM2T atlas alpha is untouched.
  * The CLARA local->world light transform is NOT yet resolved; this is
  * diagnostic illumination only, not parity with original iOS. */
 GLint g299_prior_texture_env=GL_MODULATE;
 glGetTexEnviv(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,&g299_prior_texture_env);
 glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE);
 const B24G75Vec actor_xyz={pose->x,pose->y,pose->z};
 const B24G75Vec test_up={0.f,0.f,1.f};
 const float g299_brightness=fminf(1.f,fmaxf(0.f,
                       b24_g75_light_factor(actor_xyz,test_up)));
 glColor4f(g299_brightness,g299_brightness,g299_brightness,1.f);
#else
 glColor4f(1.f,1.f,1.f,1.f);
#endif
 glEnableClientState(GL_VERTEX_ARRAY);
 glEnableClientState(GL_TEXTURE_COORD_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(B24GpuSuitVertex),&src->vertices[0].x);
 glTexCoordPointer(2,GL_FLOAT,sizeof(B24GpuSuitVertex),&src->vertices[0].u);
 glDrawElements(GL_TRIANGLES,(GLsizei)(src->nt*3u),
                GL_UNSIGNED_SHORT,src->triangles);
 glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);
 glDisable(GL_TEXTURE_2D);
#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE
 glColor4f(1.f,1.f,1.f,1.f);
 glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,g299_prior_texture_env);
#endif
 glPopMatrix();
 return 1;
}
void b24_gpu_suit_release(B24GpuSuit *s){
 if(!s)return;
 if(s->prepared){
    GLuint texture=s->texture_id;
    glDeleteTextures(1,&texture);
 }
 memset(s,0,sizeof(*s));
}
