#include "b24_g149_native_lua_bool_return.h"
#include <string.h>

int b24_g149_capture_original_PC72_boolean(
    const B24G137Event *event, const B24G147Tutorial *tutorial,
    B24G149LuaBooleanReturn *out_return)
{
    if (out_return)
        memset(out_return, 0, sizeof(*out_return));
    if (!out_return || !event || !tutorial ||
        event->original_lua_pc != 72 ||
        event->opcode != B24_G137_CALL_IS_TUT_CONFIRMED ||
        !event->original_args_reliable ||
        !tutorial->tutorial_was_requested ||
        !tutorial->original_renderer_ack ||
        !tutorial->native_translator_verified ||
        tutorial->source_clara_text_id != 339 ||
        tutorial->current_original_game_ui_mode != 12 ||
        (tutorial->current_original_game_ui_text_id != 0x1053 &&
         tutorial->current_original_game_ui_text_id != -1))
        return 0;

    /* Original 2010 native 0x187BC: override || UI+0x1E38 == -1.
     * A false return is a normal completed native call. */
    out_return->query_pc = 72;
    out_return->pending_conditional_pc = 73;
    out_return->lua_boolean =
        (uint8_t)(b24_g147_lua_IsTutConfirmed_native(tutorial) != 0);
    out_return->result_is_valid = 1;
    /* Do not infer a PC73 EQ direction or MissionResume. */
    out_return->conditional_evaluated = 0;
    return 1;
}
