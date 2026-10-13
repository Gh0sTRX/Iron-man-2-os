#ifndef IM2_B21_CONTROL_LAB_H
#define IM2_B21_CONTROL_LAB_H
#ifdef __cplusplus
extern "C" {
#endif
#include <stdint.h>
#define IM2_MAX_TARGETS 16
typedef enum { IM2_BT_R=1u<<0, IM2_BT_L=1u<<1, IM2_BT_SQUARE=1u<<2,
 IM2_BT_TRIANGLE=1u<<3, IM2_BT_CIRCLE=1u<<4, IM2_BT_CROSS=1u<<5,
 IM2_BT_DUP=1u<<6, IM2_BT_DDOWN=1u<<7, IM2_BT_DLEFT=1u<<8,
 IM2_BT_DRIGHT=1u<<9, IM2_BT_START=1u<<10, IM2_BT_SELECT=1u<<11 } Im2Button;
typedef struct { float x,y,z; } Im2Point;
typedef struct { int id,alive,visible; Im2Point pos; } Im2Target;
typedef enum { IM2_PLAYING, IM2_PAUSED } Im2State;
typedef enum { IM2_MENUMAIN, IM2_MENUOPTIONS } Im2Menu;
typedef enum { IM2_SETTING_MUSIC, IM2_SETTING_SFX, IM2_SETTING_INVERT_X,
 IM2_SETTING_INVERT_Y, IM2_SETTING_SENSITIVITY, IM2_SETTING_COUNT } Im2Setting;
typedef struct { int music,sfx,invert_x,invert_y; float camera_sensitivity; } Im2Settings;
typedef struct {
 float health,shield,energy; int weapon,target_id,ammo,mission_completed;
 int enemies_left,wave; float enemy_hp; const char *objective;
} Im2HudInfo;
typedef struct {
 uint32_t held,pressed,released; float move_x,move_y,cam_x,cam_y;
 int fire,melee,boost,interact,flight_toggle,vertical,weapon_delta;
 int target_locked,target_id; Im2State state; Im2Menu menu;
 int selected_option; Im2Settings settings;
} Im2Controls;
void im2_controls_init(Im2Controls *c);
void im2_controls_tick(Im2Controls *c,uint32_t buttons,float lx,float ly,float rx,float ry);
int im2_controls_lock_target(Im2Controls *c,Im2Point origin,Im2Point look_dir,
                             const Im2Target *targets,int count,float max_dist,float cone_cos);
void im2_hud_normalized(const Im2HudInfo *h,float *health,float *shield,float *energy);
#ifdef __cplusplus
}
#endif
#endif
