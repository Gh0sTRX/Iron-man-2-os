#include "b24_g87_transition_events.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 B24G87TransitionState s={0};
 #define T(mode,contact,paused,event) \
  assert(b24_g87_transition_tick(&s,mode,contact,paused)==event)
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 T(B24G83_HOVER,0,0,B24G83_EVENT_GROUND_TO_HOVER);
 T(B24G83_HOVER,0,0,B24G83_EVENT_NONE);
 T(B24G83_FLIGHT,0,0,B24G83_EVENT_FLY_START);
 T(B24G83_RUSH,0,0,B24G83_EVENT_NONE);
 T(B24G83_HOVER,0,0,B24G83_EVENT_FLY_STOP);
 T(B24G83_FLIGHT,0,0,B24G83_EVENT_FLY_START);
 /* Real G75 B14 can drop flying ahead of touching the authored surface. */
 T(B24G83_GROUND,0,0,B24G83_EVENT_NONE);
 assert(s.pending_landing);
 T(B24G83_GROUND,0,0,B24G83_EVENT_NONE);
 T(B24G83_GROUND,1,1,B24G83_EVENT_NONE); /* pause cannot consume */
 assert(s.pending_landing);
 T(B24G83_GROUND,1,0,B24G83_EVENT_FLY_TO_GROUND);
 assert(!s.pending_landing);
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 /* A hover-only excursion must not claim the flight-to-ground clip. */
 b24_g87_transition_reset(&s);
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 T(B24G83_HOVER,0,0,B24G83_EVENT_GROUND_TO_HOVER);
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 /* A failed landing is invalidated by a second takeoff. */
 b24_g87_transition_reset(&s);
 T(B24G83_FLIGHT,0,0,B24G83_EVENT_NONE);
 T(B24G83_GROUND,0,0,B24G83_EVENT_NONE);
 assert(s.pending_landing);
 T(B24G83_HOVER,0,0,B24G83_EVENT_GROUND_TO_HOVER);
 assert(!s.pending_landing);
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 /* Illegal states and paused inputs must not rewrite previous mode. */
 T((B24G83Mode)999,1,0,B24G83_EVENT_NONE);
 T(B24G83_FLIGHT,0,1,B24G83_EVENT_NONE);
 T(B24G83_GROUND,1,0,B24G83_EVENT_NONE);
 puts("PASS G87 one B14 transition edge per physical mode change; original sourced polygon contact only, no fake grounded landing, pause/reset/re-takeoff regression, NO VPK");
 return 0;
}
