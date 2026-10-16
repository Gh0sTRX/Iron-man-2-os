#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../b24_gpu_g72_light.h"
int main(void){
 float a[3]={0,0,0},b[3]={1,0,0},c[3]={0,1,0};
 float lit=b24_g72_light_factor(a,b,c);
 assert(lit>.78f&&lit<=.99f);
 unsigned char color[4]={255,200,120,37},backup_alpha=color[3];
 b24_g72_color(color,lit);
 assert(color[0]<255&&color[1]<200&&color[2]<120);
 assert(color[3]==backup_alpha);
 float bad[3]={NAN,0,0};
 assert(b24_g72_light_factor(bad,b,c)==.84f);
 assert(b24_g72_tint(255,2.f)==255);
 puts("PASS G72: host daylight normal, conservative color modulation, native RGBA alpha unchanged");
 return 0;
}
