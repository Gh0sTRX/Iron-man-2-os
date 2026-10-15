#include "b24_g10_practice_target.h"
#include <math.h>
B24G10PracticeTarget b24_g10_practice_target_at_floor(float ground_z){
 return (B24G10PracticeTarget){0.f,10.f,ground_z+1.0f,.46f,1,0.f};
}
int b24_g10_practice_target_valid(const B24G10PracticeTarget *t){
 return t&&isfinite(t->x)&&isfinite(t->y)&&isfinite(t->z)&&
        isfinite(t->radius)&&t->radius>.1f&&t->radius<2.f&&
        t->invulnerable==1;
}
