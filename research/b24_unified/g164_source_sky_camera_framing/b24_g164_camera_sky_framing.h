#ifndef B24_G164_CAMERA_SKY_FRAMING_H
#define B24_G164_CAMERA_SKY_FRAMING_H
/* Geometry: actual 2010 G73 original sky sphere centered at source (0,0,0)
 * must remain camera-relative so skyline/moon do not slip behind / below
 * world during player exploration. Preserve true original UV/atlas, view
 * ROTATION only, without inventing original camera position/sky shader. */
int b24_g164_source_sky_view(const float world_view[16],float sky_view[16]);
/* Experimental Vita player framing, NOT decoded original iOS FOV/zoom.
 * Only perspective is updated, model original 2.2355 source height
 * and physical G75 player capsule NEVER scaled or touched. */
int b24_g164_camera_framing(float shoulder_weight,float *distance_multiplier,
                             float *vertical_fov_deg);
#endif
