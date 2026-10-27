#ifndef B24_G156_EXACT_VERTICAL_TRIANGLE_CONTACT_H
#define B24_G156_EXACT_VERTICAL_TRIANGLE_CONTACT_H
/* Continuous vertical CYLINDER vs one original planar source wall face.
 * This replaces G75/G108 THREE selected z slices with an exact planar
 * Z-clipped convex polygon XY radial test, rather than missing a diagonal
 * wall between those sample heights. No fake collision triangles, scene
 * physics owner, animation or mission events. Header-only to avoid an
 * additional Vita runtime movement owner/link path.
 *
 * The caller has already classified wall solidity/visual-source candidate,
 * validated finite input and filtered XY AABB. This routine changes only
 * geometry contact, NOT original iOS object material/solidness metadata.
 * The .005 source overlap inset matches the original G75/G108 guards.
 */
#include <math.h>
typedef struct { float x,y,z; } B24G156Point;

static inline int b24_g156_clip_plane(
    const B24G156Point *in,int len,B24G156Point *out,
    float zplane,int keep_above)
{
    int n=0;
    if(len<1||len>6)return 0;
    for(int i=0;i<len;i++) {
        const B24G156Point a=in[(i+len-1)%len], b=in[i];
        const int ain=keep_above?(a.z>=zplane):(a.z<=zplane);
        const int bin=keep_above?(b.z>=zplane):(b.z<=zplane);
        if(ain!=bin) {
            const float den=b.z-a.z;
            if(fabsf(den)<=1.e-12f)return 0;
            float t=(zplane-a.z)/den;
            if(t<0.f)t=0.f;
            if(t>1.f)t=1.f;
            if(n>=6)return 0;
            out[n++]=(B24G156Point){a.x+(b.x-a.x)*t,
                                     a.y+(b.y-a.y)*t,zplane};
        }
        if(bin) {
            if(n>=6)return 0;
            out[n++]=b;
        }
    }
    return n;
}

static inline float b24_g156_xy_seg_distance2(
    float x,float y,B24G156Point a,B24G156Point b)
{
    const float dx=b.x-a.x,dy=b.y-a.y,dd=dx*dx+dy*dy;
    float t=dd>1.e-12f?((x-a.x)*dx+(y-a.y)*dy)/dd:0.f;
    if(t<0.f)t=0.f;
    if(t>1.f)t=1.f;
    const float ex=x-(a.x+t*dx),ey=y-(a.y+t*dy);
    return ex*ex+ey*ey;
}

static inline int b24_g156_exact_vertical_triangle_contact(
    const float xyz[9],float x,float y,float feet,float radius,float height)
{
    if(!xyz||!isfinite(x)||!isfinite(y)||!isfinite(feet)||
       !isfinite(radius)||!isfinite(height)||
       radius<=0.f||height<=.01f)return 0;
    const float zlow=feet+.005f,zhigh=feet+height-.005f;
    if(zhigh<zlow)return 0;
    const B24G156Point triangle[3]={
        {xyz[0],xyz[1],xyz[2]},
        {xyz[3],xyz[4],xyz[5]},
        {xyz[6],xyz[7],xyz[8]}
    };
    for(int i=0;i<3;i++)
        if(!isfinite(triangle[i].x)||!isfinite(triangle[i].y)||
           !isfinite(triangle[i].z))return 0;
    B24G156Point half[6],polygon[6];
    const int n1=b24_g156_clip_plane(triangle,3,half,zlow,1);
    if(n1<1)return 0;
    const int n=b24_g156_clip_plane(half,n1,polygon,zhigh,0);
    if(n<1)return 0;
    const float r2=radius*radius;
    if(n==1) {
        const float dx=x-polygon[0].x,dy=y-polygon[0].y;
        return dx*dx+dy*dy<r2;
    }
    /* Intersect projected convex clipping polygon with XY disc.
     * A sloped wall can project to a filled area; a perfect vertical wall
     * projects to a line. Both must work; degenerate area never uses the
     * point-in-poly shortcut. */
    float area2=0.f;
    int pos=0,neg=0;
    for(int i=0;i<n;i++) {
        B24G156Point a=polygon[i],b=polygon[(i+1)%n];
        area2+=a.x*b.y-b.x*a.y;
        const float cross=(b.x-a.x)*(y-a.y)-(b.y-a.y)*(x-a.x);
        if(cross>1.e-6f)pos=1;
        if(cross< -1.e-6f)neg=1;
        if(b24_g156_xy_seg_distance2(x,y,a,b)<r2)return 1;
    }
    if(fabsf(area2)>1.e-8f && !(pos&&neg))return 1;
    return 0;
}
#endif
