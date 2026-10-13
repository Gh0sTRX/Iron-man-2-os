#include "im2_camera.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>

static void near(float a,float b,float eps){assert(isfinite(a)&&isfinite(b)&&fabsf(a-b)<eps);}
static float rad(float deg){return deg*.017453292519943f;}
static void check(Im2CameraState *s){
    assert(s->initialized && isfinite(s->position.x)&&isfinite(s->position.y)&&isfinite(s->position.z));
    assert(isfinite(s->forward.x)&&isfinite(s->forward.y)&&isfinite(s->forward.z));
    near(sqrtf(s->forward.x*s->forward.x+s->forward.y*s->forward.y+s->forward.z*s->forward.z),1.f,1e-4f);
    near(s->forward.x*s->right.x+s->forward.y*s->right.y+s->forward.z*s->right.z,0.f,1e-4f);
    near(s->up.x*s->right.x+s->up.y*s->right.y+s->up.z*s->right.z,0.f,1e-4f);
    assert(s->shoulder_to_chase>=0.f&&s->shoulder_to_chase<=1.f);
    assert(s->rush_amount>=0.f&&s->rush_amount<=1.f);
    assert(s->fov_deg>=35.f&&s->fov_deg<=105.f);
}
static void repeat(Im2CameraState *s,const Im2CameraConfig *cfg,Im2CameraInput in,int count){
    for(int i=0;i<count;i++){im2_camera_step(s,cfg,&in);check(s);}
}
int main(void){
    Im2CameraConfig cfg;im2_camera_defaults(&cfg);
    Im2CameraState s;im2_camera_init(&s);
    Im2CameraInput in={0};in.player_position=(Im2Vec3){0,12,0};in.delta_seconds=1.f/60.f;
    in.flight_stage=IM2_FLIGHT_HOVER;
    repeat(&s,&cfg,in,90);
    near(s.shoulder_to_chase,0,1e-5f);near(s.fov_deg,64.f,.01f);
    assert(s.position.x>.6f && s.target.x>.39f); /* shoulder view, character left-of-center */
    float original_x=s.position.x;
    in.flight_stage=IM2_FLIGHT_CRUISE;
    im2_camera_step(&s,&cfg,&in);
    assert(s.shoulder_to_chase>0.f&&s.shoulder_to_chase<.2f);
    assert(s.position.x<original_x && s.position.x>0.f); /* no teleport */
    repeat(&s,&cfg,in,90);
    assert(s.shoulder_to_chase>.99f && fabsf(s.position.x)<.02f);
    near(s.fov_deg,72.f,.1f);
    assert(s.current_distance>4.f);
    /* RUSH camera pulls back and widens FOV, still gentle on the first frame. */
    in.flight_stage=IM2_FLIGHT_RUSH;
    float fov_before=s.fov_deg;
    im2_camera_step(&s,&cfg,&in);
    assert(s.fov_deg>fov_before&&s.fov_deg<fov_before+1.f);
    repeat(&s,&cfg,in,110);
    assert(s.rush_amount>.99f);
    near(s.fov_deg,80.f,.1f);
    assert(s.current_distance>5.f);
    /* Returning from rush back to hover does not snap. */
    in.flight_stage=IM2_FLIGHT_HOVER;
    float first_distance=s.current_distance;
    im2_camera_step(&s,&cfg,&in);
    assert(s.current_distance<first_distance && s.current_distance>3.5f);
    repeat(&s,&cfg,in,135);
    near(s.fov_deg,64.f,.05f);
    assert(s.position.x>.65f);
    /* Active right stick keeps freedom to orbit, no forced heading pull. */
    in.flight_stage=IM2_FLIGHT_CRUISE;in.manual_right_stick=1;
    in.character_heading_yaw_rad=rad(120.f);in.camera_input_yaw_rad=rad(25.f);
    repeat(&s,&cfg,in,200);
    near(s.yaw_rad,rad(25.f),.01f);
    in.manual_right_stick=0;
    float yaw_before=s.yaw_rad;
    im2_camera_step(&s,&cfg,&in);
    assert(s.yaw_rad>yaw_before && s.yaw_rad<yaw_before+rad(5.f));
    repeat(&s,&cfg,in,260);
    near(s.yaw_rad,rad(120.f),.01f);
    /* Crossing +/-180 degrees takes shortest path. */
    in.manual_right_stick=1;in.camera_input_yaw_rad=rad(179.f);
    repeat(&s,&cfg,in,100);
    in.camera_input_yaw_rad=rad(-179.f);
    im2_camera_step(&s,&cfg,&in);
    assert(fabsf(s.yaw_rad)>rad(170.f));
    /* Wall clipping is a request to reduce view distance; no raycast is performed. */
    in.camera_input_yaw_rad=0.f;in.wall_hit_distance=1.4f;
    repeat(&s,&cfg,in,120);
    assert(s.safe_distance<1.2f);
    assert(s.current_distance<2.f);
    in.wall_hit_distance=0.f;repeat(&s,&cfg,in,120);
    assert(s.safe_distance>4.f);
    /* Player moving changes both target and position gently. */
    in.player_position.x=20.f;
    float x_before=s.position.x;
    im2_camera_step(&s,&cfg,&in);
    assert(s.position.x>x_before && s.position.x<x_before+4.f);
    repeat(&s,&cfg,in,90);
    assert(fabsf(s.target.x-20.f)<.2f);
    /* Valid flight-physics bank never forces horizon rolling beyond ~1.5 degrees. */
    in.visual_suit_roll_rad=-.523599f;
    repeat(&s,&cfg,in,100);
    assert(fabsf(s.visual_roll_rad)<=.026181f);
    /* Numerically hostile and long time frames must be finite / bounded. */
    in.delta_seconds=INFINITY;in.camera_input_pitch_rad=NAN;in.camera_input_yaw_rad=INFINITY;
    in.visual_suit_roll_rad=INFINITY;
    repeat(&s,&cfg,in,10);
    in.delta_seconds=1234.f;
    repeat(&s,&cfg,in,30);
    /* Deterministic 30/60 Hz end states when input is constant. */
    Im2CameraState a,b;im2_camera_init(&a);im2_camera_init(&b);
    in=(Im2CameraInput){0};in.flight_stage=IM2_FLIGHT_HOVER;in.delta_seconds=1.f/60.f;
    im2_camera_step(&a,&cfg,&in);im2_camera_step(&b,&cfg,&in);
    in.flight_stage=IM2_FLIGHT_CRUISE;in.camera_input_pitch_rad=.2f;
    repeat(&a,&cfg,in,240);
    in.delta_seconds=1.f/30.f;
    repeat(&b,&cfg,in,120);
    near(a.shoulder_to_chase,b.shoulder_to_chase,.0002f);
    near(a.position.y,b.position.y,.001f);
    /* Fuzz input transitions, camera pose and all basis vector guards. */
    uint32_t seed=0x222c2026u;
    for(int i=0;i<20000;i++){
        seed=seed*1664525u+1013904223u;
        in.flight_stage=(Im2FlightStage)(seed%4u);
        in.camera_input_yaw_rad=(float)((int)(seed%6280u)-3140)/1000.f;
        seed=seed*1664525u+1013904223u;
        in.camera_input_pitch_rad=(float)((int)(seed%2200u)-1100)/1000.f;
        in.character_heading_yaw_rad=in.camera_input_yaw_rad*.8f;
        in.manual_right_stick=(int)((seed>>5)&1u);
        in.visual_suit_roll_rad=(float)((int)(seed%1200u)-600)/1000.f;
        in.wall_hit_distance=seed%7u==0u?1.3f:0.f;
        in.player_position.x=(float)(i%400)/10.f;
        in.delta_seconds=i%70==0?NAN:.016f;
        im2_camera_step(&a,&cfg,&in);check(&a);
    }
    puts("PASS B22.3 camera: shoulder->chase->rush, no cut, right-stick orbit, yaw recenter, wall distance, bounded roll, 20k fuzz");
    return 0;
}
