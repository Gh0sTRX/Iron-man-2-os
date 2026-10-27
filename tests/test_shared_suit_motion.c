/* Synthetic motion bytes test bank routing and event ownership, not native
 * input/combat or original animation quality. Asset layout has a separate test. */
#include "b24_g8_live_original_motion.h"
#include "b24_g83_unified_movement_aim.h"
#include "b24_g169_native_source_unibeam.h"
#include "im2_suit_profile.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float x,y,z,u,v;} Vertex;
static void clip(const char *name){
 char path[200];snprintf(path,sizeof(path),"%s.im2v",name);
 FILE *f=fopen(path,"wb");assert(f);
 const uint32_t h[]={0x56324d49u,802,5,20,200};
 assert(fwrite(h,sizeof(h),1,f)==1);
 for(unsigned t=0;t<5;t++)for(unsigned i=0;i<802;i++){
  const float xyz[]={.001f*(float)i,.02f*(float)t,1.f};
  assert(fwrite(xyz,sizeof(xyz),1,f)==1);
 }
 assert(fclose(f)==0);
}
int main(void){
 const char *names[]={"ironman_ironman_walk_f","ironman_ironman_aim_ground_move_f_att"};
 for(unsigned i=0;i<2;i++)clip(names[i]);
 Vertex *vertices=calloc(802,sizeof(*vertices));assert(vertices);
 B24G8LiveOriginalMotion actor={0};
 const int suits[]={0,1,3};
 for(unsigned j=0;j<3;j++){
  const int suit=suits[j];
  B24G83Input input={0};B24G83Selection choice={0};
  input.suit_index=suit;input.motion=B24G83_GROUND;input.axis_y=1.f;
  assert(b24_g83_select_original_motion(&input,&choice));
  assert(choice.stem&&!strcmp(choice.stem,names[0])&&!choice.needs_2010_hit_event);
  assert(b24_g8_motion_tick_g84(&actor,".",vertices,sizeof(*vertices),802,suit,
                              B24M_WALK,0,1,1000+j*100,choice.stem));
  assert(actor.active&&!actor.missing&&actor.suit_index==suit);
  assert(!actor.repulsor_pending&&!b24_g8_motion_whole_body_fire(&actor));
  b24_g8_motion_repulsor_trigger(&actor,1001+j*100);
  assert(b24_g8_motion_tick_g84(&actor,".",vertices,sizeof(*vertices),802,suit,
                              B24M_WALK,0,1,1016+j*100,choice.stem));
  assert(actor.repulsor_pending&&b24_g8_motion_whole_body_fire(&actor));
  B24G169Beam beam={0};assert(b24_g169_native_beam_begin(&beam,suit,0,1000));
  assert(!strcmp(b24_g169_native_beam_clip(&beam,suit,0,0,1450),"ironman_ironman_aim_ground_beam2"));
 }
 unsigned char before[sizeof(actor)];memcpy(before,&actor,sizeof(actor));
 char bad[140];memset(bad,'a',sizeof(bad)-1);bad[sizeof(bad)-1]=0;
 assert(!b24_g8_motion_tick_g84(&actor,".",vertices,sizeof(*vertices),802,0,
                             B24M_WALK,0,1,2000,bad));
 assert(!memcmp(before,&actor,sizeof(actor))); /* no stream/owner mutation */
 assert(!b24_g8_motion_tick_g84(&actor,".",vertices,sizeof(*vertices),802,0,
                             B24M_WALK,0,1,2000,"../bad"));
 assert(!memcmp(before,&actor,sizeof(actor)));
 assert(im2_suit_source_vertices(2)==1292&&im2_suit_source_vertices(4)==629);
 assert(im2_suit_source_vertices(-1)==0&&!b24_g8_motion_route(99,B24M_WALK,0,1));
 b24_g8_motion_release(&actor);free(vertices);
 for(unsigned i=0;i<2;i++){
  char path[200];snprintf(path,sizeof(path),"%s.im2v",names[i]);assert(remove(path)==0);
 }
 puts("PASS shared 802v pose bank: VI/IV/Stealth, actual owner retained, no shot leakage, atomic invalid-route rejection");
 return 0;
}
