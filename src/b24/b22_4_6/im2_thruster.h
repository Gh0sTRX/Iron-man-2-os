#ifndef IM2_THRUSTER_H
#define IM2_THRUSTER_H
#include "im2_flight.h"
#include <stdint.h>

#define IM2_THRUSTER_SOCKETS 6
#define IM2_THRUSTER_MAX_PARTICLES 128

typedef enum {
    IM2_FOOT_L=0,IM2_FOOT_R=1, IM2_PALM_L=2,IM2_PALM_R=3,
    IM2_BACK_L=4,IM2_BACK_R=5
} Im2ThrusterSocketId;
typedef enum { IM2_PARTICLE_IM_BLUE=0,IM2_PARTICLE_WM_AMBER=1 } Im2ParticleTheme;
typedef struct {
    int valid;  /* No invented bone/socket positions: game must supply pose-local anchors */
    Im2Vec3 model_position, model_exhaust_direction;
} Im2ThrusterSocket;
typedef struct {
    Im2Vec3 position,velocity;
    float age,life,size;
    uint8_t socket_id,theme;
    int active;
} Im2ThrusterParticle;
typedef struct {
    uint8_t enabled[IM2_THRUSTER_SOCKETS];
    float intensity[IM2_THRUSTER_SOCKETS];
    int rush_entry; /* one-frame event */
    int allowed_particle_count;
} Im2ThrusterOutput;
typedef struct {
    Im2ThrusterParticle particles[IM2_THRUSTER_MAX_PARTICLES];
    float fractional[IM2_THRUSTER_SOCKETS];
    float rush_pulse;
    Im2FlightStage last_stage;
    uint32_t rng;
} Im2ThrusterState;

void im2_thruster_init(Im2ThrusterState *state);
/* Recovered .im2v animation pose/socket binding required at future Vita integration. */
Im2ThrusterOutput im2_thruster_step(Im2ThrusterState *state,
        const Im2FlightState *flight, Im2FlightStage stage,
        const Im2ThrusterSocket sockets[IM2_THRUSTER_SOCKETS],
        Im2ParticleTheme theme, float dt);
#endif
