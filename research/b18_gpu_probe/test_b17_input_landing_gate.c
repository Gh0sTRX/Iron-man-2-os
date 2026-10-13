#include "b17_input_landing_gate.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
int main(void){B17GateConfig c;B17GateState s;B17GateInput i={0};
 b17_gate_defaults(&c);b17_gate_init(&s);
 assert(c.run_enter>.90f&&c.flight_enter>.90f);
 i.stick_forward=.78f;
 b17_gate_step(&s,&c,&i);assert(!s.is_ground_running);
 i.stick_forward=.95f;b17_gate_step(&s,&c,&i);assert(!s.is_ground_running);
 i.stick_forward=.98f;b17_gate_step(&s,&c,&i);assert(s.is_ground_running);
 i.stick_forward=.91f;b17_gate_step(&s,&c,&i);assert(s.is_ground_running);
 i.stick_forward=.86f;b17_gate_step(&s,&c,&i);assert(!s.is_ground_running);
 i.airborne=1;i.stick_forward=.85f;b17_gate_step(&s,&c,&i);assert(!s.is_fast_flight);
 i.stick_forward=.97f;b17_gate_step(&s,&c,&i);assert(s.is_fast_flight);
 i.stick_forward=.90f;b17_gate_step(&s,&c,&i);assert(s.is_fast_flight);
 i.stick_forward=.84f;b17_gate_step(&s,&c,&i);assert(!s.is_fast_flight);
 i.stick_forward=0.f;i.stick_x=1.f;b17_gate_step(&s,&c,&i);assert(!s.is_fast_flight);
 i.landing_requested=1;i.ground_valid=1;i.feet_world_z=2.f;i.ground_world_z=-1.f;
 i.vertical_velocity_z=-.5f;b17_gate_step(&s,&c,&i);assert(s.landing_pending&&!s.landing_event);
 i.landing_requested=0;i.feet_world_z=-.9f;b17_gate_step(&s,&c,&i);assert(!s.landing_event);
 i.feet_world_z=-.98f;i.vertical_velocity_z=1.f;
 b17_gate_step(&s,&c,&i);assert(!s.landing_event);
 i.vertical_velocity_z=-.08f;b17_gate_step(&s,&c,&i);assert(s.landing_event&&!s.landing_pending);
 b17_gate_step(&s,&c,&i);assert(!s.landing_event);
 i.feet_world_z=-.98f;i.landing_requested=1;i.ground_valid=0;
 b17_gate_step(&s,&c,&i);assert(!s.landing_event);
 i.ground_valid=1;b17_gate_step(&s,&c,&i);assert(s.landing_event);
 uint32_t rng=0xa11c2026u;
 for(int k=0;k<20000;k++){
  rng=rng*1664525u+1013904223u;i.stick_forward=(float)((int)(rng%251u)-125)/100.f;
  rng=rng*1664525u+1013904223u;i.stick_x=(float)((int)(rng%251u)-125)/100.f;
  i.landing_requested=(int)((rng>>5)&1u);i.ground_valid=(int)((rng>>6)&1u);
  i.airborne=(int)((rng>>7)&1u);
  i.feet_world_z=(float)((int)(rng%201u)-100)/100.f-1.f;
  i.ground_world_z=-1.f;i.vertical_velocity_z=(rng&1u)?-.1f:.1f;
  b17_gate_step(&s,&c,&i);
  assert((s.is_ground_running==0)||(i.airborne==0));
  assert(!s.landing_event || i.airborne);
  assert(!s.landing_event || i.ground_valid);
  assert(!s.landing_event || fabsf(i.feet_world_z-i.ground_world_z)<=c.contact_tolerance);
 }
 puts("PASS B17 control/landing host lab: full-stick hysteresis, no pre-contact landing, 20000 fuzz");return 0;}
