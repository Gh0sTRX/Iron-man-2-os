#include "b24_gpu_reticle.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
static uint32_t buf[480*272];
int main(void){
 B24ReticlePoint p=b24_reticle_position(0.f);
 assert(fabsf(p.x-278.f)<.01f&&fabsf(p.y-110.f)<.01f);
 p=b24_reticle_position(1.f);
 assert(fabsf(p.x-240.f)<.01f&&fabsf(p.y-136.f)<.01f);
 p=b24_reticle_position(.5f);
 assert(fabsf(p.x-259.f)<.01f&&fabsf(p.y-123.f)<.01f);
 b24_reticle_draw(buf,480,0.f,0,0);
 assert(buf[110*480+278+9]==0x55dff8u);
 b24_reticle_draw(buf,480,1.f,1,0);
 assert(buf[136*480+240+10]==0xe8bb5du);
 uint32_t snap=buf[136*480+240+10];
 b24_reticle_draw(buf,480,1.f,0,1);
 assert(buf[136*480+240+10]==snap);
 b24_reticle_draw(buf,480,.5f,0,0);
 assert(buf[123*480+259+7]==0x55dff8u);
 p=b24_reticle_position(NAN);
 assert(p.x==278.f&&p.y==110.f);
 p=b24_reticle_position(900.f);
 assert(p.x==240.f&&p.y==136.f);
 puts("PASS B24 crosshair: shoulder(278,110)->chase(240,136), smooth halfway, lock color, pause hidden, invalid inputs");
 return 0;
}
