#include "b24_g87_transition_events.h"
#include <string.h>
void b24_g87_transition_reset(B24G87TransitionState *state){
 if(state)memset(state,0,sizeof(*state));
}
B24G83Event b24_g87_transition_tick(B24G87TransitionState *s,
 B24G83Mode current,int original_floor_contact_verified,int paused){
 if(!s||(unsigned)current>(unsigned)B24G83_RUSH||paused)
  return B24G83_EVENT_NONE;
 if(!s->initialized){
  s->initialized=1;
  s->previous=current;
  s->saw_stage2_flight=(unsigned)(current>=B24G83_FLIGHT);
  return B24G83_EVENT_NONE; /* Startup/armor change cannot fake takeoff */
 }
 B24G83Mode prior=s->previous;
 B24G83Event event=B24G83_EVENT_NONE;
 s->previous=current;
 if(current!=B24G83_GROUND){
  /* A new takeoff cancels any old, never-finished landing request. */
  s->pending_landing=0;
  if(prior==B24G83_GROUND){
   s->saw_stage2_flight=0;
   event=current==B24G83_HOVER?
    B24G83_EVENT_GROUND_TO_HOVER:B24G83_EVENT_FLY_START;
  }else if(prior==B24G83_HOVER&&current>=B24G83_FLIGHT){
   event=B24G83_EVENT_FLY_START;
  }else if(prior>=B24G83_FLIGHT&&current==B24G83_HOVER){
   event=B24G83_EVENT_FLY_STOP;
  }
  if(current>=B24G83_FLIGHT)s->saw_stage2_flight=1;
 }else{
  if(prior!=B24G83_GROUND&&s->saw_stage2_flight)
   s->pending_landing=1;
  /* B14 sets flying=false before its Z has reached the floor.
   * Only the original C1L1 polygon's verified foot-contact may release
   * Fly2Ground. Merely turning flight OFF is never landing proof. */
  if(s->pending_landing&&original_floor_contact_verified){
   event=B24G83_EVENT_FLY_TO_GROUND;
   s->pending_landing=0;
   s->saw_stage2_flight=0;
  }
  if(prior!=B24G83_GROUND&&!s->pending_landing)
   s->saw_stage2_flight=0;
 }
 return event;
}
