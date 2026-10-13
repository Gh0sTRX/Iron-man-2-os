#include "b19_hit_geometry.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
    B19Point3 o={0,0,0},a={100,0,0},center={50,0,0};
    B19SegmentHit h=b19_segment_sphere(o,a,center,1.f);
    assert(h.hit && fabsf(h.fraction-.49f)<.001f); /* prevents 100m-frame tunneling */
    assert(!b19_segment_sphere(o,(B19Point3){-100,0,0},center,1.f).hit);
    assert(!b19_segment_sphere(o,a,(B19Point3){50,5,0},1.f).hit);
    assert(b19_segment_sphere(center,center,center,1.f).hit);
    assert(!b19_segment_sphere(o,o,(B19Point3){5,0,0},1.f).hit);
    assert(!b19_segment_sphere(o,a,center,-1.f).hit);
    assert(!b19_segment_sphere(o,a,center,NAN).hit);
    assert(!b19_segment_sphere((B19Point3){NAN,0,0},a,center,1.f).hit);
    h=b19_segment_sphere((B19Point3){0,0,0},(B19Point3){5,0,0},(B19Point3){6,0,0},1.f);
    assert(h.hit && fabsf(h.fraction-1.f)<.0001f); /* tangent at endpoint */
    puts("PASS B19 sweep: high-speed hit, miss, behind, inside, finite guards, tangent");
    return 0;
}
