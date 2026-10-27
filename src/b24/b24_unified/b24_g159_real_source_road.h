#ifndef B24_G159_REAL_SOURCE_ROAD_H
#define B24_G159_REAL_SOURCE_ROAD_H
#include <stdint.h>
/* C1L1 G66M original city GPU atlas 12: independently byte-identical
 * to 2010 iOS original PVR "c1l1_road.tga" (G158). This candidate
 * ground is opt-in; original iOS road SOLID bit still unproven.
 * No fake triangles, no floor snapping beyond existing G75 +/- .5.
 */
typedef struct {float p[9],minx,maxx,miny,maxy,minz,maxz;} B24G159RoadFace;
typedef struct {
 B24G159RoadFace *faces;
 uint32_t count,ready;
 /* G160 precomputed, exactly indexed original road XYZ; optional
  * accelerator, NEVER an alternative collider or gameplay owner.
  * On OOM/oversize builds, legacy full scan remains exact. */
 float cell_origin_x,cell_origin_y;
 uint32_t cell_cols,cell_rows,cell_ref_count;
 uint32_t *cell_offsets,*cell_face_ids;
 uint32_t spatial_index_ready;
} B24G159Road;
int b24_g159_road_open(B24G159Road *r,const char *source_g66m);
void b24_g159_road_close(B24G159Road *r);
int b24_g159_road_near(const B24G159Road *r,float x,float y,float footz,float *support);
int b24_g159_road_crossed(const B24G159Road *r,float x,float y,float oldz,float newz,float *support);
#endif
