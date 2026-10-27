#include "b24_camera_recenter.h"
#include <math.h>
#include <stddef.h>
static float clipped(float x,float lo,float hi){return x<lo?lo:x>hi?hi:x;}
float b24_camera_recenter(B24CameraRecenter *s,int stage,float dt,
        float rx,float ry,float orbit,float heading){
    if(!s)return orbit;
    if(!isfinite(dt)||dt<0.f)dt=0.f;
    if(dt>.05f)dt=.05f;
    if(!isfinite(orbit)||!isfinite(heading)){s->idle_seconds=0.f;return orbit;}
    /* Do not override aiming or over-the-shoulder behavior on ground/hover. */
    if(stage<2 || stage>3){s->idle_seconds=0.f;return orbit;}
    if(!isfinite(rx)||!isfinite(ry)){s->idle_seconds=0.f;return orbit;}
    if(fabsf(rx)>.13f||fabsf(ry)>.13f){s->idle_seconds=0.f;return orbit;}
    s->idle_seconds=clipped(s->idle_seconds+dt,0.f,10.f);
    if(s->idle_seconds<.65f)return orbit;
    const float diff=atan2f(sinf(heading-orbit),cosf(heading-orbit));
    const float rate=stage==3?3.5f:2.2f;
    return orbit+diff*(1.f-expf(-rate*dt));
}
