#ifndef B24_G72_SOURCE_LIGHT_H
#define B24_G72_SOURCE_LIGHT_H
/* Engineering-only baked dusk diffuse, NOT original Gameloft light shader.
 * Input is the genuine authored unindexed G66 mesh triangles in Z-up.
 * Applied once in CPU RAM just BEFORE existing STATIC GPU city VBO upload;
 * original geometry XYZ/UV, RGBA alpha bytes, textures and VPK unchanged.
 * Keeps one VBO and no per-frame CPU lighting. */
#include <math.h>
#include <stdint.h>
static inline float b24_g72_light_factor(const float a[3],const float b[3],
                                         const float c[3]){
 float ux=b[0]-a[0],uy=b[1]-a[1],uz=b[2]-a[2];
 float vx=c[0]-a[0],vy=c[1]-a[1],vz=c[2]-a[2];
 float nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
 float mag=sqrtf(nx*nx+ny*ny+nz*nz);
 if(!isfinite(mag)||mag<1e-8f)return .84f;
 /* Soft double-sided directional contribution avoids inverting real source
  * surface winding or creating black faces. Values are tuneable experiment. */
 float dot=(nx*.36f-ny*.44f+nz*.82f)/mag;
 if(dot<0.f)dot=0.f;
 if(dot>1.f)dot=1.f;
 return .78f+.21f*dot;
}
static inline unsigned char b24_g72_tint(unsigned char original,float f){
 float v=(float)original*f;
 if(v<0.f)v=0.f;
 if(v>255.f)v=255.f;
 return (unsigned char)(v+.5f);
}
static inline void b24_g72_color(unsigned char native_rgba[4],float f){
 native_rgba[0]=b24_g72_tint(native_rgba[0],f*.94f);
 native_rgba[1]=b24_g72_tint(native_rgba[1],f*.98f);
 native_rgba[2]=b24_g72_tint(native_rgba[2],f*1.01f);
 /* Native source alpha never altered. */
}
#endif
