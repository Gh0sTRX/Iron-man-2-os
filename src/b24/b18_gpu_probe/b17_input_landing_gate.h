#ifndef B17_INPUT_LANDING_GATE_H
#define B17_INPUT_LANDING_GATE_H
/* Standalone original B17 Z-up adapter proposal, host-only. */
typedef struct {
    float run_enter,run_exit,flight_enter,flight_exit;
    float min_forward,contact_tolerance;
} B17GateConfig;
typedef struct {int is_ground_running,is_fast_flight,landing_pending,landing_event;} B17GateState;
typedef struct {
    float stick_x,stick_forward,feet_world_z,ground_world_z,vertical_velocity_z;
    int airborne,landing_requested,ground_valid;
} B17GateInput;
void b17_gate_defaults(B17GateConfig *c);
void b17_gate_init(B17GateState *s);
void b17_gate_step(B17GateState *s,const B17GateConfig *c,const B17GateInput *in);
#endif
