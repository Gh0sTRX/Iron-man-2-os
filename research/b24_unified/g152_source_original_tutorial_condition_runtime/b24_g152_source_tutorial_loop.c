#include "b24_g152_source_tutorial_loop.h"
#include <string.h>

void b24_g152_tutorial_loop_init(B24G152TutorialLoop *state)
{
    if (!state) return;
    memset(state,0,sizeof(*state));
    state->stage=B24_G152_NEED_REAL_PC72;
}
B24G152Step b24_g152_tutorial_loop_step(
    B24G152TutorialLoop *state,const B24G147Tutorial *source_tut,
    int original_wait_finished,
    B24G152NativeWait native_wait,
    B24G152NativeStopVoice native_stop_voice,
    B24G152NativeShowTut native_show_tut,
    void *ctx)
{
    if (!state) return B24_G152_BLOCKED_NATIVE_BINDING;
    if (state->stage==B24_G152_STOP_AT_UNRESOLVED_PC86)
        return B24_G152_STOPPED_AT_PC86;
    if (state->stage==B24_G152_WAIT_NATIVE_10) {
        if (!original_wait_finished)
            return B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION;
        state->stage=B24_G152_NEED_REAL_PC72;
        return B24_G152_PC71_REQUERY_READY;
    }
    if (state->stage==B24_G152_NEED_REAL_PC72) {
        const B24G137Event pc72 = {
            .original_lua_pc=72,
            .opcode=B24_G137_CALL_IS_TUT_CONFIRMED,
            .original_args_reliable=1
        };
        B24G149LuaBooleanReturn result;
        if (!b24_g149_capture_original_PC72_boolean(
                &pc72,source_tut,&result) ||
            !result.result_is_valid ||
            result.conditional_evaluated ||
            result.pending_conditional_pc!=73)
            return B24_G152_BLOCKED_NATIVE_BINDING;
        /* G151 original PC73: EQ A=0, R0 versus K35 FALSE.
         * false -> Wait(10); true -> StopVoice at PC79. */
        state->original_pc72_result=result;
        if (!result.lua_boolean) {
            if (!native_wait || !native_wait(ctx,10.0f))
                return B24_G152_BLOCKED_NATIVE_BINDING;
            state->source_wait_request_count++;
            state->stage=B24_G152_WAIT_NATIVE_10;
            return B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION;
        }
        state->stage=B24_G152_NEED_PC79_STOPVOICE;
        return B24_G152_PC79_ACTION_READY;
    }
    if (state->stage==B24_G152_NEED_PC79_STOPVOICE) {
        if (!native_stop_voice || !native_stop_voice(ctx))
            return B24_G152_BLOCKED_NATIVE_BINDING;
        state->source_stop_voice_ack_count++;
        state->stage=B24_G152_NEED_PC81_SHOWTUT340;
        return B24_G152_PC81_ACTION_READY;
    }
    if (state->stage==B24_G152_NEED_PC81_SHOWTUT340) {
        /* G148 authentic 2010 StringMgr: one-based source ID 340
         * -> chap1 section index 1, local 84 -> native packed 0x1054.
         * Source Lua arg2=1 passes GamePlayUI native mode=0 (arg2-1).
         * No source HUD/font renderer is fabricated. */
        if (!native_show_tut ||
            !native_show_tut(ctx,340,0x1054,0,1))
            return B24_G152_BLOCKED_NATIVE_BINDING;
        state->source_show_tut340_ack_count++;
        state->stage=B24_G152_STOP_AT_UNRESOLVED_PC86;
        return B24_G152_STOPPED_AT_PC86;
    }
    return B24_G152_BLOCKED_NATIVE_BINDING;
}
