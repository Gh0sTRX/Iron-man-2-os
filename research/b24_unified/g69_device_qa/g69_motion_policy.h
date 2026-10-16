#ifndef IM2_G69_MOTION_POLICY_H
#define IM2_G69_MOTION_POLICY_H
/* Source-only G69 direction selector.
 * One state chosen per physics tick; NO new position integration, so existing
 * source-triangle G67 collision cannot be double-integrated. Original clip
 * identities are copied from audited Iron Man 2010 248-entry catalog.
 * Pose/orientation/bone parity still requires an actual Vita capture.
 */
#include <math.h>
typedef enum { G69_GROUND=0,G69_HOVER=1,G69_CRUISE=2,G69_RUSH=3 } G69Stage;
typedef enum { G69_STOP=0,G69_FORWARD=1,G69_BACK=2,G69_LEFT=3,G69_RIGHT=4 } G69Direction;
typedef struct {float stick_x,stick_y;G69Stage stage;int fire,melee;} G69Input;
typedef struct {G69Direction direction;const char *original_anim;int one_shot;int fire_requested;int melee_requested;} G69Playback;
static inline G69Direction g69_dir(float x,float y){
 if(!isfinite(x)||!isfinite(y)||fabsf(x)>1.001f||fabsf(y)>1.001f)return G69_STOP;
 if(fmaxf(fabsf(x),fabsf(y))<.18f)return G69_STOP;
 if(fabsf(x)>fabsf(y))return x<0?G69_LEFT:G69_RIGHT;
 return y<0?G69_BACK:G69_FORWARD;
}
static inline G69Playback g69_select(G69Input in){
 static const char * const ground[5]={
  "IronMan_Ground_Idel.anim","IronMan_Walk_F.anim","IronMan_Walk_B.anim",
  "IronMan_Walk_L.anim","IronMan_Walk_R.anim"};
 static const char * const hover[5]={
  "IronMan_Aim_Float_idle.anim","IronMan_Aim_Float_move_F.anim",
  "IronMan_Aim_Float_move_B.anim","IronMan_Aim_Float_move_L.anim",
  "IronMan_Aim_Float_move_R.anim"};
 static const char * const cruise[5]={
  "IronMan_Aim_Float_idle.anim","Ironman_Fly_F.anim","Ironman_Fly_B.anim",
  "Ironman_Fly_L.anim","Ironman_Fly_R.anim"};
 G69Playback out={0};out.direction=g69_dir(in.stick_x,in.stick_y);
 if(in.stage<G69_GROUND||in.stage>G69_RUSH)return out;
 out.fire_requested=!!in.fire;out.melee_requested=!!in.melee;
 if(in.melee&&in.stage==G69_GROUND){
  out.original_anim="IronMan_Ground_Combo_1.anim";out.one_shot=1;return out;
 }
 /* These are source-authentic full-body poses, not guaranteed original
  * repulsor upper-body overlays. An actual right-arm masked blend is required. */
 if(in.fire&&in.stage==G69_GROUND&&out.direction==G69_STOP){
  out.original_anim="Ironman_Aim_Ground_idle_Att.anim";
  out.one_shot=1;return out;
 }
 switch(in.stage){
 case G69_GROUND:out.original_anim=ground[out.direction];break;
 case G69_HOVER:out.original_anim=hover[out.direction];break;
 case G69_CRUISE:out.original_anim=cruise[out.direction];break;
 case G69_RUSH:
  /* Do not run forward RUSH pose for backward/sideways analog! */
  out.original_anim=out.direction==G69_FORWARD?
   "Ironman_Fly_F_RUSH.anim":cruise[out.direction];break;
 }
 return out;
}
#endif
