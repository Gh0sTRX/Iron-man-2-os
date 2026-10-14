#include "b24_hover_pose_blend.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

/* Separate from original .im2v keyframe interpolation and any hit/shot events.
   Only interpolates already-decoded XYZ positions for SAME original topology;
   per-vertex UV and original triangles stay unchanged in GPU renderer. */
static int finite_xyz(const float *a,size_t n) {
    if (!a) return 0;
    for (size_t i=0;i<n*3;i++) if (!isfinite(a[i])) return 0;
    return 1;
}
int b24_hover_pose_blend_init(B24HoverPoseBlend *b,size_t vertices) {
    if (!b||b->previous_xyz||vertices<3||vertices>16000)return 0;
    float *p=(float *)calloc(vertices*3,sizeof(float));
    if (!p)return 0;
    b->previous_xyz=p;b->vertices=vertices;
    b->elapsed_seconds=0;b->duration_seconds=0;b->active=0;
    return 1;
}
int b24_hover_pose_blend_begin(B24HoverPoseBlend *b,
                              const float *last_presented_xyz,float seconds) {
    if (!b||!b->previous_xyz||!b->vertices||
        !isfinite(seconds)||seconds<0.f||seconds>.8f||
        !finite_xyz(last_presented_xyz,b->vertices))return 0;
    /* Capture PREVIOUS PRESENTED pose, not the previous clip's initial pose.
       This matters for L -> L_Att -> R_Att interruptions mid-crossfade. */
    memcpy(b->previous_xyz,last_presented_xyz,b->vertices*3*sizeof(float));
    b->elapsed_seconds=0.f;
    b->duration_seconds=seconds;
    b->active=seconds>0.f;
    return 1;
}
int b24_hover_pose_blend_step(B24HoverPoseBlend *b,const float *target_xyz,
                             float *out_xyz,float dt) {
    if (!b||!b->previous_xyz||!out_xyz||!isfinite(dt)||
        dt<0.f||dt>.5f||!finite_xyz(target_xyz,b->vertices))return 0;
    if (!b->active) {
        memmove(out_xyz,target_xyz,b->vertices*3*sizeof(float));
        return 1;
    }
    b->elapsed_seconds=fminf(b->duration_seconds,b->elapsed_seconds+dt);
    float t=b->elapsed_seconds/b->duration_seconds;
    /* bounded smootherstep: endpoint velocity zero without an inertial pop */
    float alpha=t*t*(3.f-2.f*t);
    for(size_t i=0;i<b->vertices*3;i++)
        out_xyz[i]=b->previous_xyz[i]*(1.f-alpha)+target_xyz[i]*alpha;
    if (b->elapsed_seconds>=b->duration_seconds)b->active=0;
    return 1;
}
void b24_hover_pose_blend_close(B24HoverPoseBlend *b) {
    if(!b)return;
    free(b->previous_xyz);
    memset(b,0,sizeof(*b));
}
