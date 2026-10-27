/* G277: observational only. Count which original C1L1 authored-source
 * G75 wall/floor checks reject one grounded movement proposal.
 * Probe is disabled unless the existing G227 real-world renderer logging
 * flag is ON. No movement/physics/scene modifications, no VPK.
 */
#ifndef B24_G277_REAL_C1L1_GROUNDED_REJECT_REASONS_H
#define B24_G277_REAL_C1L1_GROUNDED_REJECT_REASONS_H
#include <stdint.h>
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
typedef struct {
 uint32_t candidate_wall_reject;
 uint32_t candidate_no_source_support;
 uint32_t candidate_unsupported_step_height;
 uint32_t candidate_accepted;
 uint32_t sweep_substeps;
} B24G277CollisionReasons;
B24G277CollisionReasons b24_g277_last_collision_reasons(void);
#endif
#endif
