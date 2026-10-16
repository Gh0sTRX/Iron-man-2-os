#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "b14_world.h"
static void advance(B14World *w,int flight,int rush,float forward,int n){
 w->flying=flight;w->rush=rush;
 for(int k=0;k<n;k++)b14_world_tick(w,.016f,0.f,forward,0.f,0.f,0.f);
}
static float distance(B14World *w){return hypotf(w->x,w->y);}
int main(void){
 B14World ground={0},fast={0},flight={0},rush={0};
 b14_world_init(&ground);b14_world_init(&fast);
 b14_world_init(&flight);b14_world_init(&rush);
 advance(&ground,0,0,.65f,60);
 advance(&fast,0,1,1.f,60);
 advance(&flight,1,0,1.f,60);
 advance(&rush,1,1,1.f,60);
 float a=distance(&ground),b=distance(&fast);
 float c=distance(&flight),d=distance(&rush);
 printf("G75 0.96s ground=%0.3f run=%0.3f air=%0.3f rush=%0.3f\n",a,b,c,d);
 fprintf(stderr,"G75 G9 reconstructed source movement four real displacements: %.7f %.7f %.7f %.7f\n",a,b,c,d);
 assert(a>1.f&&a<4.f);
 assert(b>a*1.4f);
 assert(c>b*1.15f);
 assert(d>c*1.4f);
 B14World look={0};b14_world_init(&look);
 for(int i=0;i<120;i++)b14_world_tick(&look,.016f,0,0,0,1,0);
 assert(look.pitch>.90f && look.pitch<=1.050001f);
 for(int i=0;i<120;i++)b14_world_tick(&look,.016f,0,0,0,-1,0);
 assert(look.pitch<-.85f && look.pitch>=-.920001f);
 B14World stop={0};b14_world_init(&stop);
 advance(&stop,1,1,1.f,60);
 float before=distance(&stop);
 for(int i=0;i<60;i++)b14_world_tick(&stop,.016f,0,0,0,0,0);
 assert(distance(&stop)>before);
 assert(distance(&stop)<before+2.5f);
 puts("PASS G75: ground/run/air/rush responsiveness, eased coast and full up/down manual camera range");
 return 0;
}
