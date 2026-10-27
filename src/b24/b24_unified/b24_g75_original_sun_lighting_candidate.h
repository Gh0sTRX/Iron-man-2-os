#ifndef B24_G75_ORIGINAL_SUN_CANDIDATE_H
#define B24_G75_ORIGINAL_SUN_CANDIDATE_H
#include <math.h>
#include <stdint.h>
/* C1L1 level1.bclara typed actual Sun001/2/3/4 LIGHT positions from G30.
 * Geometry/position data is AUTHENTIC; local-space->world, falloff, color,
 * original shader and intensity interpretation are NOT RECOVERED.
 * Use only as reversible VitaGL visual A/B, never "native source light". */
typedef struct{float x,y,z;} B24G75Vec;
typedef struct{
 B24G75Vec original_local_xyz;
 float approximate_falloff_radius; /* diagnostic, not native authored */
 float approximate_intensity;      /* diagnostic, not native authored */
} B24G75Light;
static const B24G75Light b24_g75_source_light_positions[4]={
 {{-23.170f,-21.477f,37.670f},70.f,.38f}, /* Sun001 */
 {{-19.994f,-21.699f,37.906f},70.f,.32f}, /* Sun002 */
 {{-32.448f,100.158f,29.493f},95.f,.38f}, /* Sun003 */
 {{-21.325f,-20.287f,37.906f},70.f,.30f}  /* Sun004 */
};
static inline float b24_g75_clamp01(float x){
 return x<0.f?0.f:x>1.f?1.f:x;
}
static inline B24G75Vec b24_g75_sub(B24G75Vec a,B24G75Vec b){
 B24G75Vec v={a.x-b.x,a.y-b.y,a.z-b.z};return v;
}
static inline float b24_g75_dot(B24G75Vec a,B24G75Vec b){
 return a.x*b.x+a.y*b.y+a.z*b.z;
}
static inline float b24_g75_len(B24G75Vec a){return sqrtf(b24_g75_dot(a,a));}
static inline B24G75Vec b24_g75_unit(B24G75Vec a){
 float mag=b24_g75_len(a);
 if(!isfinite(mag)||mag<1e-8f)return (B24G75Vec){0,0,1};
 return (B24G75Vec){a.x/mag,a.y/mag,a.z/mag};
}
/* Geometric hemisphere ambient + one world-space key + four G30 sourced
 * light positions treated as TEST POINT sources. Not original Gameloft
 * light type 2/0 interpretation. Full mesh static bake once on Vita, zero
 * light loops at runtime. Could be called on moving armor each frame later. */
static inline float b24_g75_light_factor(B24G75Vec position,B24G75Vec normal){
 normal=b24_g75_unit(normal);
 const B24G75Vec moon=b24_g75_unit((B24G75Vec){-.28f,-.38f,.88f});
 float lambert=b24_g75_dot(normal,moon);
 float val=.42f+.22f*b24_g75_clamp01(normal.z)+.17f*b24_g75_clamp01(lambert);
 for(int i=0;i<4;i++){
  B24G75Vec to=b24_g75_sub(b24_g75_source_light_positions[i].original_local_xyz,position);
  const float distance=b24_g75_len(to);
  const float radius=b24_g75_source_light_positions[i].approximate_falloff_radius;
  const float ndotl=b24_g75_clamp01(b24_g75_dot(normal,b24_g75_unit(to)));
  const float attenuation=1.f/(1.f+(distance/radius)*(distance/radius)*5.f);
  val+=b24_g75_source_light_positions[i].approximate_intensity*attenuation*ndotl;
 }
 if(!isfinite(val))return .72f;
 return fmaxf(.26f,fminf(val,1.1f));
}
static inline void b24_g75_light_original_vertex(unsigned char rgba[4],
  B24G75Vec pos,B24G75Vec surface_normal){
 float f=b24_g75_light_factor(pos,surface_normal);
 /* Dusk cool channel offsets are clearly diagnostic tuning, not
  * a decoded source packed color. Preserve source alpha EXACTLY. */
 const float rgb[3]={f*.94f,f*.98f,f*1.04f};
 for(int c=0;c<3;c++){
   float b=(float)rgba[c]*rgb[c];
   rgba[c]=(unsigned char)(fminf(255.f,fmaxf(0.f,b))+.5f);
 }
}
#endif
