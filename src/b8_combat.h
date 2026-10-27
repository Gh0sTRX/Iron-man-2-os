#ifndef IRONMAN_B8_COMBAT_H
#define IRONMAN_B8_COMBAT_H
#include <stdint.h>

/* Deliberately limited target-range prototype. Hits are assessed in 2-D screen
 * space; this is NOT the 2010 game's 3-D weapon/collision engine. */
typedef struct {
    float aim_x, aim_y, flash_time, beam_time, cooldown;
    float beam_x, beam_y, hit_x, hit_y;
    unsigned hits, shots, stage;
    int last_hit, completed;
} B8Combat;
void b8_init(B8Combat *c);
void b8_update(B8Combat *c,float delta,float x_axis,float y_axis);
int b8_fire(B8Combat *c);
void b8_draw(uint32_t *out,const B8Combat *c);
void b8_get_target(const B8Combat *c,float *x,float *y);
#endif
