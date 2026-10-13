#ifndef IM2_SPEED_FX_H
#define IM2_SPEED_FX_H
#include "im2_flight.h"
#include <stdint.h>
#define IM2_SPEED_W 480
#define IM2_SPEED_H 272
typedef struct {
    float strength,entry_pulse;
    uint32_t ticks;
    int enabled;
} Im2SpeedFx;
void im2_speed_fx_init(Im2SpeedFx *s);
void im2_speed_fx_step(Im2SpeedFx *s, Im2FlightStage stage, int rush_enter, float dt);
int im2_speed_fx_draw(uint32_t *pixels, int stride, const Im2SpeedFx *s, int war_machine);
#endif
