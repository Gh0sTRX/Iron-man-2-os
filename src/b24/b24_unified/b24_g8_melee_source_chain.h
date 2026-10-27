#ifndef B24_G8_MELEE_SOURCE_CHAIN_H
#define B24_G8_MELEE_SOURCE_CHAIN_H
#include <stdint.h>
/* Authoritative original 2010 Mark VI ground combo clip names and durations.
   Timing is original animation metadata, NOT reverse-engineered hit frames.
   Buffered attack input is NEW Vita mechanic, no damage until real hit sockets. */
typedef struct {
 unsigned phase;           /* 0 idle, 1/2/3 attacks, 4 end1, 5 end2 */
 unsigned buffered;        /* user queued another melee press */
 uint32_t started_ms;
 unsigned completed_attacks;
} B24G8MeleeChain;
void b24_g8_melee_press(B24G8MeleeChain *a,uint32_t now);
const char *b24_g8_melee_tick(B24G8MeleeChain *a,uint32_t now);
int b24_g8_melee_active(const B24G8MeleeChain *a);
#endif
