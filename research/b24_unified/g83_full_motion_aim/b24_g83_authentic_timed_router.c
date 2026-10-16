#include "b24_g83_authentic_timed_router.h"
#include <string.h>
#include <stddef.h>
void b24_g83_timeline_reset(B24G83Timeline *state){
 if(state)memset(state,0,sizeof(*state));
}
static int is_original_combo(const char *name){
 if(!name)return 0;
 return strstr(name,"ironman_ironman_ground_combo_")!=NULL;
}
int b24_g83_timeline_tick(B24G83Timeline *state,
 B24G82Combat *combat,uint32_t now,
 const B24G83Input *input,B24G83Selection *selected){
 if(!state||!input||!selected)return 0;
 B24G83Selection choice;
 if(!b24_g83_select_combined(combat,now,input,&choice))return 0;
 if(input->paused){
  /* Do not advance motion renderer while B14 world is paused. Caller
   * should pass pause-adjusted game time; no clock advanced here. */
  *selected=choice;
  return 1;
 }
 if(is_original_combo(choice.stem)){
  /* G82 combo uses its own authentic 266/300/500ms phase durations.
   * It ALWAYS preempts old held ranged-shot animation. */
  state->has_pinned_one_shot=0;
  *selected=choice;
  return 1;
 }
 const int contact_transition=
   input->grounded_contact_verified &&
   (input->transition==B24G83_EVENT_FLY_TO_GROUND ||
    input->transition==B24G83_EVENT_FLY_TO_RUN);
 const int urgent_dodge=
   input->transition==B24G83_EVENT_DODGE_LEFT||
   input->transition==B24G83_EVENT_DODGE_RIGHT;
 if(state->has_pinned_one_shot &&
     (uint32_t)(now-state->pinned_since_ms)<state->pinned.original_source_duration_ms &&
     !contact_transition&&!urgent_dodge){
  *selected=state->pinned;
  /* A held original pose is NOT a second accepted fire/damage event.
   * Keep B16/2010 shots exclusively on their already verified edge. */
  selected->needs_2010_hit_event=0;
  return 1;
 }
 if(state->has_pinned_one_shot)state->completed_one_shots++;
 state->has_pinned_one_shot=0;
 if(choice.stem&&choice.one_shot_not_looping&&
    !is_original_combo(choice.stem)){
  if(!choice.original_source_duration_ms)return 0;
  state->pinned=choice;
  state->pinned_since_ms=now;
  state->has_pinned_one_shot=1;
 }
 *selected=choice;
 return 1;
}
