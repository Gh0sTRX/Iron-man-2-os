#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "b24_g75_original_sun_lighting_candidate.h"
int main(void){
 const B24G75Vec n={0,0,1};
 const B24G75Vec near={-23.17f,-21.477f,0.f},far={500.f,500.f,0.f};
 float a=b24_g75_light_factor(near,n);
 float b=b24_g75_light_factor(far,n);
 assert(a>b && a>.25f && a<=1.1f && b>.25f);
 unsigned char color[4]={210,210,210,91};
 b24_g75_light_original_vertex(color,near,n);
 assert(color[3]==91);
 assert(color[0]>0 && color[2]>0);
 assert(b24_g75_light_factor(near,(B24G75Vec){0,0,0})>0.f);
 printf("PASS G75 4 real authored Sun positions with diagnostic distance attenuation: near %.3f far %.3f original alpha %u preserved\n",a,b,color[3]);
 return 0;
}
