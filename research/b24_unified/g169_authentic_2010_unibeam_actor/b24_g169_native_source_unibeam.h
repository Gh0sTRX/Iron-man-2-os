#ifndef B24_G169_NATIVE_SOURCE_UNIBEAM_H
#define B24_G169_NATIVE_SOURCE_UNIBEAM_H
#include <stdint.h>
/* Actual 2010 iOS six named Beam 1/2/3 IM2V clips, dispatch ONLY for
 * accepted current weapon event. This is a local port-animation bridge:
 * original native Gameloft AttackType/VM callback mapping not proven. */
typedef struct {uint32_t began_ms;int suit,hover,active;} B24G169Beam;
int b24_g169_native_beam_begin(B24G169Beam *actor,int suit,int hover,uint32_t at_ms);
const char *b24_g169_native_beam_clip(B24G169Beam *actor,int suit,int hover,
                                      int flight_stage,uint32_t now_ms);
#endif
