#include "b19_gameplay_core.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static void wait(B19Game *g){for(int k=0;k<11;k++)b19_tick(g,.02f);}
static int aim_and_hit(B19Game *g,int i){
    B19Enemy *e=&g->enemies[i];B19Vec3 p={e->pos.x,e->pos.y,e->pos.z+1.f};
    B19Vec3 origin=g->player_pos;
    B19Vec3 d={p.x-origin.x,p.y-origin.y,p.z-origin.z};
    return b19_fire_repulsor(g,origin,d);
}
int main(void){
    B19Game g;b19_init(&g);
    assert(g.state==B19_PLAYING&&g.alive==2&&g.wave==0);
    assert(g.player_hp==100.f&&g.player_shield==25.f);
    assert(b19_fire_repulsor(&g,(B19Vec3){0,0,0},(B19Vec3){0,0,0})==-1);
    int miss=b19_fire_repulsor(&g,(B19Vec3){0,0,0},(B19Vec3){0,-1,0});
    assert(miss==0&&g.alive==2);
    assert(b19_fire_repulsor(&g,(B19Vec3){0,0,0},(B19Vec3){0,1,0})==-1);
    wait(&g);
    assert(aim_and_hit(&g,0)>0);wait(&g);
    assert(aim_and_hit(&g,0)>0);assert(g.alive==1);wait(&g);
    assert(aim_and_hit(&g,1)>0);wait(&g);
    int final_first_wave_id=g.enemies[1].id;
    assert(aim_and_hit(&g,1)==final_first_wave_id);
    assert(g.wave==1&&g.alive==3);
    for(int i=0;i<3;i++){wait(&g);assert(aim_and_hit(&g,i)>0);wait(&g);assert(aim_and_hit(&g,i)>0);}
    assert(g.state==B19_WON&&g.kills==5&&g.alive==0);
    B19Event ev;int saw_win=0,saw_start=0,saw_death=0;
    while(b19_pop_event(&g,&ev)){saw_win+=ev.type==B19_EV_MISSION_WIN;saw_start+=ev.type==B19_EV_WAVE_START;saw_death+=ev.type==B19_EV_ENEMY_DIED;}
    assert(saw_win==1&&saw_start==2&&saw_death==5);
    b19_restart(&g);assert(g.state==B19_PLAYING&&g.kills==0);
    for(int i=0;i<1500&&g.state==B19_PLAYING;i++)b19_tick(&g,.02f);
    assert(g.state==B19_LOST&&g.player_hp==0&&g.player_shield==0);
    b19_restart(&g);assert(g.player_hp==100.f);
    puts("PASS B19 native gameplay: miss/cooldown/ray, 2 waves, 5 kills, win/fail/restart, shield, events");
    return 0;
}
