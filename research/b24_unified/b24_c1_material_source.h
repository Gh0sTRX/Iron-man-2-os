#ifndef B24_C1_MATERIAL_SOURCE_H
#define B24_C1_MATERIAL_SOURCE_H
#include <stddef.h>
#include <stdint.h>
/* True 2010 BDAE triangle->source material NAME (not a diffuse texture).
   C1MA authentic 370 mesh partitions exactly cover 37946 GPU vertices and
   22919 triangles. File-scope material identity is preserved; no guessed
   texture mappings/UV orientation/illumination assignment. */
#define B24_C1_MAT_NMESH 370u
#define B24_C1_MAT_NTRI 22919u
#define B24_C1_MAT_NVERT 37946u
#define B24_C1_MAT_NLABEL 94u
typedef struct {
 uint32_t group,first_vertex,vertex_count,first_triangle,triangle_count;
} B24C1MatMesh;
typedef struct {
 B24C1MatMesh meshes[B24_C1_MAT_NMESH];
 uint16_t *triangle_material;
 char **labels;
 uint32_t nmaterials;
 size_t material_bytes;
 int loaded;
} B24C1MaterialSource;
int b24_c1_material_source_load(B24C1MaterialSource *out,const char *path);
void b24_c1_material_source_free(B24C1MaterialSource *out);
/* True source identity, not guessed atlas. NULL for invalid index. */
const char *b24_c1_material_label(const B24C1MaterialSource *src,uint16_t mat_id);
#endif
