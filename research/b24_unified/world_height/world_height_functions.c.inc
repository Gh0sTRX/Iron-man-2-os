/* B14_WORLD_HEIGHT_SUPPORT: helpers only change B14 intent/contact state.
 * B14 tick remains the sole integrator; G75 alone accepts source collision.
 * .8 / .35 / 36 / 7 are existing PORT prototype values, not iOS discoveries. */
void b14_world_toggle_flight(B14World *w){
 if(!w)return;
#ifndef B24_G75_SOURCE_CAPSULE
 /* Standalone B14 still has its explicit Z=0 playground and no G75 owner. */
 w->flying=!w->flying;
 w->target_z=w->flying?fmaxf(w->target_z,.8f):0.f;
#else
 if(!w->flying){
  w->flying=1;
  w->flight_base_z=w->z;
  w->target_z=w->z+.8f;
 }else{
  w->flying=0;
  w->target_z=w->z;
 }
 w->ground_supported=0;
#endif
}
void b14_world_accept_ground_support(B14World *w,int found,float support_z){
 if(!w)return;
 w->ground_supported=!w->flying&&found&&isfinite(support_z)&&
                       fabsf(w->z-support_z)<=.0001f;
 if(w->ground_supported){
  w->ground_z=support_z;
  w->target_z=support_z;
 }
}
