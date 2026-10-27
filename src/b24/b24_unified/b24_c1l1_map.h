#ifndef B24_C1L1_MAP_H
#define B24_C1L1_MAP_H
#include <stddef.h>
#include <stdint.h>
/* Original C1L1 source geometry, B17-compatible Z-up world.
 * Native little-endian 44 byte triangle records. No guessed original mission graph. */
typedef struct {
    float p[9]; /* three XYZ original vertices */
    uint32_t rgb, category; /* 0 ground; 1 urban; 2 vehicles; 3 lights */
} B24C1Triangle;
int b24_c1l1_load(const char *path);
void b24_c1l1_unload(void);
size_t b24_c1l1_count(void);
const B24C1Triangle *b24_c1l1_triangle(size_t index);
#endif
