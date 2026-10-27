#include "im2_melee_focus.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
static float cap(float x,float lo,float hi){return !isfinite(x)?lo:x<lo?lo:x>hi?hi:x;}
static Im2Vec3 add(Im2Vec3 a,Im2Vec3 b){return (Im2Vec3){a.x+b.x,a.y+b.y,a.z+b.z};}
static Im2Vec3 sub(Im2Vec3 a,Im2Vec3 b){return (Im2Vec3){a.x-b.x,a.y-b.y,a.z-b.z};}
static Im2Vec3 mul(Im2Vec3 v,float t){return (Im2Vec3){v.x*t,v.y*t,v.z*t};}
static float dot(Im2Vec3 a,Im2Vec3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static Im2Vec3 cross(Im2Vec3 a,Im2Vec3 b){return (Im2Vec3){a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
static Im2Vec3 unit(Im2Vec3 x){float n=sqrtf(dot(x,x));return n>1.e-5f?mul(x,1.f/n):(Im2Vec3){0.f,0.f,1.f};}
static int finite_v(Im2Vec3 v){return isfinite(v.x)&&isfinite(v.y)&&isfinite(v.z);}
void im2_melee_focus_init(Im2MeleeFocusState *s){if(s)memset(s,0,sizeof(*s));}
void im2_melee_focus_apply(Im2MeleeFocusState *s,const Im2MeleeFocusInput *in,
                     const Im2CameraState *base,Im2CameraState *out){
    if(!s||!in||!base||!out)return;
    *out=*base;
    float dt=cap(in->delta_seconds,0.f,.05f);
    int stage_allowed=in->stage==IM2_FLIGHT_GROUND||in->stage==IM2_FLIGHT_HOVER;
    int valid=in->attack_active && in->target_alive && in->target_visible &&
           stage_allowed && finite_v(in->player_head) && finite_v(in->target_center) &&
           isfinite(in->target_distance) && in->target_distance>0.f && in->target_distance<=4.5f;
    float desired=valid?(in->manual_camera_input?.40f:1.f):0.f;
    if(dt>0.f)s->focus+= (desired-s->focus)*(1.f-expf(-7.5f*dt));
    s->focus=cap(s->focus,0.f,1.f);
    if(s->focus<.0001f)return;
    /* Player and enemy must both stay visible, favor their midpoint, not hard lock. */
    Im2Vec3 middle=add(mul(in->player_head,.45f),mul(in->target_center,.55f));
    if(!finite_v(middle))return;
    Im2Vec3 shifted_target=add(base->target,mul(sub(middle,base->target),s->focus*.60f));
    /* Shift camera from shoulder toward center, and dolly back slightly in melee. */
    float pull=s->focus*.50f;
    Im2Vec3 position=add(base->position,
        add(mul(base->right,-s->focus*.50f),mul(base->forward,-pull)));
    Im2Vec3 forward=unit(sub(shifted_target,position));
    Im2Vec3 right=unit(cross((Im2Vec3){0.f,1.f,0.f},forward));
    Im2Vec3 up=unit(cross(forward,right));
    out->position=position;out->target=shifted_target;
    out->forward=forward;out->right=right;out->up=up;
    out->fov_deg=cap(base->fov_deg+s->focus*5.f,35.f,105.f);
    out->current_distance=sqrtf(dot(sub(shifted_target,position),sub(shifted_target,position)));
}
