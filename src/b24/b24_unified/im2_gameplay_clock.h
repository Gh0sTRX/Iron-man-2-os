#ifndef IM2_GAMEPLAY_CLOCK_H
#define IM2_GAMEPLAY_CLOCK_H
#include <stdint.h>
/* One pause-adjusted timestamp for existing action/animation owners. Raw frame
 * timing and SDL observations stay separate; authored clip rates are unchanged. */
typedef struct {uint32_t wall_ms,game_ms;int initialized,was_paused;} Im2GameplayClock;
static inline uint32_t im2_gameplay_clock_tick(Im2GameplayClock *c,uint32_t wall_ms,int paused){
 paused=!!paused;
 if(!c->initialized){
  c->wall_ms=c->game_ms=wall_ms;c->initialized=1;c->was_paused=paused;
  return c->game_ms;
 }
 const uint32_t elapsed=wall_ms-c->wall_ms;
 c->wall_ms=wall_ms;
 /* Both transition frames retain the presented pose. The world was still
  * paused at frame start on resume; no paused interval may enter clip age. */
 if(!paused&&!c->was_paused)c->game_ms+=elapsed;
 c->was_paused=paused;
 return c->game_ms;
}
#endif
