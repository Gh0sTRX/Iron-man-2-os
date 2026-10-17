#ifndef B24_G147_AUTHENTIC_TUTORIAL_ACTOR_H
#define B24_G147_AUTHENTIC_TUTORIAL_ACTOR_H
#include <stdint.h>
#include "b24_g137_source_mission000_intro.h"
/* Verified actual original 2010 owner Mach-O ARM:
 * ShowTut(lua_State*) VM 0x18818 (5 Lua args, despite 3 supplied in L1):
 * first arg ID passes StringMgr::strIDClara2Real(&id).
 * second arg translated via (arg2-1) to GamePlayUI::ShowTutorial.
 * Native GamePlayUI::ShowTutorial(int,int,int,bool,int,int) VM0x1E1F8
 * stores translated text ID at UI+0x1E38, native mode at UI+0x1E3C,
 * arg3 at UI+0x1E40.
 * IsTutConfirmed(lua_State*) VM 0x187BC loads current UI+0x1E38 and
 * checks global short circuit flag: result=(global_override!=0 ||
 *                                          ui_current_text_ID==-1).
 * This is a BOOL QUERY; by itself does NOT execute PC73 Lua branch.
 */
typedef struct {
 int current_original_game_ui_text_id; /* actual UI+0x1E38, -1 = no tutor */
 int current_original_game_ui_mode;    /* native UI+0x1E3C */
 int native_third_argument;           /* native UI+0x1E40 */
 int source_clara_text_id;            /* authored script 339 */
 uint8_t global_ui_override;
 uint8_t native_translator_verified;
 uint8_t original_renderer_ack;
 uint8_t tutorial_was_requested;
} B24G147Tutorial;
typedef int (*B24G147TextTranslator)(void *ctx,int original_clara_string_id,int *real_text_id_out);
typedef int (*B24G147TutorialRenderer)(void *ctx,int game_ui_text_id,int native_ui_mode,int third);
void b24_g147_tutorial_init(B24G147Tutorial *q);
int b24_g147_lua_ShowTut_PC67(B24G147Tutorial *q,
 const B24G137Event *e,B24G147TextTranslator translate,
 B24G147TutorialRenderer draw,void *ctx);
int b24_g147_lua_IsTutConfirmed_native(const B24G147Tutorial *q);
#endif
