#include "im2_thruster.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
static float clampf(float a,float lo,float hi){return !isfinite(a)?lo:a<lo?lo:a>hi?hi:a;}
static Im2Vec3 add(Im2Vec3 a,Im2Vec3 b){return (Im2Vec3){a.x+b.x,a.y+b.y,a.z+b.z};}
static Im2Vec3 mul(Im2Vec3 a,float k){return (Im2Vec3){a.x*k,a.y*k,a.z*k};}
static float norm(Im2Vec3 a){return sqrtf(a.x*a.x+a.y*a.y+a.z*a.z);}
static int finitev(Im2Vec3 a){return isfinite(a.x)&&isfinite(a.y)&&isfinite(a.z);}
static Im2Vec3 unit(Im2Vec3 a){float n=norm(a);return n>1.e-5f?mul(a,1.f/n):(Im2Vec3){0,-1.f,0};}
static uint32_t random32(Im2ThrusterState *s){uint32_t v=s->rng;v^=v<<13;v^=v>>17;v^=v<<5;s->rng=v;return v;}
static float jitter(Im2ThrusterState *s){return (float)(random32(s)&65535u)/65535.f-.5f;}
static void spawn(Im2ThrusterState *s,const Im2FlightState *flight,
                  const Im2ThrusterSocket *socket,int id,Im2ParticleTheme theme,
                  float intensity){
    int index=-1;
    for(int i=0;i<IM2_THRUSTER_MAX_PARTICLES;i++)if(!s->particles[i].active){index=i;break;}
    if(index<0)return; /* fixed memory/cost, never overflow */
    Im2Vec3 pos=im2_flight_socket_world(flight,socket->model_position);
    Im2Vec3 dir=unit(im2_flight_rotate(im2_flight_orientation(flight),socket->model_exhaust_direction));
    if(!finitev(pos)||!finitev(dir))return;
    float speed=(12.f+18.f*intensity)*(1.f+.2f*jitter(s));
    Im2ThrusterParticle *p=&s->particles[index];
    p->active=1;p->position=pos;
    p->velocity=add(mul(dir,speed),mul(flight->velocity,.12f));
    p->age=0.f;p->life=.22f+.13f*intensity+.07f*(jitter(s)+.5f);
    p->size=.045f+.04f*intensity;
    p->socket_id=(uint8_t)id;p->theme=(uint8_t)theme;
}
void im2_thruster_init(Im2ThrusterState *s){
    if(!s)return;
    memset(s,0,sizeof(*s));
    s->rng=0x1a20beefu;
    s->last_stage=IM2_FLIGHT_GROUND;
}
Im2ThrusterOutput im2_thruster_step(Im2ThrusterState *s,
        const Im2FlightState *flight,Im2FlightStage stage,
        const Im2ThrusterSocket sockets[IM2_THRUSTER_SOCKETS],
        Im2ParticleTheme theme,float dt){
    Im2ThrusterOutput out={0};
    if(!s||!flight||!sockets)return out;
    dt=clampf(dt,0.f,.05f);
    int hover=(stage==IM2_FLIGHT_HOVER),cruise=(stage==IM2_FLIGHT_CRUISE),rush=(stage==IM2_FLIGHT_RUSH);
    out.rush_entry=rush&&s->last_stage!=IM2_FLIGHT_RUSH;
    if(out.rush_entry)s->rush_pulse=.18f;
    if(!rush)s->rush_pulse=0.f; /* back vents stop IMMEDIATELY outside RUSH */
    else if(dt>0.f)s->rush_pulse=fmaxf(0.f,s->rush_pulse-dt);
    for(int i=0;i<IM2_THRUSTER_SOCKETS;i++){
        int allow=i<2?(hover||cruise||rush):i<4?(cruise||rush):rush;
        int valid=allow&&sockets[i].valid&&finitev(sockets[i].model_position)&&
            finitev(sockets[i].model_exhaust_direction)&&norm(sockets[i].model_exhaust_direction)>1.e-5f;
        out.enabled[i]=(uint8_t)valid;
        out.intensity[i]=!valid?0.f:(hover?.38f:cruise?.65f:
                         (i>=4?.85f:1.f));
        if(valid&&rush&&s->rush_pulse>0.f)out.intensity[i]=fminf(1.4f,out.intensity[i]+.4f*s->rush_pulse/.18f);
        if(!valid)s->fractional[i]=0.f;
    }
    /* Immediate takeoff / boost event: two real socket-bound flares on entry. */
    if(dt>0.f){
        int launching=(stage!=IM2_FLIGHT_GROUND && s->last_stage==IM2_FLIGHT_GROUND);
        if(launching){
            for(int i=0;i<2;i++)if(out.enabled[i])
                spawn(s,flight,&sockets[i],i,theme,out.intensity[i]);
        }
        if(out.rush_entry){
            for(int i=IM2_BACK_L;i<=IM2_BACK_R;i++)if(out.enabled[i])
                spawn(s,flight,&sockets[i],i,theme,out.intensity[i]);
        }
    }
    /* Explicitly discard forbidden effect particles on stage exit, especially RUSH back jets. */
    for(int i=0;i<IM2_THRUSTER_MAX_PARTICLES;i++){
        Im2ThrusterParticle *p=&s->particles[i];
        if(!p->active)continue;
        if(!out.enabled[p->socket_id]||dt<=0.f){if(!out.enabled[p->socket_id])p->active=0;continue;}
        p->age+=dt;
        if(p->age>=p->life){p->active=0;continue;}
        p->position=add(p->position,mul(p->velocity,dt));
        if(!finitev(p->position))p->active=0;
    }
    if(dt>0.f){
        for(int i=0;i<IM2_THRUSTER_SOCKETS;i++){
            if(!out.enabled[i])continue;
            float rate=hover?9.f:cruise?13.f:(i<4?23.f:15.f);
            s->fractional[i]+=rate*dt;
            while(s->fractional[i]>=1.f){
                spawn(s,flight,&sockets[i],i,theme,out.intensity[i]);
                s->fractional[i]-=1.f;
            }
        }
    }
    s->last_stage=stage;
    for(int i=0;i<IM2_THRUSTER_MAX_PARTICLES;i++)out.allowed_particle_count+=!!s->particles[i].active;
    return out;
}
