#include "b17_input_landing_gate.h"
#include <math.h>
#include <string.h>
static float limited(float a){return !isfinite(a)?0.f:a>1.f?1.f:a< -1.f?-1.f:a;}
void b17_gate_defaults(B17GateConfig *c){if(c)*c=(B17GateConfig){.run_enter=.96f,.run_exit=.88f,
  .flight_enter=.96f,.flight_exit=.88f,.min_forward=.55f,.contact_tolerance=.08f};}
void b17_gate_init(B17GateState *s){if(s)memset(s,0,sizeof(*s));}
void b17_gate_step(B17GateState *s,const B17GateConfig *c,const B17GateInput *in){
 if(!s||!c||!in)return;
 float x=limited(in->stick_x),y=limited(in->stick_forward);
 float magnitude=fminf(1.f,sqrtf(x*x+y*y));
 s->landing_event=0;
 if(!in->airborne){
   s->is_fast_flight=0;s->landing_pending=0;
   s->is_ground_running=magnitude>=(s->is_ground_running?c->run_exit:c->run_enter);
   return;
 }
 s->is_ground_running=0;
 s->is_fast_flight=(y>=c->min_forward &&
        magnitude>=(s->is_fast_flight?c->flight_exit:c->flight_enter));
 if(in->landing_requested)s->landing_pending=1;
 /* Z-up in B17. Never play landing before signed feet gap reaches level geometry. */
 float gap=in->feet_world_z-in->ground_world_z;
 if(s->landing_pending&&in->ground_valid&&isfinite(gap)&&
    gap>=-c->contact_tolerance&&gap<=c->contact_tolerance&&
    isfinite(in->vertical_velocity_z)&&in->vertical_velocity_z<=.02f){
     s->landing_event=1;s->landing_pending=0;s->is_fast_flight=0;
 }
}
