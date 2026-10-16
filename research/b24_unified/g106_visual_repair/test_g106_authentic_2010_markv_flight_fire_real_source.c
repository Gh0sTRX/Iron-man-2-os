/* G106 verify original 2010 owner Mark V source 629v 20Hz fly_att_s
 * for real B16 accepted stage2 and RUSH action; no synthetic animation
 * and no true iOS weapon-ID/damage claim. Source G85 G8 one actor owner.
 */
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef struct {float xyz[3],u,v;} Vtx;
static Vtx verts[629];
static int frame(B24G8LiveOriginalMotion *a,const char *dir,
 uint32_t now,B24MotionStage stage,const char *route){
 for(unsigned i=0;i<629;i++){
  verts[i].xyz[0]=.003f*(float)i;verts[i].xyz[1]=0;verts[i].xyz[2]=1.f;
 }
 return b24_g8_motion_tick_g84(a,dir,verts,sizeof(Vtx),629u,4,
                               stage,0.f,1.f,now,route);
}
static void run_case(const char *dir,B24MotionStage stage,const char *locomotion) {
 B24G8LiveOriginalMotion actor={0};
 assert(frame(&actor,dir,100,stage,locomotion));
 assert(actor.active&&!actor.missing);
 assert(strcmp(actor.selected,"suitcase_ironman_fly_att_s")!=0);
 const unsigned before=actor.transitions;
 b24_g8_motion_repulsor_trigger(&actor,200);
 assert(actor.repulsor_pending);
 assert(frame(&actor,dir,201,stage,locomotion));
 assert(actor.active&&!actor.missing);
 assert(strcmp(actor.selected,"suitcase_ironman_fly_att_s")==0);
 assert(actor.stream.duration_ms==1600u);
 assert(actor.stream.nv==629u&&actor.stream.frames==33u);
 assert(actor.repulsor_pending);
 assert(b24_g8_motion_whole_body_fire(&actor));
 assert(actor.transitions==before+1);
 assert(frame(&actor,dir,1800,stage,locomotion));
 assert(b24_g8_motion_whole_body_fire(&actor));
 assert(frame(&actor,dir,1801,stage,locomotion));
 char expected[160];snprintf(expected,sizeof(expected),"suitcase_%s",locomotion+8);
 assert(strcmp(actor.selected,expected)==0);
 assert(!actor.repulsor_pending);
 assert(!b24_g8_motion_whole_body_fire(&actor));
 assert(actor.transitions==before+2);
 assert(frame(&actor,dir,1810,stage,locomotion));
 assert(actor.transitions==before+2);
 b24_g8_motion_release(&actor);
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 run_case(argv[1],B24M_CRUISE,"ironman_ironman_fly_f");
 run_case(argv[1],B24M_RUSH,"ironman_ironman_fly_f_rush");
 puts("G106 PASS authenticated actual 2010 Mark V 629v 33-frame flight fullbody attack on accepted Stage2 and RUSH repulsor source event; one return-to-flight, no 2010 Damage claim.");
 return 0;
}
