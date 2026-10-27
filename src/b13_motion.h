#ifndef IM2_B13_MOTION_H
#define IM2_B13_MOTION_H
#include "renderer.h"
#include <stdint.h>

/* Authentic original iOS .anim bone poses prebaked to textured Vita mesh coordinates.
   B13 is independently authored control/state selection; not the original game engine. */
enum {B13_GROUND_IDLE, B13_WALK, B13_RUN, B13_FLY_NORMAL, B13_RUSH01,
      B13_RUSH06, B13_RUSH12, B13_RUSH_FULL, B13_FLY_START, B13_FLY_END,
      B13_FLOAT_MOVE, B13_AIR_MOVE, B13_COUNT};
typedef struct {float *xyz;uint32_t verts,frames,fps,duration_ms;} B13Clip;
typedef struct {B13Clip clips[B13_COUNT];uint32_t nverts;int armor;int previous_state;
                unsigned state_started;float *transition_from; } B13Motion;
int b13_prepare(B13Motion *s,int armor,const IM2Model *model);
void b13_release(B13Motion *s);
/* Return 1 if this state has authored B13 motion; otherwise keep B9 baseline pose.
  boost selects running on ground / faster pose in flight.  fire_aim_ms inhibits non-aim
  ground walking to avoid losing original raised-arm aim pose during combat. */
int b13_apply(B13Motion *s,IM2Model *model,int flying,int moving,int landing,int boost,
              int aiming,unsigned now_ms,unsigned flight_begin_ms);
#endif
