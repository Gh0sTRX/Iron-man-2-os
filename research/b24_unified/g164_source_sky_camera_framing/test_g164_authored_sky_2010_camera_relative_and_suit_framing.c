#include "b24_g164_camera_sky_framing.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 /* Real G73 sky BRES (6 authentic batches 288 source vertices) should
  * NOT translate while roaming original 2010 C1L1 x[-761,+649].
  * No fake moon position, no newly generated skyline mesh. */
 const float view[16]={
  1,0,0,0, 0,1,0,0, 0,0,1,0,
  158.5f,299.25f,-4.5f,1
 };
 float sky[16]={0};
 assert(b24_g164_source_sky_view(view,sky));
 for(int i=0;i<12;i++)assert(sky[i]==view[i]);
 assert(sky[12]==0.f&&sky[13]==0.f&&sky[14]==0.f&&sky[15]==1.f);
 assert(view[12]==158.5f&&view[13]==299.25f);
 float d=0,fov=0;
 assert(b24_g164_camera_framing(1.f,&d,&fov));
 assert(fabsf(d-.87f)<.00001f&&fabsf(fov-68.f)<.00001f);
 assert(b24_g164_camera_framing(0.f,&d,&fov));
 assert(d==1.f&&fov==72.f);
 assert(b24_g164_camera_framing(.5f,&d,&fov));
 assert(d>.87f&&d<1.f&&fov>68.f&&fov<72.f);
 assert(!b24_g164_camera_framing(NAN,&d,&fov));
 float bad[16]={0};
 assert(!b24_g164_source_sky_view(bad,sky));
 puts("G164 PASS original 2010 G73 moon/stars/skyline camera-relative rotation-only source sky; 2.2355 unit MarkV model world scale untouched; ground shoulder camera QA 68deg .87 distance. NO VPK");
 return 0;
}
