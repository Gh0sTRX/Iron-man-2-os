#ifndef B24_G72_DIAGNOSTIC_SKY_H
#define B24_G72_DIAGNOSTIC_SKY_H
/* A/B diagnostic dusk atmosphere, NOT yet source C1L1_sky_001 rendering.
 * Source sky Deco001 model has been identified; this cheap background is
 * temporary until its true native texture/shader and runtime transform decode.
 * Drawn into the ALREADY OPEN G9 VitaGL frame, before source city. */
int b24_g72_draw_dusk_atmosphere(float camera_pitch,float camera_yaw);
#endif
