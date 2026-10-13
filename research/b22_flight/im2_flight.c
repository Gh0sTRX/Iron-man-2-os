#include "im2_flight.h"
#include <math.h>
#include <stddef.h>

#define IM2_PI 3.14159265358979323846f
#define IM2_TAU (2.f * IM2_PI)

static float fcap(float v, float lo, float hi) {
    if (!isfinite(v)) return 0.f;
    return v < lo ? lo : v > hi ? hi : v;
}
static float fwrap(float a) {
    if (!isfinite(a)) return 0.f;
    return remainderf(a, IM2_TAU);
}
static float smooth_factor(float rate, float dt) {
    return 1.f - expf(-fcap(rate, 0.f, 100.f) * dt);
}
static float approach(float curr, float dest, float rate, float dt) {
    return curr + (dest-curr)*smooth_factor(rate, dt);
}
static float approach_angle(float curr, float dest, float rate, float dt) {
    return fwrap(curr + fwrap(dest-curr)*smooth_factor(rate,dt));
}
static Im2Vec3 vadd(Im2Vec3 a, Im2Vec3 b) {
    Im2Vec3 v={a.x+b.x,a.y+b.y,a.z+b.z}; return v;
}
static Im2Vec3 vscale(Im2Vec3 v,float x) {
    Im2Vec3 out={v.x*x,v.y*x,v.z*x};return out;
}
static float length(Im2Vec3 v) { return sqrtf(v.x*v.x+v.y*v.y+v.z*v.z); }
static Im2Vec3 normalize(Im2Vec3 v) {
    float n=length(v);return n>0.00001f?vscale(v,1.f/n):(Im2Vec3){0.f,0.f,0.f};
}
static Im2Vec3 camera_horizontal(float yaw, float x, float y) {
    Im2Vec3 r={cosf(yaw)*x+sinf(yaw)*y,0.f,-sinf(yaw)*x+cosf(yaw)*y};
    return r;
}
static Im2Vec3 forward_3d(float yaw, float pitch) {
    Im2Vec3 v={sinf(yaw)*cosf(pitch),sinf(pitch),cosf(yaw)*cosf(pitch)};
    return normalize(v);
}
void im2_flight_defaults(Im2FlightConfig *c) {
    if (!c) return;
    *c=(Im2FlightConfig){
      .deadzone=.16f,.cruise_enter=.78f,.cruise_exit=.68f,
      .hover_speed=4.2f,.cruise_speed=15.f,.rush_speed=29.f,
      .hover_accel=9.f,.cruise_accel=7.f,.rush_accel=5.f,
      .yaw_response=6.f,.pose_response=5.5f,.idle_drag=4.f,
      .cruise_roll_rad=.349066f,.rush_roll_rad=.523599f,
      .max_pitch_rad=.523599f,.ground_height=0.f,.altitude_ceiling=120.f
    };
}
void im2_flight_init(Im2FlightState *s,Im2Vec3 initial_position) {
    if (!s)return;
    if (!isfinite(initial_position.x))initial_position.x=0;
    if (!isfinite(initial_position.y))initial_position.y=0;
    if (!isfinite(initial_position.z))initial_position.z=0;
    *s=(Im2FlightState){0};
    s->position=initial_position;
    s->stage=IM2_FLIGHT_GROUND;s->pose=IM2_POSE_GROUND;
}
void im2_flight_step(Im2FlightState *s, const Im2FlightConfig *c,
                     const Im2FlightInput *in) {
    if (!s||!c||!in)return;
    float dt=fcap(in->delta_seconds,0.f,.05f);
    if(dt<=0.f){s->stage_changed=0;return;}
    float x=fcap(in->left_x,-1.f,1.f),y=fcap(in->left_y,-1.f,1.f);
    float yaw=fwrap(in->camera_yaw_rad);
    float pitch=fcap(in->camera_pitch_rad,-c->max_pitch_rad,c->max_pitch_rad);
    float altitude=fcap(in->altitude_axis,-1.f,1.f);
    float stick=sqrtf(x*x+y*y);
    if (stick>1.f) {x/=stick;y/=stick;stick=1.f;}
    if (stick<c->deadzone) {x=0.f;y=0.f;stick=0.f;}
    Im2FlightStage before=s->stage;
    if (!in->airborne) s->stage=IM2_FLIGHT_GROUND;
    else {
        int currently_fast=(s->stage==IM2_FLIGHT_CRUISE||s->stage==IM2_FLIGHT_RUSH);
        float threshold=currently_fast?c->cruise_exit:c->cruise_enter;
        if(stick>=threshold&&y>0.12f)s->stage=in->boost?IM2_FLIGHT_RUSH:IM2_FLIGHT_CRUISE;
        else s->stage=IM2_FLIGHT_HOVER;
    }
    s->stage_changed=(before!=s->stage);
    Im2Vec3 wanted={0.f,0.f,0.f};
    float desired_pitch=0.f,desired_roll=0.f;
    float throttle=0.f;
    if(s->stage==IM2_FLIGHT_GROUND){
        /* Full grounded movement remains owned by B15/B17; never double-integrate it. */
        wanted=(Im2Vec3){0.f,0.f,0.f};
        s->velocity=vscale(s->velocity,expf(-c->idle_drag*dt));
        s->velocity.y=0.f;
        if(s->position.y<c->ground_height)s->position.y=c->ground_height;
    } else if(s->stage==IM2_FLIGHT_HOVER) {
        wanted=camera_horizontal(yaw,x,y);
        wanted=vscale(wanted,c->hover_speed);
        wanted.y=altitude*c->hover_speed*.7f;
        if(stick>.02f)s->heading_yaw_rad=approach_angle(s->heading_yaw_rad,
                                 atan2f(wanted.x,wanted.z),c->yaw_response,dt);
        s->velocity=vadd(s->velocity,vscale((Im2Vec3){wanted.x-s->velocity.x,
                   wanted.y-s->velocity.y,wanted.z-s->velocity.z},
                   smooth_factor(c->hover_accel,dt)));
    } else {
        /* Forward direction follows camera pitch, but analogue steering biases YAW. */
        float bias=atan2f(x,y);
        float target_heading=fwrap(yaw+bias);
        float previous_heading=s->heading_yaw_rad;
        s->heading_yaw_rad=approach_angle(previous_heading,target_heading,c->yaw_response,dt);
        float changed=fwrap(s->heading_yaw_rad-previous_heading);
        float maxbank=s->stage==IM2_FLIGHT_RUSH?c->rush_roll_rad:c->cruise_roll_rad;
        /* Bank in sign of turning, bounded by input and actual yaw rate. */
        float steer_yaw_rate=fcap(changed/dt,-3.f,3.f);
        s->turn_command=fcap((.55f*x+.45f*steer_yaw_rate/2.f),-1.f,1.f);
        desired_roll=-maxbank*s->turn_command;
        desired_pitch=-pitch; /* model +Z forward, right-hand Rx negative noses upward */
        throttle=fcap(stick,.2f,1.f);
        wanted=vscale(forward_3d(s->heading_yaw_rad,pitch),
                    (s->stage==IM2_FLIGHT_RUSH?c->rush_speed:c->cruise_speed)*throttle);
        wanted.y+=altitude*c->hover_speed*.7f;
        float acceleration=s->stage==IM2_FLIGHT_RUSH?c->rush_accel:c->cruise_accel;
        s->velocity=vadd(s->velocity,vscale((Im2Vec3){wanted.x-s->velocity.x,
                        wanted.y-s->velocity.y,wanted.z-s->velocity.z},
                        smooth_factor(acceleration,dt)));
    }
    if(s->stage==IM2_FLIGHT_HOVER || s->stage==IM2_FLIGHT_GROUND)
        s->turn_command=approach(s->turn_command,0.f,c->pose_response,dt);
    s->visual_pitch_rad=approach(s->visual_pitch_rad,desired_pitch,c->pose_response,dt);
    s->visual_roll_rad=approach(s->visual_roll_rad,desired_roll,c->pose_response,dt);
    s->camera_roll_hint_rad=fcap(s->visual_roll_rad*.10f,-.05236f,.05236f);
    float blendtarget=s->stage==IM2_FLIGHT_RUSH?1.f:0.f;
    s->pose_blend=fcap(approach(s->pose_blend,blendtarget,c->pose_response,dt),0.f,1.f);
    s->pose=s->stage==IM2_FLIGHT_GROUND?IM2_POSE_GROUND:
            s->stage==IM2_FLIGHT_HOVER?(stick>.2f?IM2_POSE_AIR_MOVE:IM2_POSE_HOVER):
            s->stage==IM2_FLIGHT_RUSH?IM2_POSE_RUSH:IM2_POSE_FLY_F;
    if (s->stage!=IM2_FLIGHT_GROUND) {
        Im2Vec3 next=vadd(s->position,vscale(s->velocity,dt));
        if (next.y<c->ground_height) {next.y=c->ground_height;if(s->velocity.y<0)s->velocity.y=0.f;}
        if (next.y>c->altitude_ceiling) {next.y=c->altitude_ceiling;if(s->velocity.y>0)s->velocity.y=0.f;}
        s->position=next;
    }
}
static Im2Quat qmul(Im2Quat a, Im2Quat b) {
    Im2Quat q={a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,
               a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x,
               a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w,
               a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z};
    return q;
}
static Im2Quat qaxis(int axis,float angle) {
    float sn=sinf(.5f*angle),co=cosf(.5f*angle);
    if(axis==0)return (Im2Quat){sn,0.f,0.f,co};
    if(axis==1)return (Im2Quat){0.f,sn,0.f,co};
    return (Im2Quat){0.f,0.f,sn,co};
}
Im2Quat im2_flight_orientation(const Im2FlightState *s) {
    if(!s)return (Im2Quat){0,0,0,1};
    Im2Quat a=qmul(qmul(qaxis(1,s->heading_yaw_rad),qaxis(0,s->visual_pitch_rad)),
                   qaxis(2,s->visual_roll_rad));
    float mag=sqrtf(a.x*a.x+a.y*a.y+a.z*a.z+a.w*a.w);
    if(mag<.001f||!isfinite(mag))return (Im2Quat){0,0,0,1};
    return (Im2Quat){a.x/mag,a.y/mag,a.z/mag,a.w/mag};
}
Im2Vec3 im2_flight_rotate(Im2Quat q,Im2Vec3 p) {
    /* Faster unit-quaternion vector transform (q normalized in orientation()). */
    Im2Vec3 u={q.x,q.y,q.z};
    Im2Vec3 t={2.f*(u.y*p.z-u.z*p.y),2.f*(u.z*p.x-u.x*p.z),2.f*(u.x*p.y-u.y*p.x)};
    Im2Vec3 cross={u.y*t.z-u.z*t.y,u.z*t.x-u.x*t.z,u.x*t.y-u.y*t.x};
    return vadd(p,vadd(vscale(t,q.w),cross));
}
Im2Vec3 im2_flight_socket_world(const Im2FlightState *s,Im2Vec3 p) {
    if(!s)return p;
    return vadd(s->position,im2_flight_rotate(im2_flight_orientation(s),p));
}
