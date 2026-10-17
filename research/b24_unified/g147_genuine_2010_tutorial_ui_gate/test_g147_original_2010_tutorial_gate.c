#include "b24_g147_authentic_tutorial_actor.h"
#include <assert.h>
#include <stdio.h>
typedef struct {int queries,draws,allow,id,mode,third;} Mock;
static int translate(void *p,int original,int *out){
 Mock *m=(Mock*)p;m->queries++;
 if(original!=339||!m->allow)return 0;
 *out=1275;return 1; /* test-only source translator injection, NOT
                         a claim original ID339 resolves to 1275 */
}
static int draw(void *p,int id,int mode,int third){
 Mock *m=(Mock*)p;m->draws++;
 m->id=id;m->mode=mode;m->third=third;
 return m->allow;
}
int main(void){
 B24G147Tutorial a={0};b24_g147_tutorial_init(&a);
 /* Real original game HUD IsTutConfirmed checks whether active
  * translated tutorial ID is -1 OR native override byte is set. */
 assert(b24_g147_lua_IsTutConfirmed_native(&a)==1);
 assert(!b24_g147_lua_IsTutConfirmed_native(NULL));
 B24G137Event e={0};
 e.original_lua_pc=67;e.opcode=B24_G137_CALL_SHOW_TUT;
 e.source_arg0=339;e.source_arg1=13;e.source_arg2=0;
 assert(!b24_g147_lua_ShowTut_PC67(&a,&e,NULL,NULL,NULL));
 assert(a.tutorial_was_requested&&!a.original_renderer_ack);
 Mock m={0};assert(!b24_g147_lua_ShowTut_PC67(&a,&e,translate,draw,&m));
 assert(m.queries==1&&m.draws==0);
 m.allow=1;
 assert(b24_g147_lua_ShowTut_PC67(&a,&e,translate,draw,&m));
 assert(a.original_renderer_ack&&a.native_translator_verified);
 assert(a.current_original_game_ui_text_id==1275);
 assert(a.current_original_game_ui_mode==12&&a.native_third_argument==0);
 assert(m.id==1275&&m.mode==12&&m.third==0);
 assert(b24_g147_lua_IsTutConfirmed_native(&a)==0);
 a.global_ui_override=1;
 assert(b24_g147_lua_IsTutConfirmed_native(&a)==1);
 a.global_ui_override=0;
 a.current_original_game_ui_text_id=-1;
 assert(b24_g147_lua_IsTutConfirmed_native(&a)==1);
 e.source_arg1=14;
 assert(!b24_g147_lua_ShowTut_PC67(&a,&e,translate,draw,&m));
 puts("G147 PASS original iOS ARM 2010 ShowTut Lua PC67 source ID339 translated before UI native mode 13->12, GamePlayUI UI offsets +1E38/+1E3C/+1E40, IsTutConfirmed global flag OR UI current text ID=-1; no fake QTE or mission resume, NO VPK.");
 return 0;
}
