#ifndef B22_VISOR_H
#define B22_VISOR_H
#include <stdint.h>
#define B22_W 480
#define B22_H 272
typedef enum { B22_IRONMAN=0, B22_WARMACHINE=1 } B22Suit;
typedef enum { B22_GAME=0, B22_PAUSE=1, B22_MAIN_MENU=2, B22_UPGRADE=3, B22_RESULTS=4 } B22Page;
typedef enum { B22_ORIGINAL_LAYOUT=0, B22_HYBRID=1, B22_IMMERSIVE=2 } B22UiMode;
typedef struct {
    B22Suit suit;
    B22Page page;
    B22UiMode mode;
    float armor, shield, energy, target_hp, charge;
    int locked, target_x, target_y, ammo, wave, mission_success;
    int show_minimap, show_objective, damage_warning;
} B22UI;
typedef struct {
    uint32_t suit_main, suit_accent, alert, soft, legacy_cyan;
} B22Palette;
B22Palette b22_palette(B22Suit suit);
/* 480x272 framebuffer, RGB 0x00RRGGBB. No genuine iOS HUD art inside. */
void b22_draw_hud(uint32_t *frame, int stride, const B22UI *ui);
#endif
