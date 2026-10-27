#include "b24_g8_wm_shoulder_gameplay.h"
#include <math.h>
#include <string.h>
#include <float.h>

static int finite3(B24WMVec3 v) {
 return isfinite(v.x)&&isfinite(v.y)&&isfinite(v.z);
}
static B24WMVec3 diff(B24WMVec3 a,B24WMVec3 b){
 B24WMVec3 v={a.x-b.x,a.y-b.y,a.z-b.z};return v;
}
static float squared(B24WMVec3 a){
 return a.x*a.x+a.y*a.y+a.z*a.z;
}
static B24WMVec3 unit(B24WMVec3 v){
 float n=sqrtf(squared(v));if(n<=1.e-6f){B24WMVec3 zero={0,0,1};return zero;}
 v.x/=n;v.y/=n;v.z/=n;return v;
}
static float decrease(float v,float dt){return v>dt?v-dt:0.f;}
void b24_wm_default_config(B24WMConfig *c){
 if(!c)return;
 c->skill_active_seconds=20.f;c->skill_cooldown_seconds=20.f;
 c->gatling_interval_seconds=.12f;c->gatling_range=24.f;
 c->missile_cooldown_seconds=2.0f;
}
int b24_wm_init(B24WMShoulder *a,const B24WMConfig *cfg){
 if(!a||!cfg||!isfinite(cfg->skill_active_seconds)||
    !isfinite(cfg->skill_cooldown_seconds)||
    !isfinite(cfg->gatling_interval_seconds)||
    !isfinite(cfg->gatling_range)||!isfinite(cfg->missile_cooldown_seconds)||
    cfg->skill_active_seconds<.1f||cfg->skill_active_seconds>120.f||
    cfg->skill_cooldown_seconds<0.f||cfg->skill_cooldown_seconds>120.f||
    cfg->gatling_interval_seconds<.02f||cfg->gatling_interval_seconds>5.f||
    cfg->gatling_range<.1f||cfg->gatling_range>1000.f||
    cfg->missile_cooldown_seconds<0.f||cfg->missile_cooldown_seconds>60.f)return 0;
 memset(a,0,sizeof(*a));a->config=*cfg;a->last_target_id=-1;return 1;
}
static void event(B24WMOutput *out,B24WMEventKind kind,int id,
                  B24WMVec3 origin,B24WMVec3 aim,float damage){
 if(out->event_count>=8)return;
 B24WMEvent *e=&out->events[out->event_count++];
 e->kind=kind;e->target_id=id;e->origin=origin;
 e->direction=unit(aim);e->damage=damage;
}
/* Independent turret: target selection ONLY uses right-muzzle world origin
   and actual entity visibility/occlusion, NEVER player's camera crosshair,
   heading or player-selected lock. Retain lock while legal to avoid thrashing.
   Original engine's precise acquisition and fire windows NOT recovered. */
static int select_target(const B24WMShoulder *a,const B24WMInput *in){
 if(!in->real_enemies_loaded||!in->targets||!in->target_count)return -1;
 float max2=a->config.gatling_range*a->config.gatling_range;
 int best=-1;float best2=FLT_MAX;
 for(size_t i=0;i<in->target_count;i++){
  const B24WMTarget *t=&in->targets[i];
  if(!t->alive||!t->visible||t->occluded||!finite3(t->center))continue;
  const float d2=squared(diff(t->center,in->muzzle_right_gatling));
  if(!isfinite(d2)||d2>max2)continue;
  if(t->id==a->last_target_id)return (int)i;
  if(d2<best2){best=(int)i;best2=d2;}
 }
 return best;
}
int b24_wm_tick(B24WMShoulder *a,const B24WMInput *in,B24WMOutput *out){
 if(!a||!in||!out||!isfinite(in->dt)||in->dt<0.f||in->dt>.2f||
    !finite3(in->muzzle_left_rocket)||
    !finite3(in->muzzle_right_gatling)||
    !finite3(in->rocket_aim_direction)||
    in->target_count>1024||(in->target_count&&!in->targets))return 0;
 memset(out,0,sizeof(*out));out->locked_target_id=-1;
 /* In a source-only G8 build with no real hostile actors this subsystem
    must NEVER create combat targets or claim damage/effects on its own. */
 if(!in->war_machine_selected){
  a->active_left=0.f;a->shot_left=0.f;a->last_target_id=-1;
  a->cooldown_left=decrease(a->cooldown_left,in->dt);
  a->missile_left=decrease(a->missile_left,in->dt);
  out->ready=a->cooldown_left==0.f;out->cooldown_left=a->cooldown_left;
  return 1;
 }
 float prev_active=a->active_left;
 a->active_left=decrease(a->active_left,in->dt);
 a->missile_left=decrease(a->missile_left,in->dt);
 if(prev_active>0.f&&a->active_left==0.f){
  a->cooldown_left=a->config.skill_cooldown_seconds;
  a->last_target_id=-1;
 }
 if(prev_active==0.f)
  a->cooldown_left=decrease(a->cooldown_left,in->dt);
 if(in->trigger_skill_edge&&a->active_left==0.f&&a->cooldown_left==0.f){
  a->active_left=a->config.skill_active_seconds;
  a->shot_left=0.f;a->last_target_id=-1;
 }
 if(in->trigger_missile_edge&&a->missile_left==0.f){
  a->missile_left=a->config.missile_cooldown_seconds;
  /* Only gun-origin emissions: missile flight, smoke simulation and
     impact hit checks belong to a separate real-entities system. */
  event(out,B24WM_EVENT_MISSILE_LAUNCH_LEFT,-1,
        in->muzzle_left_rocket,in->rocket_aim_direction,0.f);
  event(out,B24WM_EVENT_MISSILE_EXHAUST_LEFT,-1,
        in->muzzle_left_rocket,in->rocket_aim_direction,0.f);
  a->fired_missiles++;
 }
 if(a->active_left>0.f){
  int picked=select_target(a,in);
  if(picked>=0){
   const B24WMTarget *target=&in->targets[picked];
   out->locked_target_id=target->id;
   if(a->last_target_id!=target->id){a->last_target_id=target->id;a->locks++;}
   if(a->shot_left<=0.f){
    B24WMVec3 direction=diff(target->center,in->muzzle_right_gatling);
    event(out,B24WM_EVENT_GATLING_SHOT_RIGHT,target->id,
          in->muzzle_right_gatling,direction,1.f);
    event(out,B24WM_EVENT_GATLING_SPARK_RIGHT,target->id,
          in->muzzle_right_gatling,direction,0.f);
    a->shot_left=a->config.gatling_interval_seconds;
    a->fired_gatling++;
   }else a->shot_left=decrease(a->shot_left,in->dt);
  }else{
   a->shot_left=0.f;a->last_target_id=-1;
  }
 }
 out->active=a->active_left>0.f;out->active_left=a->active_left;
 out->cooldown_left=a->cooldown_left;out->ready=!out->active&&a->cooldown_left==0.f;
 return 1;
}
