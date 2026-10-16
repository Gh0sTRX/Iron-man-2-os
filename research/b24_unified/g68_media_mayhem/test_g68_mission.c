#include <assert.h>
#include <stdio.h>
#include "g68_mission.h"
int main(void){
 G68Mission m={0};float hp=100;
 g68_start(&m,0,0,0);
 assert(m.wave==1&&g68_remaining(&m)==2);
 /* Out-of-range and backwards shooting must not damage original wave. */
 assert(!g68_shoot(&m,0,0,0,3.14159f,0,0));
 g68_tick(&m,.3f,0,0,0,&hp);
 assert(m.knockouts==0&&hp==100);
 /* Aim directly at each prototype target, with realistic cooldown. */
 for(int n=0;n<2;n++){
  for(int i=0;i<3;i++)if(m.bots[i].alive){
   float heading=atan2f(m.bots[i].x,m.bots[i].y);
   for(int shot=0;shot<3;shot++){
    g68_tick(&m,.21f,0,0,0,&hp);
    (void)g68_shoot(&m,0,0,0,heading,0,0);
   }
  }
  g68_tick(&m,.02f,0,0,0,&hp);
  if(n==0)assert(m.wave==2&&g68_remaining(&m)==3);
 }
 assert(m.knockouts==5&&m.finished&&!m.lost);
 assert(!g68_shoot(&m,0,0,0,0,0,0));
 G68Mission failure={0};float hp2=5;
 g68_start(&failure,0,0,0);
 g68_tick(&failure,3.1f,0,0,0,&hp2);
 assert(failure.lost&&!failure.finished&&hp2==0.f);
 puts("PASS G68 2 waves / 5 targets / repulsor facing cone / defeat / restart");
 return 0;
}
