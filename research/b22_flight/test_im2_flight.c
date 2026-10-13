#include "im2_flight.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>

#define ABS(v) fabsf((v))
static void close_to(float a,float b,float eps){assert(isfinite(a)&&isfinite(b)&&ABS(a-b)<=eps);}
static int finite_state(const Im2FlightState *s){
    return isfinite(s->position.x)&&isfinite(s->position.y)&&isfinite(s->position.z)&&
           isfinite(s->velocity.x)&&isfinite(s->velocity.y)&&isfinite(s->velocity.z)&&
           isfinite(s->heading_yaw_rad)&&isfinite(s->visual_pitch_rad)&&
           isfinite(s->visual_roll_rad)&&isfinite(s->camera_roll_hint_rad)&&
           s->pose_blend>=0.f&&s->pose_blend<=1.f;
}
static void run(Im2FlightState *s,const Im2FlightConfig *cfg,Im2FlightInput in,int frames){
    for(int i=0;i<frames;i++){im2_flight_step(s,cfg,&in);assert(finite_state(s));}
}
int main(void){
    Im2FlightConfig cfg;im2_flight_defaults(&cfg);
    Im2FlightState s;im2_flight_init(&s,(Im2Vec3){0.f,20.f,0.f});
    assert(s.stage==IM2_FLIGHT_GROUND && s.pose==IM2_POSE_GROUND);
    Im2FlightInput input={0};input.airborne=1;input.left_y=.50f;input.delta_seconds=1.f/60.f;
    run(&s,&cfg,input,120);
    assert(s.stage==IM2_FLIGHT_HOVER && s.position.z>1.f && ABS(s.position.y-20.f)<.0001f);
    input.left_y=1.f;input.camera_pitch_rad=.30f;
    float ybefore=s.position.y;
    run(&s,&cfg,input,150);
    assert(s.stage==IM2_FLIGHT_CRUISE && s.pose==IM2_POSE_FLY_F);
    assert(s.position.y>ybefore+2.f && s.position.z>10.f);
    assert(s.visual_pitch_rad<-.28f && ABS(s.visual_roll_rad)<.001f);
    /* Downward-looking camera with forward stick must descend physically. */
    input.camera_pitch_rad=-.30f;
    float ypeak=s.position.y;
    run(&s,&cfg,input,190);
    assert(s.position.y<ypeak-2.f);
    /* Banking direction / continuous yaw and actual world X motion. */
    input.camera_pitch_rad=0.f;input.left_x=.36f;input.left_y=.92f;
    float xbefore=s.position.x;
    run(&s,&cfg,input,90);
    assert(s.position.x>xbefore+2.f && s.visual_roll_rad<-.01f);
    assert(ABS(s.visual_roll_rad)<=cfg.cruise_roll_rad+0.0001f);
    assert(ABS(s.camera_roll_hint_rad)<=.05237f);
    Im2Vec3 socket=im2_flight_socket_world(&s,(Im2Vec3){.5f,1.4f,.2f});
    assert(isfinite(socket.x)&&isfinite(socket.y)&&isfinite(socket.z));
    Im2Quat q=im2_flight_orientation(&s);
    close_to(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w,1.f,.0001f);
    /* Boost follows same steering physics, but bigger bounded bank. */
    input.boost=1;
    run(&s,&cfg,input,180);
    assert(s.stage==IM2_FLIGHT_RUSH && s.pose==IM2_POSE_RUSH && s.pose_blend>.99f);
    assert(ABS(s.visual_roll_rad)<=cfg.rush_roll_rad+.0001f);
    input.boost=0;input.left_x=0.f;input.left_y=1.f;
    run(&s,&cfg,input,180);
    assert(s.stage==IM2_FLIGHT_CRUISE && ABS(s.visual_roll_rad)<.003f && s.pose_blend<.01f);
    /* Toggle cruise-to-hover with hysteresis. */
    input.left_y=.72f;im2_flight_step(&s,&cfg,&input);assert(s.stage==IM2_FLIGHT_CRUISE);
    input.left_y=.62f;im2_flight_step(&s,&cfg,&input);assert(s.stage==IM2_FLIGHT_HOVER);
    input.left_y=.72f;im2_flight_step(&s,&cfg,&input);assert(s.stage==IM2_FLIGHT_HOVER);
    input.left_y=.90f;im2_flight_step(&s,&cfg,&input);assert(s.stage==IM2_FLIGHT_CRUISE);
    /* Simulate ceiling / floor & inability to pass either plane. */
    cfg.altitude_ceiling=23.f;s.position.y=22.9f;
    input.camera_pitch_rad=.52f;
    run(&s,&cfg,input,180);
    close_to(s.position.y,23.f,.0001f);
    input.camera_pitch_rad=-.52f;
    run(&s,&cfg,input,500);
    assert(s.position.y>=cfg.ground_height && s.position.y<=23.f);
    close_to(s.position.y,cfg.ground_height,.0001f);
    input.airborne=0;
    float before=s.position.z;
    run(&s,&cfg,input,40);
    assert(s.stage==IM2_FLIGHT_GROUND && s.pose==IM2_POSE_GROUND);
    close_to(s.position.z,before,.0001f); /* ground movement remains B17-owned */
    /* Large delta cannot tunnel, and invalid analog must never corrupt state. */
    input.airborne=1;input.delta_seconds=1000.f;input.left_x=NAN;input.left_y=INFINITY;
    input.camera_pitch_rad=NAN;input.camera_yaw_rad=INFINITY;input.altitude_axis=NAN;
    run(&s,&cfg,input,200);
    assert(s.position.y>=cfg.ground_height && s.position.y<=23.f);
    input.delta_seconds=NAN;input.left_y=1.f;
    Im2Vec3 frozen=s.position;run(&s,&cfg,input,10);
    close_to(s.position.x,frozen.x,0.f);
    close_to(s.position.y,frozen.y,0.f);
    close_to(s.position.z,frozen.z,0.f);
    /* Determinism for identical inputs / initial condition. */
    Im2FlightState a,b;im2_flight_init(&a,(Im2Vec3){3.f,2.f,1.f});
    im2_flight_init(&b,(Im2Vec3){3.f,2.f,1.f});
    input=(Im2FlightInput){.25f,.9f,.2f,.1f,0.f,1,0,1.f/60.f};
    for(int i=0;i<300;i++){
        im2_flight_step(&a,&cfg,&input);im2_flight_step(&b,&cfg,&input);
        close_to(a.position.x,b.position.x,0.f);
        close_to(a.position.y,b.position.y,0.f);
        close_to(a.position.z,b.position.z,0.f);
    }
    /* Both turn directions affect trajectory and bank sign. */
    Im2FlightState left_turn,right_turn;
    im2_flight_init(&left_turn,(Im2Vec3){0.f,12.f,0.f});
    im2_flight_init(&right_turn,(Im2Vec3){0.f,12.f,0.f});
    input=(Im2FlightInput){-.42f,.89f,0.f,0.f,0.f,1,0,1.f/60.f};
    run(&left_turn,&cfg,input,100);
    assert(left_turn.position.x < -2.f && left_turn.visual_roll_rad>0.f);
    input.left_x=.42f;
    run(&right_turn,&cfg,input,100);
    assert(right_turn.position.x > 2.f && right_turn.visual_roll_rad<0.f);
    /* Local +X right wing tilts downward for a right bank. */
    Im2Vec3 wing=im2_flight_rotate(im2_flight_orientation(&right_turn),(Im2Vec3){1.f,0.f,0.f});
    assert(wing.y<0.f);
    /* The model's +Z forward vector noses UP if camera pitch is positive. */
    Im2FlightState nose;im2_flight_init(&nose,(Im2Vec3){0.f,12.f,0.f});
    input=(Im2FlightInput){0.f,1.f,0.f,.45f,0.f,1,0,1.f/60.f};
    run(&nose,&cfg,input,120);
    Im2Vec3 front=im2_flight_rotate(im2_flight_orientation(&nose),(Im2Vec3){0.f,0.f,1.f});
    assert(front.y>.3f && nose.position.y>12.5f);
    /* Yaw angle must select shortest crossing at +/-pi, without 360-degree spins. */
    nose.heading_yaw_rad=3.13f;
    input.camera_yaw_rad=-3.13f;input.camera_pitch_rad=0.f;
    im2_flight_step(&nose,&cfg,&input);
    assert(fabsf(nose.heading_yaw_rad)>3.f);
    /* A 30 FPS / 60 FPS simulation of the same steering has near-equal trajectory. */
    Im2FlightState fps30,fps60;
    im2_flight_init(&fps30,(Im2Vec3){0.f,15.f,0.f});
    im2_flight_init(&fps60,(Im2Vec3){0.f,15.f,0.f});
    input=(Im2FlightInput){.28f,.92f,.18f,.25f,0.f,1,0,1.f/30.f};
    run(&fps30,&cfg,input,120);
    input.delta_seconds=1.f/60.f;
    run(&fps60,&cfg,input,240);
    assert(fabsf(fps30.position.x-fps60.position.x)<.25f);
    assert(fabsf(fps30.position.y-fps60.position.y)<.25f);
    assert(fabsf(fps30.position.z-fps60.position.z)<.25f);
    /* Finite input fuzz and camera orientation safety. */
    uint32_t rng=0x203005afU;
    for(int i=0;i<20000;i++){
        rng=rng*1664525U+1013904223U;
        float t=(float)(rng%201U)/100.f-1.f;
        input.left_x=t;
        rng=rng*1664525U+1013904223U;
        input.left_y=(float)(rng%201U)/100.f-1.f;
        input.camera_yaw_rad=t*3.f;
        input.camera_pitch_rad=t;
        input.altitude_axis=t;
        input.boost=(int)(rng&1U);
        input.airborne=(int)((rng>>1)&1U);
        input.delta_seconds=i%40==0?INFINITY:.016f;
        im2_flight_step(&a,&cfg,&input);
        assert(finite_state(&a));
        q=im2_flight_orientation(&a);
        close_to(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w,1.f,.0001f);
    }
    puts("PASS B22.2 directional flight: 3 stages, true climb/dive, yaw and bank, smooth return, ceiling/floor, root quaternion, sockets, 20k host fuzz");
    return 0;
}
