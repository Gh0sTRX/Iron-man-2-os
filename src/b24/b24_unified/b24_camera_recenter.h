#ifndef B24_CAMERA_RECENTER_H
#define B24_CAMERA_RECENTER_H
typedef struct { float idle_seconds; } B24CameraRecenter;
/* World Z-up, B17: orbit camera azimuth toward character heading.
 * Active ONLY when Stage2/RUSH, manual right stick released >0.6s.
 * Returns camera orbit angle. Player/flight heading is NOT modified.
 */
float b24_camera_recenter(B24CameraRecenter *state,int flight_stage,
    float delta_seconds,float right_x,float right_y,float orbit,float character_heading);
#endif
