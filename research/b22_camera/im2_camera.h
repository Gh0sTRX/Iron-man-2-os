#ifndef IM2_CAMERA_H
#define IM2_CAMERA_H

#include "im2_flight.h"

/* Isolated C11 host rig: stage-aware follow camera, not Vita integration. */
typedef struct {
    float shoulder_right_offset;
    float shoulder_aim_offset;
    float shoulder_distance, cruise_distance, rush_distance;
    float shoulder_lift, cruise_lift, rush_lift;
    float shoulder_fov_deg, cruise_fov_deg, rush_fov_deg;
    float anchor_head_height;
    float transition_rate, follow_rate, yaw_follow_rate;
    float min_wall_distance, wall_padding;
    float pitch_limit_rad;
    float camera_roll_fraction, max_camera_roll_rad;
} Im2CameraConfig;

typedef struct {
    Im2Vec3 player_position;
    Im2FlightStage flight_stage;
    float character_heading_yaw_rad;
    float camera_input_yaw_rad;
    float camera_input_pitch_rad;
    int manual_right_stick; /* allow free look, disable forced alignment to suit */
    float visual_suit_roll_rad;
    float wall_hit_distance; /* <=0 or non-finite: no hit; otherwise external raycast */
    float delta_seconds;
} Im2CameraInput;

typedef struct {
    Im2Vec3 position, target, forward, right, up;
    float yaw_rad, pitch_rad, visual_roll_rad;
    float fov_deg, shoulder_to_chase, rush_amount;
    float current_distance, safe_distance;
    int initialized;
} Im2CameraState;

void im2_camera_defaults(Im2CameraConfig *config);
void im2_camera_init(Im2CameraState *state);
void im2_camera_step(Im2CameraState *state, const Im2CameraConfig *config,
                     const Im2CameraInput *input);

#endif
