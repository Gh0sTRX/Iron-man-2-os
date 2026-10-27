#ifndef B24_G172_WM_GROUND_M_SOURCE_H
#define B24_G172_WM_GROUND_M_SOURCE_H
#include <stdint.h>
#include <string.h>
/* Source: original user-owned 2010 iOS B18/304 clip inventory.
 * These names and durations are AUTHORED animation data.
 * "M" weapon semantics / native key mapping are NOT yet proven.
 * No fabricated keyframes, attacks, root motion, or hit windows. */
static const char *const b24_g172_ground_m[5]={
 "warmachine_warmachine_aim_m_ground_idle",
 "warmachine_warmachine_aim_m_ground_move_f",
 "warmachine_warmachine_aim_m_ground_move_b",
 "warmachine_warmachine_aim_m_ground_move_l",
 "warmachine_warmachine_aim_m_ground_move_r"};
static const char *const b24_g172_ground_m_att[5]={
 "warmachine_warmachine_aim_m_ground_idle_att",
 "warmachine_warmachine_aim_m_ground_move_f_att",
 "warmachine_warmachine_aim_m_ground_move_b_att",
 "warmachine_warmachine_aim_m_ground_move_l_att",
 "warmachine_warmachine_aim_m_ground_move_r_att"};
static const uint32_t b24_g172_ground_m_ms[5]={1600u,1600u,1600u,1600u,1600u};
static const uint32_t b24_g172_ground_m_att_ms[5]={1600u,866u,1399u,866u,866u};
static inline const char *b24_g172_wm_m_ground_clip(unsigned direction,int accepted_fire){
 if(direction>=5u)return 0;
 return accepted_fire?b24_g172_ground_m_att[direction]:b24_g172_ground_m[direction];
}
static inline uint32_t b24_g172_wm_m_ground_duration(const char *stem){
 if(!stem)return 0;
 for(unsigned d=0;d<5u;d++){
  if(!strcmp(stem,b24_g172_ground_m[d]))return b24_g172_ground_m_ms[d];
  if(!strcmp(stem,b24_g172_ground_m_att[d]))return b24_g172_ground_m_att_ms[d];
 }
 return 0; /* strict: unknown native clip gets NO guessed timing */
}
#endif
