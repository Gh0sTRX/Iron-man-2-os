/* B19 proof-of-logic. Pure C11, no VitaSDK or SDL dependency.
   World and enemies use PROTOTYPE values; authentic assets arrive later. */
#include "b19_gameplay_core.h"
#include <math.h>
#include <string.h>

static B19Vec3 minus(B19Vec3 a, B19Vec3 b) { B19Vec3 v={a.x-b.x,a.y-b.y,a.z-b.z};return v; }
static B19Vec3 addmul(B19Vec3 a, B19Vec3 b, float t) { B19Vec3 v={a.x+t*b.x,a.y+t*b.y,a.z+t*b.z};return v; }
static float dot(B19Vec3 a,B19Vec3 b) {return a.x*b.x+a.y*b.y+a.z*b.z;}
static float norm(B19Vec3 a){return sqrtf(dot(a,a));}
static void emit(B19Game *g,B19EventType type,int id,int amount){
    if(g->events_count<B19_MAX_EVENTS) {
        B19Event e={type,id,amount};g->events[g->events_count++]=e;
    }
}
static void spawn(B19Game *g){
    static const B19Vec3 formation[2][3]={
      {{-2,6,0},{2,7,0},{0,0,0}},
      {{-3,8,1},{3,9,1},{0,10,1}}
    };
    const int count=g->wave==0?2:3;
    memset(g->enemies,0,sizeof g->enemies);
    g->alive=count;
    for(int i=0;i<count;i++){
        B19Enemy *e=&g->enemies[i];e->id=g->wave*10+i+1;
        e->pos=formation[g->wave][i];e->hp=60.f;e->alive=1;
        e->attack_cooldown=1.5f+(float)i*.2f;
    }
    emit(g,B19_EV_WAVE_START,g->wave+1,count);
}
void b19_init(B19Game *g){
    if(!g)return;
    memset(g,0,sizeof *g);g->state=B19_PLAYING;
    g->player_hp=100.f;g->player_shield=25.f;
    spawn(g);
}
void b19_restart(B19Game *g){b19_init(g);}
void b19_set_player_position(B19Game *g,B19Vec3 pos){
    if(g&&isfinite(pos.x)&&isfinite(pos.y)&&isfinite(pos.z))g->player_pos=pos;
}
int b19_pop_event(B19Game *g,B19Event *out){
    if(!g||!out||g->events_count<=0)return 0;
    *out=g->events[0];
    memmove(g->events,g->events+1,(size_t)(--g->events_count)*sizeof(B19Event));
    return 1;
}
void b19_tick(B19Game *g,float dt){
    if(!g||g->state!=B19_PLAYING||!isfinite(dt)||dt<=0.f)return;
    /* Fixed-sized step prevents huge leap on pause; caller supplies a 20 ms tick. */
    if(dt>.05f)dt=.05f;
    g->elapsed+=dt;
    if(g->shot_cooldown>0.f){g->shot_cooldown-=dt;if(g->shot_cooldown<0)g->shot_cooldown=0;}
    for(int i=0;i<B19_MAX_ENEMIES;i++){
        B19Enemy *e=&g->enemies[i];if(!e->alive)continue;
        B19Vec3 delta=minus(g->player_pos,e->pos);float d=norm(delta);
        if(d>4.f && d>.0001f){
            const float movement=fminf(1.8f*dt,d-4.f);
            e->pos=addmul(e->pos,delta,movement/d);
        }
        e->attack_cooldown-=dt;
        if(d<=7.0f && e->attack_cooldown<=0.f){
            const float incoming=8.f;
            const float absorbed=fminf(g->player_shield,incoming);
            g->player_shield-=absorbed;g->player_hp-=incoming-absorbed;
            if(g->player_hp<0)g->player_hp=0;
            emit(g,B19_EV_PLAYER_HIT,e->id,(int)(incoming-absorbed));
            e->attack_cooldown=1.4f;
            if(g->player_hp<=0.f){g->state=B19_LOST;emit(g,B19_EV_MISSION_FAIL,0,0);return;}
        }
    }
}
int b19_fire_repulsor(B19Game *g,B19Vec3 origin,B19Vec3 direction){
    if(!g||g->state!=B19_PLAYING||g->shot_cooldown>0.f)return -1;
    if(!isfinite(direction.x)||!isfinite(direction.y)||!isfinite(direction.z))return -1;
    float len=norm(direction);if(len<.0001f)return -1;
    B19Vec3 dir={direction.x/len,direction.y/len,direction.z/len};
    float closest=10000.f;int best=-1;
    for(int i=0;i<B19_MAX_ENEMIES;i++){
        B19Enemy *e=&g->enemies[i];if(!e->alive)continue;
        B19Vec3 center={e->pos.x,e->pos.y,e->pos.z+1.f};
        B19Vec3 rel=minus(center,origin);float t=dot(rel,dir);
        if(t<0.f||t>18.f||t>=closest)continue;
        float d2=dot(rel,rel)-t*t;
        if(d2<=.8f*.8f){closest=t;best=i;}
    }
    g->shot_cooldown=.2f;emit(g,B19_EV_PLAYER_FIRE,best<0?0:g->enemies[best].id,0);
    if(best<0)return 0;
    B19Enemy *e=&g->enemies[best];e->hp-=30.f;
    emit(g,B19_EV_ENEMY_HIT,e->id,30);
    if(e->hp<=0.f){
        e->hp=0.f;e->alive=0;g->alive--;g->kills++;
        emit(g,B19_EV_ENEMY_DIED,e->id,0);
        if(g->alive==0){
            if(g->wave<1){g->wave++;spawn(g);}
            else {g->state=B19_WON;emit(g,B19_EV_MISSION_WIN,0,g->kills);}
        }
    }
    return e->id;
}
