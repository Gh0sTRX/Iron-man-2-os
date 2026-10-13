#ifndef B23_MISSILE_LOCK_H
#define B23_MISSILE_LOCK_H
#include <stddef.h>
#include <stdint.h>
#include "../b22_hud/b22_visor.h"

/* New Vita design (not recovered 2010 Gameloft lock-on implementation). */
typedef enum {
    B23_REPULSOR=0, B23_UNIBEAM=1, B23_MISSILE=2, B23_MELEE=3
} B23Weapon;
typedef enum { B23_IDLE=0, B23_ACQUIRING=1, B23_LOCKED=2 } B23Phase;
typedef struct {
    int id, alive, visible, occluded;
    float distance, aim_cos, health_percent;
    int screen_x, screen_y;
} B23Target;
typedef struct {
    B23Weapon weapon;
    B23Phase phase;
    int lock_button_held;
    int target_id, target_x, target_y;
    float target_health_percent;
    float acquire_s, required_s;
    float max_distance, min_aim_cos;
} B23Lock;

void b23_init(B23Lock *lock);
/* Stable target ID, no involuntary camera movement and NO non-missile lock. */
void b23_tick(B23Lock *lock, B23Weapon weapon, int lock_button_held,
              const B23Target *targets, size_t count, float delta_seconds);
float b23_progress(const B23Lock *lock);
/* Disable B22's old weapon-agnostic brackets; draw missile-only overlay afterward. */
void b23_prepare_b22_ui(B22UI *ui);
void b23_draw_missile_hud(uint32_t *frame, int stride, const B23Lock *lock,
                          B22Suit suit, B22UiMode mode, B22Page page);
#endif
