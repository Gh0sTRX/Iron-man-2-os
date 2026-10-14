#include "b24_hover_pose_blend.h"
#include <assert.h>
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static void check(size_t nv){
    B24HoverPoseBlend b={0};
    assert(b24_hover_pose_blend_init(&b,nv));
    assert(!b24_hover_pose_blend_init(&b,nv));
    const size_t n=nv*3;
    float *old=calloc(n,sizeof(float));
    float *goal=malloc(n*sizeof(float));
    float *out=calloc(n,sizeof(float));
    assert(old&&goal&&out);
    for(size_t i=0;i<n;i++)goal[i]=2.f;
    assert(b24_hover_pose_blend_begin(&b,old,.12f));
    assert(b24_hover_pose_blend_step(&b,goal,out,.03f));
    for(size_t i=0;i<n;i++)assert(out[i]>0.f&&out[i]<2.f);
    assert(b.active);
    /* Direction changes while shooting: no snap back to idle pose. */
    for(size_t i=0;i<n;i++)old[i]=out[i];
    assert(b24_hover_pose_blend_begin(&b,old,.12f));
    assert(b24_hover_pose_blend_step(&b,goal,out,0.f));
    for(size_t i=0;i<n;i++)assert(fabsf(out[i]-old[i])<1e-5f);
    assert(b24_hover_pose_blend_step(&b,goal,out,.06f));
    for(size_t i=0;i<n;i++)assert(out[i]>old[i]&&out[i]<2.f);
    assert(b24_hover_pose_blend_step(&b,goal,out,.08f));
    assert(!b.active);
    for(size_t i=0;i<n;i++)assert(fabsf(out[i]-2.f)<1e-5f);
    assert(b24_hover_pose_blend_step(&b,old,out,0.f));
    assert(memcmp(old,out,n*sizeof(float))==0);
    assert(!b24_hover_pose_blend_begin(&b,old,-.001f));
    assert(!b24_hover_pose_blend_step(&b,goal,out,-.2f));
    goal[n-1]=NAN;
    assert(!b24_hover_pose_blend_step(&b,goal,out,.016f));
    b24_hover_pose_blend_close(&b);
    b24_hover_pose_blend_close(&b);
    free(old);free(goal);free(out);
}
int main(void){
    check(802);check(1292);check(840);
    puts("PASS B24 G8 host hover attack pose XYZ transition: Mark VI 802v,"
         " War Machine 1292v, Underwater 840v, interrupt continuity,"
         " finite/dt guards; NOT YET ATTACHED TO G8 GAME");
    return 0;
}
