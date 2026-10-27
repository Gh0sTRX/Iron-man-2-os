#ifndef B24_HOVER_POSE_BLEND_H
#define B24_HOVER_POSE_BLEND_H
#include <stddef.h>

/* CPU animation crossfade only; genuine per-clip .IM2V source frames drive target.
   This is a NEW transition heuristic, not the recovered 2010 transition graph.
   No GL, no physics, no reallocation in the animation frame loop. */
typedef struct {
    float *previous_xyz;
    size_t vertices;
    float elapsed_seconds;
    float duration_seconds;
    int active;
} B24HoverPoseBlend;

int b24_hover_pose_blend_init(B24HoverPoseBlend *b, size_t vertices);
int b24_hover_pose_blend_begin(B24HoverPoseBlend *b,
                              const float *last_presented_xyz, float seconds);
int b24_hover_pose_blend_step(B24HoverPoseBlend *b, const float *target_xyz,
                             float *out_xyz, float delta_seconds);
void b24_hover_pose_blend_close(B24HoverPoseBlend *b);
#endif
