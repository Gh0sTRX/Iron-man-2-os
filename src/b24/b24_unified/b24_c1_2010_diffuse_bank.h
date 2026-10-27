#ifndef B24_C1_2010_DIFFUSE_BANK_H
#define B24_C1_2010_DIFFUSE_BANK_H
#include <stdint.h>
/* Proven 2010 original BRES 88B material shader→60B sampler index→20B
   original TGA array, aligned against original C1MA 94 material IDs.
   Source C1MT 1 format: 20B header, 94*uint16 texture IDs, bank filenames.
   0xffff means genuinely missing/unverified original 2010 source sampler.
   UV-less 2284 light triangles remain fallback color. No guessed textures. */
#define B24_C1_2010_MATERIALS 94u
#define B24_C1_2010_ATLASES 40u
#define B24_C1_2010_LEGACY_ATLASES 39u
#define B24_C1_2010_NAME_MAX 76u
#define B24_C1_2010_NO_TEXTURE 65535u
typedef struct {
 uint16_t texture_for_material[B24_C1_2010_MATERIALS];
 char names[B24_C1_2010_ATLASES][B24_C1_2010_NAME_MAX];
 uint32_t gl_texture_ids[B24_C1_2010_ATLASES];
 uint32_t source_verified_count;
 uint32_t atlas_count; /* G12 39 or G13 40 original source atlases */
 int loaded;
} B24C1OriginalDiffuseBank;
int b24_c1_2010_diffuse_bank_load(B24C1OriginalDiffuseBank *out,const char *c1mt);
void b24_c1_2010_diffuse_bank_reset(B24C1OriginalDiffuseBank *out);
int b24_c1_2010_diffuse_bank_lookup(const B24C1OriginalDiffuseBank *b,
                                     unsigned material_id);
#endif
