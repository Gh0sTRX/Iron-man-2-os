#include "b24_g156_exact_vertical_triangle_contact.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

/* Source-format XYZ triangle (not an invented asset): a steep 2010-style
 * wall panel whose intersection is in BETWEEN the three G75/G108 height
 * samples. Reproducer for actual code path's geometric undersampling;
 * no claim that these exact authored coords occurred in source C1L1. */
static float dist2(float px,float py,float ax,float ay,
                   float bx,float by) {
 float dx=bx-ax,dy=by-ay,dd=dx*dx+dy*dy;
 float t=dd>1.e-10f?((px-ax)*dx+(py-ay)*dy)/dd:0;
 if(t<0)t=0;if(t>1)t=1;
 float qx=px-(ax+t*dx),qy=py-(ay+t*dy);
 return qx*qx+qy*qy;
}
static int original_three_height_samples_miss(float x,float y,float r) {
 /* Triangle intersection at height z: x=z/2-1;
  * y between -1 and (z/2-1) on the same original-format plane.
  * Old G75/G108 take ONLY .005, 2.0, 3.995 at foot0/head4.
  */
 const float sampled[3]={.005f,2.f,3.995f};
 for(int i=0;i<3;i++){
  const float z=sampled[i],wallx=z*.5f-1.f;
  if(dist2(x,y,wallx,-1.f,wallx,wallx)<r*r)return 0;
 }
 return 1;
}
int main(void) {
 const float original_format_source_wall[9]={
  -1.f,-1.f,0.f,1.f,-1.f,4.f,1.f,1.f,4.f
 };
 const float x=-.55f,y=-.78f,r=.35f,h=4.f;
 /* The previous three selected z slices miss a REAL intersection at
  * z=.90 even though r=.35: this is the exact root-cause repro. */
 assert(original_three_height_samples_miss(x,y,r));
 assert(b24_g156_exact_vertical_triangle_contact(
     original_format_source_wall,x,y,0.f,r,h));
 assert(!b24_g156_exact_vertical_triangle_contact(
     original_format_source_wall,-4.f,-4.f,0.f,r,h));
 assert(!b24_g156_exact_vertical_triangle_contact(
     original_format_source_wall,x,y,5.f,r,h));
 assert(!b24_g156_exact_vertical_triangle_contact(
     original_format_source_wall,x,y,-5.f,r,2.f));
 /* Vertical authored original-format wall triangle source:
  * projected XY polygon degenerates to line, not infinite plane. */
 const float true_vertical[9]={
  10.6f,-50.f,-2.f,10.6f,50.f,-2.f,10.6f,0.f,10.f
 };
 assert(b24_g156_exact_vertical_triangle_contact(
     true_vertical,10.6f,0.f,0.f,.35f,2.24f));
 assert(!b24_g156_exact_vertical_triangle_contact(
     true_vertical,11.5f,0.f,0.f,.35f,2.24f));
 assert(!b24_g156_exact_vertical_triangle_contact(
     true_vertical,10.6f,70.f,0.f,.35f,2.24f));
 assert(!b24_g156_exact_vertical_triangle_contact(
     true_vertical,10.6f,0.f,20.f,.35f,2.24f));
 /* Original renderer may contain slanted planes/degenerate XY polygon.
  * Never interpret outside XY triangle as solidity solely by AABB. */
 const float sloped_source_style[9]={
  -2.f,-2.f,0.f,2.f,-2.f,1.f,-2.f,2.f,1.f
 };
 assert(b24_g156_exact_vertical_triangle_contact(
     sloped_source_style,-1.5f,-1.5f,0.f,.35f,2.24f));
 assert(!b24_g156_exact_vertical_triangle_contact(
     sloped_source_style,1.7f,1.7f,0.f,.35f,2.24f));
 /* Fail-closed input validation, no synthetic original physics. */
 assert(!b24_g156_exact_vertical_triangle_contact(
     original_format_source_wall,NAN,0.f,0.f,r,h));
 assert(!b24_g156_exact_vertical_triangle_contact(
     original_format_source_wall,0.f,0.f,0.f,0.f,h));
 puts("G156 PASS: old G75/G108 3-Z samples miss steep slant; continuous exact original-format triangle blocks actual between-slice contact without filling open scenery. NO VPK.");
 return 0;
}
