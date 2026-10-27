#ifndef B24_G87_TRANSITION_EVENTS_H
#define B24_G87_TRANSITION_EVENTS_H
#include "b24_g83_unified_movement_aim.h"
/* G87: Event adapter, NOT an original iOS input protocol decoder.
 * The existing B14 world remains the only physics owner. G83/G8 remain the
 * animation selection and IM2V playback owners. No hit/damage events here. */
typedef struct {
 B24G83Mode previous;
 unsigned initialized;
 unsigned saw_stage2_flight;
 unsigned pending_landing;
} B24G87TransitionState;
void b24_g87_transition_reset(B24G87TransitionState *state);
B24G83Event b24_g87_transition_tick(B24G87TransitionState *state,
 B24G83Mode current,int original_floor_contact_verified,int paused);
#endif
