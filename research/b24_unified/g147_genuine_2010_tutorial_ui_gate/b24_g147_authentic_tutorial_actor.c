#include "b24_g147_authentic_tutorial_actor.h"
#include <string.h>
void b24_g147_tutorial_init(B24G147Tutorial *q){
 if(!q)return;
 memset(q,0,sizeof(*q));
 /* 2010 GamePlayUI::ShowTutorial sees -1 when no tutorial active;
  * the source integer field exists at UI+0x1E38. */
 q->current_original_game_ui_text_id=-1;
 q->current_original_game_ui_mode=-1;
}
int b24_g147_lua_ShowTut_PC67(B24G147Tutorial *q,
 const B24G137Event *e,B24G147TextTranslator translate,
 B24G147TutorialRenderer draw,void *ctx){
 if(!q||!e||e->original_lua_pc!=67||
    e->opcode!=B24_G137_CALL_SHOW_TUT||
    e->source_arg0!=339||e->source_arg1!=13||
    e->source_arg2!=0)return 0;
 q->tutorial_was_requested=1;
 q->source_clara_text_id=339;
 /* From iOS native: StringMgr::strIDClara2Real transforms original
  * CLARA string ID BEFORE passing to GamePlayUI::ShowTutorial. */
 if(!translate||!draw)return 0;
 int translated=-1;
 if(!translate(ctx,339,&translated)||translated<0)return 0;
 /* native 2010 Lua function subtracts 1 from second arg 13 */
 if(!draw(ctx,translated,12,0))return 0;
 q->current_original_game_ui_text_id=translated;
 q->current_original_game_ui_mode=12;
 q->native_third_argument=0;
 q->native_translator_verified=1;
 q->original_renderer_ack=1;
 return 1;
}
int b24_g147_lua_IsTutConfirmed_native(const B24G147Tutorial *q){
 /* Original iOS native 0x187E4..0x18800:
  * if (global_override_byte) lua_pushboolean(1)
  * else lua_pushboolean(UI+0x1E38 == -1).
  * If actual UI instance not initialized, do NOT infer a true
  * confirmation from a null pointer. */
 if(!q)return 0;
 return (q->global_ui_override!=0 ||
         q->current_original_game_ui_text_id==-1);
}
