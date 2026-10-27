#ifndef B24_G83_AUTHENTIC_TIMED_ROUTER_H
#define B24_G83_AUTHENTIC_TIMED_ROUTER_H
#include "b24_g83_unified_movement_aim.h"
#include <stdint.h>
/* Source 2010 authored duration edges, not guessed hit frame windows.
 * External game camera/movement remains owned by old B14.
 * The G8 original IM2V stream is the renderer: this only holds/chooses
 * the animation stem until the source-authored duration has elapsed. */
typedef struct {
 B24G83Selection pinned;
 uint32_t pinned_since_ms;
 uint32_t completed_one_shots;
 uint32_t interrupted_one_shots; /* original duration not reached: mode/rig/event preemption */
 B24G83Mode pinned_mode;      /* B14 motion owner at one-shot start */
 int pinned_suit_index;       /* prevent a Mark VI clip leaking to WM or another suit */
 int has_pinned_one_shot;
} B24G83Timeline;
void b24_g83_timeline_reset(B24G83Timeline *state);
int b24_g83_timeline_tick(B24G83Timeline *state,
 B24G82Combat *combat, uint32_t gameplay_ms,
 const B24G83Input *input, B24G83Selection *selected);
#endif
