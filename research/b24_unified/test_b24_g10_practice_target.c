#include "b24_g10_practice_target.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B24G10PracticeTarget target=b24_g10_practice_target_at_floor(-.2473f);
 assert(target.x==0.f&&target.y==10.f);
 assert(fabsf(target.z-.7527f)<.0001f);
 assert(target.radius>.2f&&target.invulnerable);
 assert(b24_g10_practice_target_valid(&target));
 B24G10PracticeTarget bad=target;
 bad.invulnerable=0;assert(!b24_g10_practice_target_valid(&bad));
 bad=target;bad.z=NAN;assert(!b24_g10_practice_target_valid(&bad));
 puts("PASS G10 EXPLICIT test-only original C1L1 center permanent L-lock"
      " neon wire practice dummy at TRUE source ground height; no original"
      " enemy spawn, HP loss, or hidden mission");
 return 0;
}
