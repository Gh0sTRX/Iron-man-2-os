#include "b24_g164_camera_sky_framing.h"
#include <math.h>
#include <string.h>
int b24_g164_source_sky_view(const float world_view[16],float sky_view[16]){
 if(!world_view||!sky_view)return 0;
 for(int i=0;i<16;i++)if(!isfinite(world_view[i]))return 0;
 if(fabsf(world_view[15]-1.f)>.001f)return 0;
 /* source BRES sphere and skyline crosstrees are world origin centered,
  * but at gameplay world x/y hundreds from origin the previous GL view
  * translated them like buildings. Stars can remain visible while
  * near-horizon skyline and moon vanish. GL modelview camera rotation is
  * preserved; source sky is geometrically drawn at infinity. */
 memcpy(sky_view,world_view,16u*sizeof(float));
 sky_view[12]=sky_view[13]=sky_view[14]=0.f;
 return 1;
}
int b24_g164_camera_framing(float shoulder_weight,float *distance_mul,
                             float *fov_deg){
 if(!distance_mul||!fov_deg||!isfinite(shoulder_weight))return 0;
 if(shoulder_weight<0.f)shoulder_weight=0.f;
 if(shoulder_weight>1.f)shoulder_weight=1.f;
 /* Stage2/Rush shoulder=0: unchanged 4.35-distance, 72 degree world;
  * ground/hover shoulder=1: camera ~13% nearer, 68 degrees FOV.
  * Purely experimental presentation: NOT model/physics/global map scale.
  * Existing G22 smooth shoulder-to-chase transition owns interpolation. */
 *distance_mul=1.f-.13f*shoulder_weight;
 *fov_deg=72.f-4.f*shoulder_weight;
 return 1;
}
