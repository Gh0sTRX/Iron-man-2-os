#ifndef B24_G11_PRACTICE_MELEE_FEEDBACK_H
#define B24_G11_PRACTICE_MELEE_FEEDBACK_H
#include "b24_g10_practice_target.h"
#include <stdint.h>
typedef struct {
 uint32_t last_hit_ms,flash_until_ms;
 unsigned successful_hits,whiffs;
 int ever_hit;
} B24G11PracticeMeleeFeedback;
/* B16 prototype legacy dummy coords are NOT the true GPU practice actor.
   Feedback only touches the actual 3D test actor, never HP or mission flags.
   Can register hits to invulnerable actor but never removes actor. */
int b24_g11_practice_melee_hit(B24G11PracticeMeleeFeedback *st,
 const B24G10PracticeTarget *t,
 float player_x,float player_y,float player_z,
 uint32_t now_ms,int square_edge,int on_ground);
float b24_g11_practice_hit_flash(const B24G11PracticeMeleeFeedback *st,
 uint32_t now_ms);
#endif
