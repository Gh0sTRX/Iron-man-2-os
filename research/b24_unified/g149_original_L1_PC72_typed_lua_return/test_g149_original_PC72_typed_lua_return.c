#include "b24_g149_native_lua_bool_return.h"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    B24G137Event e = {0};
    e.original_lua_pc = 72;
    e.opcode = B24_G137_CALL_IS_TUT_CONFIRMED;
    e.original_args_reliable = 1;
    B24G149LuaBooleanReturn r;
    B24G147Tutorial t;
    b24_g147_tutorial_init(&t);

    /* Native without active tutorial can report true, but PC72
     * must not ACK without original requested+rendered scene. */
    assert(b24_g147_lua_IsTutConfirmed_native(&t) == 1);
    assert(!b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    assert(!r.result_is_valid && !r.conditional_evaluated);

    /* Test fixture pretends real source draw was acknowledged,
     * NOT that a QTE renderer has been implemented. */
    t.tutorial_was_requested = 1;
    t.original_renderer_ack = 1;
    t.native_translator_verified = 1;
    t.source_clara_text_id = 339;
    t.current_original_game_ui_mode = 12;
    t.current_original_game_ui_text_id = 0x1053;
    assert(b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    assert(r.result_is_valid && !r.lua_boolean);
    assert(r.query_pc == 72 && r.pending_conditional_pc == 73);
    assert(!r.conditional_evaluated);

    t.global_ui_override = 1;
    assert(b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    assert(r.result_is_valid && r.lua_boolean && !r.conditional_evaluated);
    t.global_ui_override = 0;
    t.current_original_game_ui_text_id = -1;
    assert(b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    assert(r.result_is_valid && r.lua_boolean && !r.conditional_evaluated);

    t.current_original_game_ui_text_id = 0x1054;
    assert(!b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    assert(!r.result_is_valid);
    t.current_original_game_ui_text_id = 0x1053;
    e.original_lua_pc = 73;
    assert(!b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    e.original_lua_pc = 72;
    e.opcode = B24_G137_CALL_UNKNOWN;
    assert(!b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    e.opcode = B24_G137_CALL_IS_TUT_CONFIRMED;
    e.original_args_reliable = 0;
    assert(!b24_g149_capture_original_PC72_boolean(&e, &t, &r));
    e.original_args_reliable = 1;
    assert(!b24_g149_capture_original_PC72_boolean(&e, 0, &r));
    assert(!b24_g149_capture_original_PC72_boolean(&e, &t, 0));
    puts("G149 PASS: Lua PC72 false is a valid return, missing source scene blocked, PC73 EQ NOT executed. NO VPK.");
    return 0;
}
