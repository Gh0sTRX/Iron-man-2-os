#include "../b21_controls/b21_control_lab.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

/* On the device B24-C2 accidentally converted an unconditional BUTTONDOWN
 * into IM2_BT_START, hence every controller key launched pause. This
 * host test checks the actual unified control state behavior. Separately,
 * test_b24_input_patch.py checks the generated SDL event mapping guard. */
static void next(Im2Controls *c,uint32_t key){
    im2_controls_tick(c,0,0.f,0.f,0.f,0.f);
    im2_controls_tick(c,key,0.f,0.f,0.f,0.f);
}
int main(void){
 Im2Controls c;
 im2_controls_init(&c);
 assert(c.state==IM2_PLAYING);
 uint32_t others[]={
   IM2_BT_R,IM2_BT_L,IM2_BT_SQUARE,IM2_BT_TRIANGLE,
   IM2_BT_CIRCLE,IM2_BT_CROSS,IM2_BT_DUP,IM2_BT_DDOWN,
   IM2_BT_DLEFT,IM2_BT_DRIGHT,IM2_BT_SELECT
 };
 for(unsigned i=0;i<sizeof(others)/sizeof(*others);i++){
     next(&c,others[i]);
     assert(c.state==IM2_PLAYING);
 }
 next(&c,IM2_BT_START);
 assert(c.state==IM2_PAUSED);
 /* All other buttons except the explicitly designed CIRCLE resume shortcut
  * MUST NOT toggle paused state. */
 for(unsigned i=0;i<sizeof(others)/sizeof(*others);i++){
    if(others[i]==IM2_BT_CIRCLE)continue;
    next(&c,others[i]);
    assert(c.state==IM2_PAUSED);
 }
 next(&c,IM2_BT_START);
 assert(c.state==IM2_PLAYING);
 next(&c,IM2_BT_START);
 assert(c.state==IM2_PAUSED);
 next(&c,IM2_BT_CIRCLE);
 assert(c.state==IM2_PLAYING);
 puts("PASS B24 regression: ONLY START enters pause; Circle resumes; all other controller inputs stable");
 return 0;
}
