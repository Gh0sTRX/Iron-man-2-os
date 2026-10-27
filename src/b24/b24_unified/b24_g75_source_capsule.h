#ifndef B24_G75_SOURCE_CAPSULE_H
#define B24_G75_SOURCE_CAPSULE_H
#include "b24_c1_original_collision.h"
/* Reconcile ONE existing G9/B14 world displacement using the original
 * G68 1,910 author-placed collision triangles. No extra movement or GPU
 * owner. Based on user-confirmed G67 multi-slice source collision approach.
 * Source-only opt-in prototype; not yet shipped in a Vita VPK. */
int b24_g75_capsule_reconcile(const B24C1OriginalCollision *world,
 float start_x,float start_y,float start_foot_z,
 float target_x,float target_y,float target_foot_z,
 int grounded,float radius,float height,
 float *out_x,float *out_y,float *out_foot_z);
/* Last landing swept vertical segment: prefer topmost actually crossed
 * authored source walkable triangle; no arbitrary remote roof teleport. */
int b24_g75_floor_crossed(const B24C1OriginalCollision *world,
 float x,float y,float z_before,float z_after,float *floor_z);
/* Exact accepted feet/support agreement, never just a nearby floor. */
int b24_g75_support_at(const B24C1OriginalCollision *world,
 float x,float y,float feet_z,float *support_z);
#endif
