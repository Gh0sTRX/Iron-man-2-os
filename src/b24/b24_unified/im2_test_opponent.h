#ifndef IM2_TEST_OPPONENT_H
#define IM2_TEST_OPPONENT_H
#include "b16_action.h"
#include "b24_g75_source_capsule.h"
#include <stdint.h>
/* Owner-authorized MARK IV TEST OPPONENT. Prototype HP/AI, NOT native NPC. */
typedef enum {IM2_TEST_IDLE,IM2_TEST_HURT,IM2_TEST_ATTACK,IM2_TEST_DOWN} Im2TestPhase;
typedef struct {
 B16TestTarget target;
 float x,y,z,heading,player_hp;
 uint32_t phase_since,attack_since;unsigned observed_hits,attacks;
 Im2TestPhase phase;int spawned,attack_clock_set,player_occluded;
} Im2TestOpponent;
void im2_test_opponent_reset(Im2TestOpponent *s);
int im2_test_opponent_spawn(Im2TestOpponent *s,const B24C1OriginalCollision *city,
                            float player_x,float player_y,float player_z,float heading,uint32_t now);
void im2_test_opponent_tick(Im2TestOpponent *s,float player_x,float player_y,float player_z,uint32_t now,int paused);
void im2_test_opponent_animation_done(Im2TestOpponent *s,uint32_t now);
/* Test combat visibility uses original collision triangles, never hidden targets. */
int im2_test_segment_blocked(const B24C1OriginalCollision *city,const float a[3],const float b[3]);
#endif
