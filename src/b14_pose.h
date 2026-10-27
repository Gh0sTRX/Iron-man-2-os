#ifndef B14_POSE_H
#define B14_POSE_H
#include "b7_anim.h"
#include "b13_motion.h"
typedef enum {B14_IDLE,B14_WALK,B14_RUN,B14_HOVER,B14_FLY,B14_RUSH1,B14_RUSH6,B14_RUSH12,B14_RUSHFULL,B14_LAND,B14_DRIFT} B14Mode;
typedef struct {float *from;unsigned nverts,clip_start,fade_start;int last_mode;unsigned changes;} B14Pose;
int b14_pose_init(B14Pose *p,const IM2Model *model);
void b14_pose_free(B14Pose *p);
B14Mode b14_pose_pick(const B13Motion *adv,int flying,int moving,int boost,int landing,unsigned rush_elapsed);
B14Mode b15_pose_pick(const B13Motion*,int flying,int moving,int flight_stage,int boost,int landing,unsigned rush_elapsed);
int b14_pose_tick(B14Pose *p,IM2Model *model,const B7Motion *base,const B13Motion *adv,B14Mode state,unsigned now_ms);
int b14_pose_tick_ex(B14Pose *p,IM2Model *model,const B7Motion *base,const B13Motion *adv,B14Mode state,unsigned now_ms,const B13Clip *override);
#endif
