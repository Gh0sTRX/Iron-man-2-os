#ifndef B19_GAMEPLAY_CORE_H
#define B19_GAMEPLAY_CORE_H
#ifdef __cplusplus
extern "C" {
#endif
#define B19_MAX_ENEMIES 8
#define B19_MAX_EVENTS 64
typedef struct { float x,y,z; } B19Vec3;
typedef enum { B19_READY=0, B19_PLAYING=1, B19_WON=2, B19_LOST=3 } B19MissionState;
typedef enum { B19_EV_WAVE_START=1, B19_EV_PLAYER_FIRE, B19_EV_ENEMY_HIT,
               B19_EV_ENEMY_DIED, B19_EV_PLAYER_HIT, B19_EV_MISSION_WIN,
               B19_EV_MISSION_FAIL } B19EventType;
typedef struct { B19EventType type; int entity_id, amount; } B19Event;
typedef struct { B19Vec3 pos; float hp, attack_cooldown; int id, alive; } B19Enemy;
typedef struct {
    B19MissionState state; B19Vec3 player_pos; float player_hp, player_shield;
    B19Enemy enemies[B19_MAX_ENEMIES]; int wave, alive, kills;
    float shot_cooldown, elapsed; B19Event events[B19_MAX_EVENTS]; int events_count;
} B19Game;
void b19_init(B19Game *g);
void b19_restart(B19Game *g);
void b19_set_player_position(B19Game *g, B19Vec3 pos);
void b19_tick(B19Game *g, float dt);
/* World-space ray against bounded prototype enemy collision spheres.
   This is NOT the original iOS damage model, nor original level mission graph. */
int b19_fire_repulsor(B19Game *g, B19Vec3 origin, B19Vec3 direction);
int b19_pop_event(B19Game *g, B19Event *out);
#ifdef __cplusplus
}
#endif
#endif
