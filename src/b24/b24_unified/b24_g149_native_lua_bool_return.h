#ifndef B24_G149_NATIVE_LUA_BOOL_RETURN_H
#define B24_G149_NATIVE_LUA_BOOL_RETURN_H
#include <stdint.h>
#include "b24_g147_authentic_tutorial_actor.h"

/* Original Mission000_OnStart Lua PC72 IsTutConfirmed returns a boolean.
 * A valid FALSE is not a failed scene callback. Lua PC73 EQ remains
 * unresolved until its original bytecode semantics are implemented. */
typedef struct {
    uint16_t query_pc;
    uint16_t pending_conditional_pc;
    uint8_t result_is_valid;
    uint8_t lua_boolean;
    uint8_t conditional_evaluated; /* always zero in G149 */
} B24G149LuaBooleanReturn;

/* Return 1 on successfully evaluated source PC72, INCLUDING false.
 * Return 0 for wrong original event or unacknowledged source renderer. */
int b24_g149_capture_original_PC72_boolean(
    const B24G137Event *event, const B24G147Tutorial *tutorial,
    B24G149LuaBooleanReturn *out_return);
#endif
