#ifndef B24_G11_ORIGINAL_UNIBEAM_SEQUENCE_H
#define B24_G11_ORIGINAL_UNIBEAM_SEQUENCE_H
#include <stdint.h>
/* Genuine 2010 3-part IronMan owner Beam1/2/3 originals.
   Exact B18 source durations: Ground 400+400+1000ms; Float 600+400+1266.
   These are skinned per correct BRES suit, never used for WarMachine. */
const char *b24_g11_unibeam_clip(int suit,int flying,uint32_t elapsed_ms);
uint32_t b24_g11_unibeam_duration_ms(int flying);
#endif
