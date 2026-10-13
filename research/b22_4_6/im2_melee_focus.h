#ifndef IM2_MELEE_FOCUS_H
#define IM2_MELEE_FOCUS_H
#include "im2_camera.h"

typedef struct {
    int attack_active,target_alive,target_visible;
    Im2Vec3 player_head,target_center;
    float target_distance;
    int manual_camera_input;
    Im2FlightStage stage;
    float delta_seconds;
} Im2MeleeFocusInput;
typedef struct {
    float focus,extra_back;
    int initialized;
} Im2MeleeFocusState;
void im2_melee_focus_init(Im2MeleeFocusState *s);
/* Separate composition layer: never feeds back into or overwrites base camera rig. */
void im2_melee_focus_apply(Im2MeleeFocusState *s,const Im2MeleeFocusInput *in,
                      const Im2CameraState *base,Im2CameraState *out);
#endif
