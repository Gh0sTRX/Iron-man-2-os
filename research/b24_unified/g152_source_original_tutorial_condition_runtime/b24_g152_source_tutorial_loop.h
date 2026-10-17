#ifndef B24_G152_SOURCE_TUTORIAL_LOOP_H
#define B24_G152_SOURCE_TUTORIAL_LOOP_H
#include <stdint.h>
#include "b24_g149_native_lua_bool_return.h"

/* Verified owner iOS 2010 Mission000_OnStart:
 * PC71 GETGLOBAL IsTutConfirmed, PC72 CALL returning one bool,
 * PC73 EQ R0, K35(false), A=0;
 * FALSE: PC75 GETGLOBAL Wait, PC76 LOADK 10.0, PC77 CALL,
 * PC78 JMP -8 to PC71.
 * TRUE: PC74 JMP to PC79; PC79 StopVoice(), PC80 CALL;
 * PC81 ShowTut(), PC82-84 args 340,1,1; PC85 CALL.
 *
 * Wait(10) TIME UNIT NOT RECOVERED: downstream callback must be an
 * independently proven native-source-equivalent scheduler. NULL
 * callback or rejected request fails CLOSED.
 */
typedef enum {
    B24_G152_NEED_REAL_PC72=0,
    B24_G152_WAIT_NATIVE_10=1,
    B24_G152_NEED_PC79_STOPVOICE=2,
    B24_G152_NEED_PC81_SHOWTUT340=3,
    B24_G152_STOP_AT_UNRESOLVED_PC86=4
} B24G152Stage;

typedef enum {
    B24_G152_BLOCKED_NATIVE_BINDING=0,
    B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION=1,
    B24_G152_PC71_REQUERY_READY=2,
    B24_G152_PC79_ACTION_READY=3,
    B24_G152_PC81_ACTION_READY=4,
    B24_G152_STOPPED_AT_PC86=5
} B24G152Step;

typedef int (*B24G152NativeWait)(void *ctx,float original_wait_arg);
typedef int (*B24G152NativeStopVoice)(void *ctx);
typedef int (*B24G152NativeShowTut)(void *ctx,
    int original_lua_text_id,int original_native_packed_text_id,
    int original_native_mode,int original_third_arg);

typedef struct {
    B24G152Stage stage;
    uint32_t source_wait_request_count;
    uint32_t source_stop_voice_ack_count;
    uint32_t source_show_tut340_ack_count;
    B24G149LuaBooleanReturn original_pc72_result;
} B24G152TutorialLoop;

void b24_g152_tutorial_loop_init(B24G152TutorialLoop *state);
/* original_wait_finished is a trusted event from a future original
 * Wait implementation. It MUST NOT be synthesized from frame count or
 * guessed milliseconds. Only one call/action per step.
 */
B24G152Step b24_g152_tutorial_loop_step(
    B24G152TutorialLoop *state,const B24G147Tutorial *source_tut,
    int original_wait_finished,
    B24G152NativeWait native_wait,
    B24G152NativeStopVoice native_stop_voice,
    B24G152NativeShowTut native_show_tut,
    void *ctx);
#endif
