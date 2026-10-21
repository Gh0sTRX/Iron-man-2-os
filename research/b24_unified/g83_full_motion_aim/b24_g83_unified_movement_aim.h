#ifndef B24_G83_UNIFIED_MOVEMENT_AIM_H
#define B24_G83_UNIFIED_MOVEMENT_AIM_H
#include <stdint.h>
#include "../g82_original_combat/b24_g82_original_combat_coordinator.h"
/* Original 2010 animation asset stems, proved by B18/G81 source catalog.
 * IMPORTANT: We derive no 2010 player input/permission or real hit times
 * solely from original clip names. G83 is a source-only Vita ROUTE CANDIDATE.
 * B14 remains sole physical movement integrator; this must not duplicate it. */
typedef enum {B24G83_MARKVI=0,B24G83_WARMACHINE=2} B24G83Suit;
typedef enum {B24G83_GROUND=0,B24G83_HOVER=1,
 B24G83_FLIGHT=2,B24G83_RUSH=3} B24G83Mode;
typedef enum {B24G83_AIM_NONE=0,B24G83_AIM_HAND=1,
 B24G83_AIM_DUAL=2,B24G83_AIM_LEFT=3,
 B24G83_AIM_M_UNCLASSIFIED=4} B24G83Aim;
typedef enum {B24G83_DIR_IDLE=0,B24G83_DIR_F=1,B24G83_DIR_B=2,
 B24G83_DIR_L=3,B24G83_DIR_R=4} B24G83Dir;
typedef enum {
 B24G83_EVENT_NONE=0,B24G83_EVENT_GROUND_TO_HOVER,
 B24G83_EVENT_FLY_START,B24G83_EVENT_FLY_STOP,
 B24G83_EVENT_FLY_TO_GROUND,B24G83_EVENT_FLY_TO_RUN,
 B24G83_EVENT_DODGE_LEFT,B24G83_EVENT_DODGE_RIGHT
} B24G83Event;
typedef struct {
 int suit_index;              /* 0 Mark VI, 2 WM; other suits not wrongly skinned */
 B24G83Mode motion;           /* from sole B14 physics tick */
 B24G83Aim aim;               /* input state; _M native semantics not proven */
 float axis_x;                /* already B14-owned move input */
 float axis_y;
 int run;                     /* grounded user choice; does not change velocity */
 int accepted_weapon_event;   /* only successful shot from combat gate */
 B24G83Event transition;      /* explicit confirmed event, not guessed at FPS */
 B24G83Dir previous_flight_dir;
 int grounded_contact_verified;
 int paused;
} B24G83Input;
typedef struct {
 const char *stem;            /* original source .im2v file stem */
 B24G83Dir direction;
 int source_authored_name;
 int one_shot_not_looping;    /* use clip's ORIGINAL IM2V duration */
 uint32_t original_source_duration_ms; /* 2010 authored, 0=unmapped */
 int input_semantics_verified_original_ios; /* always false so far */
 int needs_2010_hit_event;    /* G304 legacy field, MUST remain 0 until true source
                                 StateTrack time-unit+actor contact+attack permission
                                 are runtime-verified; _att/combo != hit. */
} B24G83Selection;
/* G301: actual B14 flight controller analog direction BEFORE G83 selection.
 * A pinned one-shot may carry OLD selected->direction (e.g. fly_ftol).
 * G84 must NOT feed that visual direction back into next-frame physics.
 * In HOVER/RUSH/GROUND there is no Stage2 flight turn history.
 * This is a routing helper, NOT a second movement integrator. */
B24G83Dir b24_g83_physical_flight_dir(B24G83Mode mode,
                                      float axis_x,float axis_y);
/* Safe result 0 on invalid input. Unsupported source rig/action = stem NULL.
 * Gameplay uses G8 IM2V stream/mesh ownership; this only selects filenames. */
int b24_g83_select_original_motion(const B24G83Input *in,
                                    B24G83Selection *out);
/* Existing G82 verified event+damage controller has priority over motion
 * when its original combo clip is playing. No double actor physics owner. */
int b24_g83_select_combined(B24G82Combat *combat,uint32_t time_ms,
 const B24G83Input *in,B24G83Selection *out);
#endif
