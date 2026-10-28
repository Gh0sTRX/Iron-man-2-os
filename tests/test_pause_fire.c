/* Actual main fire block; fake OS/game endpoints count accepted calls only. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#define B24_GPU_ENGINE 1
#define B16_REPULSOR 0
#define B16_MISSILE 1
#define B16_UNIBEAM 2
typedef struct{int paused;} Game;
static int fires,arm_begins,source_shots;
static unsigned arm_time,shot_time;
static int b24_unified_paused(const Game *g){return g->paused;}
static void b16_model_palm(const void *model,const void *world,unsigned emitter,float out[3]){
 (void)model;(void)world;(void)emitter;out[0]=out[1]=out[2]=0.f;
}
static int b16_combat_fire(void *combat,void *world,const float muzzle[3]){
 (void)combat;(void)world;(void)muzzle;fires++;return 0;
}
static void b16_attack_begin(void *attack,unsigned time,int flying,int a,int b){
 (void)attack;(void)flying;(void)a;(void)b;arm_begins++;arm_time=time;
}
static void b24_g8_motion_repulsor_trigger(void *motion,uint32_t time){
 (void)motion;source_shots++;shot_time=time;
}
static int frame(int paused,int trigger){
 Game b24_game={paused};struct{int mode;} combat={B16_REPULSOR};
 struct{unsigned palm_r;int attack_active;}attack={1,0};struct{int flying;}world={0};
 int model=0,b24_original_motion=0;unsigned b17_chest_vertex=2,b17_shoulder_vertex=3;
 const uint32_t now=20000,motion_now=1200;(void)now;(void)motion_now;(void)b24_game;(void)b24_unified_paused;
 #include "actual_fire_event.inc"
 return trigger;
}
int main(void){
 assert(frame(1,1)==0);assert(fires==0&&arm_begins==0&&source_shots==0);
 assert(frame(0,0)==0);assert(fires==0);
 assert(frame(0,1)==0);assert(fires==1&&arm_begins==1&&source_shots==1);
 assert(arm_time==1200&&shot_time==1200);
 assert(frame(1,1)==0);assert(fires==1);
 puts("PASS canonical main: no accepted shot while paused, no queued press, one shared action timestamp");
 return 0;
}
