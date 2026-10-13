#ifndef IM2_FLIGHT_H
#define IM2_FLIGHT_H

/* Independent C11 host-control prototype. No VitaSDK or original Gameloft physics. */

typedef struct { float x, y, z; } Im2Vec3;
typedef struct { float x, y, z, w; } Im2Quat;
typedef enum { IM2_FLIGHT_GROUND=0, IM2_FLIGHT_HOVER=1,
               IM2_FLIGHT_CRUISE=2, IM2_FLIGHT_RUSH=3 } Im2FlightStage;
typedef enum { IM2_POSE_GROUND=0, IM2_POSE_HOVER,
               IM2_POSE_AIR_MOVE, IM2_POSE_FLY_F, IM2_POSE_RUSH } Im2FlightPose;

typedef struct {
    float deadzone, cruise_enter, cruise_exit;
    float hover_speed, cruise_speed, rush_speed;
    float hover_accel, cruise_accel, rush_accel;
    float yaw_response, pose_response, idle_drag;
    float cruise_roll_rad, rush_roll_rad, max_pitch_rad;
    float ground_height, altitude_ceiling;
} Im2FlightConfig;

typedef struct {
    /* Left stick +X right, +Y forward; camera pitch + means camera above horizon. */
    float left_x, left_y, camera_yaw_rad, camera_pitch_rad;
    float altitude_axis; /* Separate fine altitude: -1..1, future D-pad mapping. */
    int airborne, boost;
    float delta_seconds;
} Im2FlightInput;

typedef struct {
    Im2Vec3 position, velocity;
    float heading_yaw_rad, visual_pitch_rad, visual_roll_rad;
    float camera_roll_hint_rad; /* max ~3 degrees; not forced on real Vita camera. */
    float turn_command; /* -1..1, positive right */
    float pose_blend; /* 0..1: visual weight of current high-speed clip */
    Im2FlightStage stage;
    Im2FlightPose pose;
    int stage_changed;
} Im2FlightState;

void im2_flight_defaults(Im2FlightConfig *config);
void im2_flight_init(Im2FlightState *s, Im2Vec3 initial_position);
void im2_flight_step(Im2FlightState *s, const Im2FlightConfig *config,
                     const Im2FlightInput *input);
/* Model is Y-up, local +Z forward; positive camera pitch = climb, right stick = -roll. */
Im2Quat im2_flight_orientation(const Im2FlightState *s);
Im2Vec3 im2_flight_rotate(Im2Quat q, Im2Vec3 local);
Im2Vec3 im2_flight_socket_world(const Im2FlightState *s, Im2Vec3 local);

#endif
