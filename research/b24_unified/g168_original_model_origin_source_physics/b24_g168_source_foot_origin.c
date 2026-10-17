#include "b24_g168_source_foot_origin.h"
#include <math.h>
#include <string.h>
int b24_g168_source_bind_origin(B24G168FootOrigin *a,const void *verts,
                 size_t stride,uint32_t nv,float center){
 if(!a||!verts||stride<3*sizeof(float)||stride>128||
    !nv||nv>16000u||!isfinite(center))return 0;
 const unsigned char *p=verts;
 float low=0,high=0;
 for(uint32_t i=0;i<nv;i++){
  float z=0;
  memcpy(&z,p+(size_t)i*stride+2*sizeof(float),sizeof z);
  if(!isfinite(z)||fabsf(z)>100000.f)return 0;
  if(i==0||z<low)low=z;
  if(i==0||z>high)high=z;
 }
 if(high-low<.001f||high-low>100.f)return 0;
 B24G168FootOrigin out={low,center,nv,1};
 *a=out;return 1;
}
float b24_g168_actor_foot_z(const B24G168FootOrigin *a,float root){
 return a&&a->valid&&isfinite(root)?
         root-a->source_center_z+a->source_min_z:NAN;
}
float b24_g168_actor_root_z(const B24G168FootOrigin *a,float foot){
 return a&&a->valid&&isfinite(foot)?
         foot-a->source_min_z+a->source_center_z:NAN;
}
