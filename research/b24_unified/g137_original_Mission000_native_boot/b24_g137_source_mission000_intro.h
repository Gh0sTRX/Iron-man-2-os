#ifndef B24_G137_SOURCE_MISSION000_INTRO_H
#define B24_G137_SOURCE_MISSION000_INTRO_H
#include <stdint.h>
#include <stddef.h>
/* G137 owner-authentic 2010 level1.bclara Mission000_OnStart actual
 * Lua5.1 GETGLOBAL/CALL sites before first conditional PC73 ONLY.
 * This engine records/dispatches authored scene actions in true order.
 * Unknown original scene/entity bindings are NEVER treated as completed
 * and the original unknown Lua branches are not fabricated. */
typedef enum {
 B24_G137_CALL_UNKNOWN=0,
 B24_G137_CALL_MISSION_PAUSE=1,
 B24_G137_CALL_SHOW=2,
 B24_G137_CALL_HIDE=3,
 B24_G137_CALL_ENABLE=4,
 B24_G137_CALL_DISABLE=5,
 B24_G137_CALL_SETSTATE=6,
 B24_G137_CALL_SETINPUT=7,
 B24_G137_CALL_PLAYVOICE=8,
 B24_G137_CALL_SETCAMERA=9
} B24G137Call;
typedef struct {
 uint16_t original_lua_pc;
 uint16_t opcode;
 int32_t source_arg0;
 int32_t source_arg1;
 const char *source_arg1_string;
 uint8_t original_arg1_boolean;
 uint8_t original_args_reliable;
} B24G137Event;
extern const B24G137Event b24_g137_source_lua_events[];
extern const uint32_t b24_g137_source_lua_event_count;
typedef enum {
 B24_G137_UNINITIALIZED=0,
 B24_G137_READY=1,
 B24_G137_BLOCKED_NATIVE_SCENE_BINDING=2,
 B24_G137_WAITING_2010_LUA_BRANCH_PC73=3,
 B24_G137_BAD_SOURCE=4
} B24G137Stage;
typedef struct {
 B24G137Stage phase;
 uint32_t cursor;
 uint32_t actually_dispatched_count;
 uint16_t next_source_lua_pc;
 /* These are ORIGINAL EVENT REQUESTS, not proof native scene side effect. */
 uint8_t requested_mission_pause;
 uint8_t requested_MarkV_idle;
 uint8_t requested_MarkV_hidden;
 uint8_t requested_input14_disabled;
 uint8_t unresolved_scene_event;
} B24G137Mission000;
typedef int (*B24G137SceneHandler)(void *context,const B24G137Event *event);
int b24_g137_mission000_init(B24G137Mission000 *m);
B24G137Stage b24_g137_mission000_dispatch_verified_prefix(
 B24G137Mission000 *m,B24G137SceneHandler native_scene_binding,void *context);
int b24_g137_mission000_is_gameplay_released(const B24G137Mission000 *m);
#endif
