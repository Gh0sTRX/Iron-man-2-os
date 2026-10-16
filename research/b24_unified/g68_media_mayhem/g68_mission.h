#ifndef IM2_G68_MISSION_H
#define IM2_G68_MISSION_H
/* FIRST-LEVEL VERTICAL SLICE, NOT original CLARA/Lua interpreter:
 * authentic opening theme = suitcase demonstration -> Stark Expo drone attack;
 * game rules/relative prototype enemy positions explicitly reconstructed.
 * Original Mission000 script, spawnpoint roles and AI still require provenance.
 */
#include <math.h>
#include <stdint.h>
#define G68_ENEMY_MAX 3
typedef struct {float x,y,z,health,cooldown;int alive;} G68Enemy;
typedef struct {
 G68Enemy bots[G68_ENEMY_MAX];
 int wave,knockouts,shots,hits,finished,lost;
 float cooldown,damage_flash;
} G68Mission;
static void g68_wave(G68Mission *m,float x,float y,float z){
 const float radial[3][2]={{8.f,12.f},{-9.f,15.f},{2.f,20.f}};
 const int active=m->wave==1?2:3;
 for(int i=0;i<G68_ENEMY_MAX;i++){
  G68Enemy *e=&m->bots[i];
  *e=(G68Enemy){x+radial[i][0],y+radial[i][1],
             z+1.5f+0.3f*i,100.f,2.2f+.5f*i,i<active};
 }
}
static void g68_start(G68Mission *m,float x,float y,float z){
 *m=(G68Mission){0};m->wave=1;g68_wave(m,x,y,z);
}
static int g68_remaining(const G68Mission *m){
 int n=0;for(int i=0;i<G68_ENEMY_MAX;i++)n+=m->bots[i].alive!=0;
 return n;
}
static void g68_tick(G68Mission *m,float dt,float x,float y,float z,
                     float *player_hp){
 if(m->finished||m->lost)return;
 m->cooldown=fmaxf(0.f,m->cooldown-dt);
 m->damage_flash=fmaxf(0.f,m->damage_flash-dt);
 for(int i=0;i<G68_ENEMY_MAX;i++){
  G68Enemy *e=&m->bots[i];if(!e->alive)continue;
  e->cooldown-=dt;
  const float dx=e->x-x,dy=e->y-y,dz=e->z-(z+1.1f);
  const float r2=dx*dx+dy*dy+dz*dz;
  if(r2<900.f&&e->cooldown<=0.f){
   *player_hp=fmaxf(0.f,*player_hp-7.f);
   m->damage_flash=.25f;
   e->cooldown=2.0f+(float)i*.45f;
  }
 }
 if(*player_hp<=0.f){m->lost=1;return;}
 if(g68_remaining(m)==0){
  if(m->wave==1){m->wave=2;g68_wave(m,x,y,z);}
  else m->finished=1;
 }
}
/* Repulsor fire cone, no arbitrary omnidirectional kills. LOS world/collider
 * obstruction NOT solved: caller must not claim original weapon behaviour. */
static int g68_shoot(G68Mission *m,float x,float y,float z,
                     float heading,float pitch,int melee){
 if(m->lost||m->finished||m->cooldown>0.f)return 0;
 m->cooldown=melee?.52f:.19f;
 m->shots++;
 float cp=cosf(pitch),vx=sinf(heading)*cp,
       vy=cosf(heading)*cp,vz=sinf(pitch);
 float score=-2.f;int pick=-1;
 for(int i=0;i<G68_ENEMY_MAX;i++){
  G68Enemy *e=&m->bots[i];
  if(!e->alive)continue;
  float dx=e->x-x,dy=e->y-y,dz=e->z-(z+1.2f);
  float d2=dx*dx+dy*dy+dz*dz;
  if(d2<.0001f||d2>(melee?10.f:3600.f))continue;
  float look=(dx*vx+dy*vy+dz*vz)/sqrtf(d2);
  if(look>(melee?.0f:.92f)&&look>score){score=look;pick=i;}
 }
 if(pick<0)return 0;
 G68Enemy *target=&m->bots[pick];
 target->health-=melee?58.f:38.f;
 m->hits++;
 if(target->health<=0.f){target->alive=0;m->knockouts++;}
 return 1;
}
#endif
