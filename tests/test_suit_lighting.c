#include "im2_suit_lighting.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void){
 B24GpuSuitVertex v[]={{0,0,0,0,0},{1,0,0,1,0},{0,1,0,0,1},{3,0,0,0,0},{3,1,0,1,0},{3,0,1,0,1}};
 B24GpuSuitTriangle t[]={{0,1,2},{3,4,5}};unsigned char atlas[]={1,2,3,91};
 B24GpuSuitSource src={v,t,atlas,6,2,1,1,0,0};B24GpuSuitVertex before[6];memcpy(before,v,sizeof(v));
 float root[]={1,0,0,0,0,1,0,0,0,0,1,0,500,500,0,1};float normals[18];unsigned char colors[24];
 assert(im2_suit_lighting_colors(&src,root,normals,colors,6));
 assert(colors[0]>colors[12]);for(unsigned i=0;i<6;i++)assert(colors[i*4+3]==255);
 assert(!memcmp(v,before,sizeof(v))&&atlas[3]==91);
 /* Rotation of actual draw root must change directional shading. */
 const float rotated[]={0,0,-1,0,0,1,0,0,1,0,0,0,500,500,0,1};unsigned char rotated_colors[24];
 assert(im2_suit_lighting_colors(&src,rotated,normals,rotated_colors,6));assert(memcmp(colors,rotated_colors,24));
 /* Equivalent geometry rotation with identity root gives same world response. */
 for(unsigned i=0;i<6;i++){float x=v[i].x;v[i].x=v[i].z;v[i].z=-x;}
 assert(im2_suit_lighting_colors(&src,root,normals,colors,6));
 for(unsigned i=0;i<24;i++)assert(abs((int)colors[i]-(int)rotated_colors[i])<=1);
 memset(colors,173,sizeof(colors));t[0].i0=99;
 assert(!im2_suit_lighting_colors(&src,root,normals,colors,6));for(unsigned i=0;i<24;i++)assert(colors[i]==173);
 t[0].i0=0;root[0]=NAN;assert(!im2_suit_lighting_colors(&src,root,normals,colors,6));root[0]=1;
 assert(!im2_suit_lighting_colors(&src,root,normals,colors,5));
 for(unsigned i=0;i<6;i++)v[i].x=v[i].y=v[i].z=0;
 assert(im2_suit_lighting_colors(&src,root,normals,colors,6));
 puts("PASS current-pose geometry normals, draw-root rotation, alpha preservation, invalid-input atomicity and degenerate faces; experimental lighting only");
 return 0;
}
