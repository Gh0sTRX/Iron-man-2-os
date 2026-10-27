#include "im2_camera.h"
#include <math.h>
#include <stddef.h>

#define IM2_PI 3.14159265358979323846f
#define IM2_TAU (2.f * IM2_PI)

static float cap(float v, float lo, float hi) {
    if(!isfinite(v))return lo;
    return v<lo?lo:v>hi?hi:v;
}
static float wrap(float a){return isfinite(a)?remainderf(a,IM2_TAU):0.f;}
static float ease(float rate,float dt){return 1.f-expf(-cap(rate,0.f,100.f)*dt);}
static float mix(float from,float to,float a){return from+(to-from)*a;}
static float mix_angle(float from,float to,float a){return wrap(from+wrap(to-from)*a);}
static Im2Vec3 add(Im2Vec3 a,Im2Vec3 b){return (Im2Vec3){a.x+b.x,a.y+b.y,a.z+b.z};}
static Im2Vec3 sub(Im2Vec3 a,Im2Vec3 b){return (Im2Vec3){a.x-b.x,a.y-b.y,a.z-b.z};}
static Im2Vec3 scale(Im2Vec3 a,float s){return (Im2Vec3){a.x*s,a.y*s,a.z*s};}
static float dot(Im2Vec3 a,Im2Vec3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static Im2Vec3 cross(Im2Vec3 a,Im2Vec3 b){
    return (Im2Vec3){a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};
}
static Im2Vec3 unit(Im2Vec3 a){float n=sqrtf(dot(a,a));return n>1.e-5f?scale(a,1.f/n):(Im2Vec3){0.f,0.f,1.f};}
static float safe_position(float x){return isfinite(x)?cap(x,-100000.f,100000.f):0.f;}
void im2_camera_defaults(Im2CameraConfig *c){
    if(!c)return;
    *c=(Im2CameraConfig){
        .shoulder_right_offset=.72f,.shoulder_aim_offset=.42f,
        .shoulder_distance=3.15f,.cruise_distance=4.65f,.rush_distance=5.85f,
        .shoulder_lift=.25f,.cruise_lift=.55f,.rush_lift=.75f,
        .shoulder_fov_deg=64.f,.cruise_fov_deg=72.f,.rush_fov_deg=80.f,
        .anchor_head_height=1.55f,
        .transition_rate=6.f,.follow_rate=11.f,.yaw_follow_rate=2.6f,
        .min_wall_distance=.75f,.wall_padding=.25f,
        .pitch_limit_rad=.95f,.camera_roll_fraction=.06f,.max_camera_roll_rad=.02618f
    };
}
void im2_camera_init(Im2CameraState *s){
    if(!s)return;
    *s=(Im2CameraState){0};s->forward=(Im2Vec3){0.f,0.f,1.f};
    s->right=(Im2Vec3){1.f,0.f,0.f};s->up=(Im2Vec3){0.f,1.f,0.f};
}
void im2_camera_step(Im2CameraState *s,const Im2CameraConfig *c,const Im2CameraInput *in){
    if(!s||!c||!in)return;
    float dt=cap(in->delta_seconds,0.f,.05f);
    if(dt==0.f&&s->initialized)return;
    float yaw_input=wrap(in->camera_input_yaw_rad);
    float pitch=cap(in->camera_input_pitch_rad,-c->pitch_limit_rad,c->pitch_limit_rad);
    int stage=(int)in->flight_stage;
    int chasing=(stage==IM2_FLIGHT_CRUISE||stage==IM2_FLIGHT_RUSH);
    int rushing=stage==IM2_FLIGHT_RUSH;
    float transition=ease(c->transition_rate,dt);
    float position_a=ease(c->follow_rate,dt);
    if(!s->initialized){
        s->yaw_rad=yaw_input;s->pitch_rad=pitch;
        s->shoulder_to_chase=chasing?1.f:0.f;
        s->rush_amount=rushing?1.f:0.f;
        s->initialized=1;
        position_a=1.f;
    }
    s->shoulder_to_chase=mix(s->shoulder_to_chase,chasing?1.f:0.f,transition);
    s->rush_amount=mix(s->rush_amount,rushing?1.f:0.f,transition);
    s->pitch_rad=mix(s->pitch_rad,pitch,ease(c->follow_rate,dt));
    /* No hidden mutations of the B15/B22 flight heading; this is visual camera only.
       Manual right-stick mode keeps the input orbit yaw. When released, the chase
       camera gently aligns behind the suit. Shoulder camera retains orbit yaw. */
    float desired_yaw=yaw_input;
    if(chasing && !in->manual_right_stick && isfinite(in->character_heading_yaw_rad))
        desired_yaw=wrap(in->character_heading_yaw_rad);
    float yaw_rate=chasing&&!in->manual_right_stick?c->yaw_follow_rate:c->follow_rate;
    s->yaw_rad=mix_angle(s->yaw_rad,desired_yaw,ease(yaw_rate,dt));
    float chase=s->shoulder_to_chase,rush=s->rush_amount;
    float lateral=c->shoulder_right_offset*(1.f-chase);
    float aim=c->shoulder_aim_offset*(1.f-chase);
    float distance=mix(c->shoulder_distance,c->cruise_distance,chase)+
        (c->rush_distance-c->cruise_distance)*rush;
    float lift=mix(c->shoulder_lift,c->cruise_lift,chase)+
        (c->rush_lift-c->cruise_lift)*rush;
    float fov=mix(c->shoulder_fov_deg,c->cruise_fov_deg,chase)+
        (c->rush_fov_deg-c->cruise_fov_deg)*rush;
    /* This hit distance is supplied by FUTURE scene raycasts; no level collision
       or occlusion query is implemented in this stand-alone camera module. */
    if(isfinite(in->wall_hit_distance) && in->wall_hit_distance>0.f)
        distance=fminf(distance,fmaxf(c->min_wall_distance,in->wall_hit_distance-c->wall_padding));
    s->safe_distance=distance;
    float cy=cosf(s->yaw_rad),sy=sinf(s->yaw_rad);
    float cp=cosf(s->pitch_rad),sp=sinf(s->pitch_rad);
    Im2Vec3 orbit_right={cy,0.f,-sy};
    Im2Vec3 orbit_forward={sy*cp,sp,cy*cp};
    Im2Vec3 anchor={safe_position(in->player_position.x),
        safe_position(in->player_position.y)+c->anchor_head_height,
        safe_position(in->player_position.z)};
    Im2Vec3 target=add(anchor,scale(orbit_right,aim));
    Im2Vec3 desired_pos=add(add(anchor,scale(orbit_right,lateral)),
                    add((Im2Vec3){0.f,lift,0.f},scale(orbit_forward,-distance)));
    if(position_a>=1.f){s->position=desired_pos;s->target=target;}
    else {
        s->position=add(s->position,scale(sub(desired_pos,s->position),position_a));
        s->target=add(s->target,scale(sub(target,s->target),position_a));
    }
    /* Orientation ALWAYS points toward the smoothed target, not rigidly +camera yaw. */
    s->forward=unit(sub(s->target,s->position));
    Im2Vec3 world_up={0.f,1.f,0.f};
    s->right=unit(cross(world_up,s->forward));
    s->up=unit(cross(s->forward,s->right));
    float bank=cap(in->visual_suit_roll_rad,-1.f,1.f);
    float desired_roll=cap(bank*c->camera_roll_fraction,-c->max_camera_roll_rad,c->max_camera_roll_rad);
    s->visual_roll_rad=mix(s->visual_roll_rad,desired_roll,transition);
    float sn=sinf(s->visual_roll_rad),co=cosf(s->visual_roll_rad);
    Im2Vec3 r=s->right,u=s->up;
    s->right=add(scale(r,co),scale(u,sn));
    s->up=add(scale(u,co),scale(r,-sn));
    s->fov_deg=cap(fov,35.f,105.f);
    s->current_distance=sqrtf(dot(sub(s->target,s->position),sub(s->target,s->position)));
}
