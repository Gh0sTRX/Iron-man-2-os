#ifndef B24_G160_ORIGINAL_ROAD_SPATIAL_H
#define B24_G160_ORIGINAL_ROAD_SPATIAL_H
#include "b24_g159_real_source_road.h"
/* Optional CSR acceleration only: same 753 original road polygons, exact
 * G159 per-triangle Z math, same source order. On OOM index absent and
 * existing full G159 linear scan remains authoritative. */
int b24_g160_index_build(B24G159Road *r);
void b24_g160_index_close(B24G159Road *r);
int b24_g160_index_query(const B24G159Road *r,float x,float y,
                        uint32_t *begin,uint32_t *end);
#endif
