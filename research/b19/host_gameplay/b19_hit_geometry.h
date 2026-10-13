#ifndef B19_HIT_GEOMETRY_H
#define B19_HIT_GEOMETRY_H
#ifdef __cplusplus
extern "C" {
#endif

typedef struct {float x,y,z;} B19Point3;
typedef struct {int hit;float fraction;} B19SegmentHit;
/* Closed segment, bounded sphere; unlike a point hit this detects fast projectiles
   crossing a target between frames. No engine or PS Vita SDK dependencies. */
B19SegmentHit b19_segment_sphere(B19Point3 start, B19Point3 end,
                                 B19Point3 center,float radius);
#ifdef __cplusplus
}
#endif
#endif
