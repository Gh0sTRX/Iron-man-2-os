#ifndef B24_WM_ORIGINAL_MARKER_G8_WORLD_H
#define B24_WM_ORIGINAL_MARKER_G8_WORLD_H
#include "b24_wm_2010_gun_stream.h"

/* REPLICATES actual G8 CPU renderer.c third-person lines 420-428, applying
   B14 authoritative position/heading to original 2010 model-local gun nodes.
   Do NOT treat resulting source marker as confirmed right Gatling/left rocket
   muzzle until original game effect-attachment identity is solved. */
typedef struct {
 float player_x,player_y,player_z;
 float player_heading;
 float model_center_z;
 float hover_bob;
} B24WMG8ActorPose;
int b24_wm_g8_marker_world_point(const B24WMG8ActorPose *actor,
                                 const float original_model_point[3],
                                 float out_world_xyz[3]);
int b24_wm_g8_marker_world_direction(const B24WMG8ActorPose *actor,
                                     const float original_model_axis[3],
                                     float out_world_unit_xyz[3]);
int b24_wm_g8_source_gun03_marker_world(const B24WMG8ActorPose *actor,
                                       const float original_gun_matrices[6][16],
                                       float world_tip[3],float world_axis[3]);
#endif
