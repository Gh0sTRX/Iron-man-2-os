#include "im2_flight.h"
#include "im2_camera.h"
#include "im2_thruster.h"
#include "im2_speed_fx.h"
#include "im2_melee_focus.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define FB_STRIDE 496
static uint32_t guarded[(size_t)FB_STRIDE*272u+2u];
static void reset(void){for(size_t i=0;i<(size_t)FB_STRIDE*272u+2u;i++)guarded[i]=0x202020u;
    guarded[0]=0x13572468u;guarded[(size_t)FB_STRIDE*272u+1u]=0x12345678u;}
static void guards(void){assert(guarded[0]==0x13572468u && guarded[(size_t)FB_STRIDE*272u+1u]==0x12345678u);
  for(int y=0;y<272;y++)for(int x=480;x<FB_STRIDE;x++)assert(guarded[1+(size_t)y*FB_STRIDE+(size_t)x]==0x202020u);
  for(int y=70;y<205;y++)for(int x=180;x<300;x++)assert(guarded[1+(size_t)y*FB_STRIDE+(size_t)x]==0x202020u);
}
static int particles_from(const Im2ThrusterState *s,int lo,int hi){
 int n=0;
 for(int i=0;i<IM2_THRUSTER_MAX_PARTICLES;i++){
  if(s->particles[i].active && s->particles[i].socket_id>=lo && s->particles[i].socket_id<hi)n++;
 }
 return n;
}
static void verify_particles(const Im2ThrusterState *s){for(int i=0;i<IM2_THRUSTER_MAX_PARTICLES;i++){
    const Im2ThrusterParticle *p=&s->particles[i];if(!p->active)continue;
    assert(p->socket_id<6 && isfinite(p->position.x)&&isfinite(p->position.y)&&isfinite(p->position.z));
    assert(p->life>.1f&&p->life<1.f&&p->age>=0.f&&p->age<=p->life);
}}
static void near(float a,float b,float eps){assert(isfinite(a)&&isfinite(b)&&fabsf(a-b)<=eps);}
int main(void){
    Im2FlightConfig cfg;im2_flight_defaults(&cfg);
    Im2FlightState fl;im2_flight_init(&fl,(Im2Vec3){0.f,8.f,0.f});
    Im2ThrusterState ts;im2_thruster_init(&ts);
    Im2ThrusterSocket sockets[6]={0};
    for(int k=0;k<6;k++){
        sockets[k].valid=1;sockets[k].model_position=(Im2Vec3){k%2?-.25f:.25f,k<2?.05f:k<4?1.25f:1.8f,k>=4?-.2f:0.f};
        sockets[k].model_exhaust_direction=(Im2Vec3){0.f,k<2?-1.f:0.f,k<2?0.f:-1.f};
    }
    Im2ThrusterOutput t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_GROUND,sockets,IM2_PARTICLE_IM_BLUE,.016f);
    for(int i=0;i<6;i++)assert(!t.enabled[i]);
    assert(t.allowed_particle_count==0);
    for(int i=0;i<130;i++){
       t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_HOVER,sockets,IM2_PARTICLE_IM_BLUE,.016f);
       assert(t.enabled[0] && t.enabled[1]);for(int k=2;k<6;k++)assert(!t.enabled[k]);
    }
    assert(particles_from(&ts,0,2)>0 && particles_from(&ts,2,6)==0);
    for(int i=0;i<90;i++){
      t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_CRUISE,sockets,IM2_PARTICLE_IM_BLUE,.016f);
      for(int k=0;k<4;k++)assert(t.enabled[k]);
      assert(!t.enabled[4]&&!t.enabled[5]);
    }
    assert(particles_from(&ts,2,4)>0 && particles_from(&ts,4,6)==0);
    t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_RUSH,sockets,IM2_PARTICLE_IM_BLUE,.016f);
    assert(t.rush_entry && t.enabled[4] && t.enabled[5] && t.intensity[4]>.85f);
    assert(particles_from(&ts,4,6)==2);
    for(int i=0;i<120;i++){
      t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_RUSH,sockets,IM2_PARTICLE_IM_BLUE,.016f);
      for(int k=0;k<6;k++)assert(t.enabled[k]);
    }
    assert(particles_from(&ts,4,6)>0 && !t.rush_entry && t.allowed_particle_count<=IM2_THRUSTER_MAX_PARTICLES);
    verify_particles(&ts);
    t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_CRUISE,sockets,IM2_PARTICLE_IM_BLUE,0.f);
    assert(!t.enabled[4]&&!t.enabled[5]&&particles_from(&ts,4,6)==0);
    for(int i=0;i<6;i++)sockets[i].valid=(i%2==0);
    t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_RUSH,sockets,IM2_PARTICLE_WM_AMBER,.016f);
    for(int i=0;i<6;i++)assert(t.enabled[i]==(i%2==0));
    verify_particles(&ts);
    t=im2_thruster_step(&ts,&fl,IM2_FLIGHT_GROUND,sockets,IM2_PARTICLE_WM_AMBER,.016f);
    assert(t.allowed_particle_count==0);
    Im2SpeedFx speed;im2_speed_fx_init(&speed);
    im2_speed_fx_step(&speed,IM2_FLIGHT_CRUISE,0,.016f);
    reset();assert(im2_speed_fx_draw(guarded+1,FB_STRIDE,&speed,0)==0);guards();
    im2_speed_fx_step(&speed,IM2_FLIGHT_RUSH,1,.016f);
    assert(speed.enabled && speed.entry_pulse>0.f);
    for(int i=0;i<140;i++){im2_speed_fx_step(&speed,IM2_FLIGHT_RUSH,0,.016f);
      reset();int count=im2_speed_fx_draw(guarded+1,FB_STRIDE,&speed,i&1);assert(count>=8&&count<=20);guards();}
    near(speed.strength,1.f,.001f);
    im2_speed_fx_step(&speed,IM2_FLIGHT_HOVER,0,0.f);
    reset();assert(im2_speed_fx_draw(guarded+1,FB_STRIDE,&speed,0)==0);guards();
    Im2CameraConfig cc;im2_camera_defaults(&cc);
    Im2CameraState base,composed;im2_camera_init(&base);
    Im2CameraInput cin={0};cin.player_position=(Im2Vec3){0.f,0.f,0.f};cin.delta_seconds=1.f/60.f;
    cin.flight_stage=IM2_FLIGHT_GROUND;
    for(int i=0;i<90;i++)im2_camera_step(&base,&cc,&cin);
    Im2CameraState stable_base=base;
    Im2MeleeFocusState ms;im2_melee_focus_init(&ms);
    Im2MeleeFocusInput mi={0};mi.player_head=(Im2Vec3){0,1.6f,0};mi.target_center=(Im2Vec3){0,1.4f,2.7f};
    mi.target_distance=2.7f;mi.attack_active=1;mi.target_alive=1;mi.target_visible=1;
    mi.stage=IM2_FLIGHT_GROUND;mi.delta_seconds=1.f/60.f;
    im2_melee_focus_apply(&ms,&mi,&base,&composed);
    assert(ms.focus>0.f && ms.focus<.25f);
    for(int i=0;i<140;i++)im2_melee_focus_apply(&ms,&mi,&base,&composed);
    assert(ms.focus>.99f && composed.fov_deg>base.fov_deg);
    assert(composed.position.x<base.position.x-.45f);
    assert(composed.target.z>base.target.z);
    assert(memcmp(&base,&stable_base,sizeof(base))==0);
    mi.attack_active=0;for(int i=0;i<150;i++)im2_melee_focus_apply(&ms,&mi,&base,&composed);
    assert(ms.focus<.001f && composed.position.x==base.position.x);
    mi.attack_active=1;mi.target_distance=20.f;
    im2_melee_focus_apply(&ms,&mi,&base,&composed);assert(ms.focus<.001f);
    mi.target_distance=2.7f;mi.stage=IM2_FLIGHT_RUSH;
    for(int i=0;i<90;i++)im2_melee_focus_apply(&ms,&mi,&base,&composed);
    assert(ms.focus<.001f);
    mi.stage=IM2_FLIGHT_HOVER;mi.manual_camera_input=1;
    for(int i=0;i<100;i++)im2_melee_focus_apply(&ms,&mi,&base,&composed);
    near(ms.focus,.4f,.01f);
    mi.target_alive=0;for(int i=0;i<150;i++)im2_melee_focus_apply(&ms,&mi,&base,&composed);
    assert(ms.focus<.001f);
    uint32_t rng=0xa2026beau;
    for(int i=0;i<20000;i++){
        rng=rng*1664525u+1013904223u;
        Im2FlightStage stage=(Im2FlightStage)(rng%4u);
        float dt=i%113==0?NAN:.016f;
        ts.rng=ts.rng?ts.rng:0x1a20beefu;
        t=im2_thruster_step(&ts,&fl,stage,sockets,IM2_PARTICLE_IM_BLUE,dt);
        assert(t.allowed_particle_count>=0 && t.allowed_particle_count<=128);
        assert(stage==IM2_FLIGHT_RUSH || (!t.enabled[4]&&!t.enabled[5]&&particles_from(&ts,4,6)==0));
        verify_particles(&ts);
        im2_speed_fx_step(&speed,stage,t.rush_entry,dt);
        reset();int count=im2_speed_fx_draw(guarded+1,FB_STRIDE,&speed,(int)(rng&1u));
        assert((stage==IM2_FLIGHT_RUSH)||count==0);guards();
        mi.stage=stage;mi.attack_active=(int)((rng>>4)&1u);mi.target_alive=(int)((rng>>5)&1u);
        mi.target_visible=(int)((rng>>6)&1u);mi.target_distance=(float)(rng%120u)/20.f;
        mi.delta_seconds=dt;
        im2_melee_focus_apply(&ms,&mi,&base,&composed);
        assert(isfinite(ms.focus)&&ms.focus>=0.f&&ms.focus<=1.f);
        assert(isfinite(composed.position.x)&&isfinite(composed.position.y)&&isfinite(composed.position.z));
    }
    puts("PASS B22.4-6: Stage1 feet; Stage2 feet+hands; Rush feet+hands+back ONLY, instant back cutoff, bounded particles, center-safe edge streaks, soft melee focus, 20000 fuzz");
}
