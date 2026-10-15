#ifndef B24_G10_PRACTICE_TARGET_H
#define B24_G10_PRACTICE_TARGET_H
/* Explicit USER-REQUESTED INDESTRUCTIBLE practice target in first C1L1.
   This is a clearly labeled debugging/aim-training actor, never an original
   iOS enemy mission or source-authored NPC. No damage/AI/hidden mission. */
#define B24_G10_PRACTICE_TARGET_ID 910
typedef struct {
 float x,y,z,radius;
 int invulnerable;
 float hit_flash; /* transient cyan->gold 3D visual hit feedback, NOT HP */
} B24G10PracticeTarget;
B24G10PracticeTarget b24_g10_practice_target_at_floor(float genuine_ground_z);
int b24_g10_practice_target_valid(const B24G10PracticeTarget *t);
/* Draw debug-world visible object within existing VitaGL scene pass; no
   new framebuffer or game target simulation. */
int b24_g10_practice_target_draw(const B24G10PracticeTarget *t);
#endif
