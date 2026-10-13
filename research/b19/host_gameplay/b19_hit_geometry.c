#include "b19_hit_geometry.h"
#include <math.h>
static B19Point3 sub(B19Point3 a,B19Point3 b){B19Point3 d={a.x-b.x,a.y-b.y,a.z-b.z};return d;}
static float dot(B19Point3 a,B19Point3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
B19SegmentHit b19_segment_sphere(B19Point3 start,B19Point3 end,
                                 B19Point3 center,float radius){
    B19SegmentHit no={0,0.f};
    if(!isfinite(start.x)||!isfinite(start.y)||!isfinite(start.z)||
       !isfinite(end.x)||!isfinite(end.y)||!isfinite(end.z)||
       !isfinite(center.x)||!isfinite(center.y)||!isfinite(center.z)||
       !isfinite(radius)||radius<=0.f)return no;
    B19Point3 d=sub(end,start),m=sub(start,center);
    float rr=radius*radius,a=dot(d,d),c=dot(m,m)-rr;
    if(c<=0.f){B19SegmentHit inside={1,0.f};return inside;}
    if(a<=1e-12f)return no;
    float b=dot(m,d),disc=b*b-a*c;
    if(disc<0.f || !isfinite(disc))return no;
    float t=(-b-sqrtf(disc))/a;
    if(!isfinite(t)||t<0.f||t>1.f)return no;
    B19SegmentHit yes={1,t};return yes;
}
