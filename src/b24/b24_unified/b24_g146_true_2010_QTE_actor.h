#ifndef B24_G146_TRUE_2010_QTE_ACTOR_H
#define B24_G146_TRUE_2010_QTE_ACTOR_H
#include <stdint.h>
#include "b24_g137_source_mission000_intro.h"
/* User's original Gameloft 2010 level1.bclara, 193 native schema,
 * actual typed class 94 InteractiveObj ID1456 (InteractiveObj_QTE):
 * native child rigid transform 1458, original LOCAL pose source.
 * Source camera 1495/2541 and PD 1491/1499/2533/2537,
 * original Material_QTE class53 ID2367. */
typedef struct {
 uint32_t source_scene_actor_ID;
 uint32_t source_native_class;
 uint32_t source_transform_child_ID;
 float original_local_xyz[3];
 float original_local_quat_xyzw[4];
 int original_show_requested;
 int original_show_actually_rendered;
 int source_tutorial_QTE_user_completion_verified;
} B24G146QTE;
typedef int (*B24G146RendererShow)(void *ctx,const B24G146QTE *source_actor);
int b24_g146_qte_source_init(B24G146QTE *q);
int b24_g146_qte_show_source_Lua_PC6(
 B24G146QTE *q,const B24G137Event *event,
 B24G146RendererShow authentic_render_callback,void *ctx);
#endif
