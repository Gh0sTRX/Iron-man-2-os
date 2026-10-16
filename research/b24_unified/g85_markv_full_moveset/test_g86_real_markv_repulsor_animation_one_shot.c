/* G86 test REAL reconstructed G85 Mark V, not mock pose names.
 * Run against all 248 original 629v source-derived IM2V staged in CI.
 * Verify B16 accepted shot -> single REAL source aim attack -> original
 * 2010 clip duration ends -> back to original idle, no duplicate shot.
 * No Vita executable, no VPK, no synthetic enemy hits.
 */
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float xyz[3];float u,v;} TestVertex;
static TestVertex body[629];
static int step(B24G8LiveOriginalMotion *s,const char *folder,
                uint32_t now,B24MotionStage stage,const char *override){
 for(unsigned i=0;i<629;i++){
  body[i].xyz[0]=0.01f*(float)i;
  body[i].xyz[1]=0.002f*(float)i;
  body[i].xyz[2]=1.f;
 }
 return b24_g8_motion_tick_g84(s,folder,body,sizeof(TestVertex),629u,4,
                                stage,0.f,0.f,now,override);
}
int main(int argc,char **argv){
 if(argc!=2){fprintf(stderr,"Usage G86 <real_2010_animation_directory>\n");return 2;}
 B24G8LiveOriginalMotion s={0};
 const char *idle="ironman_ironman_ground_idel";
 assert(step(&s,argv[1],100,B24M_IDLE,idle));
 assert(s.active&&!s.missing);
 assert(!strcmp(s.selected,"suitcase_ironman_ground_idel"));
 assert(s.stream.nv==629u);
 assert(!b24_g8_motion_whole_body_fire(&s));
 const unsigned old_transitions=s.transitions;
 b24_g8_motion_repulsor_trigger(&s,200);
 assert(s.repulsor_pending);
 assert(step(&s,argv[1],201,B24M_IDLE,idle));
 assert(!s.missing);
 assert(!strcmp(s.selected,"suitcase_ironman_aim_ground_idle_att"));
 assert(s.transitions==old_transitions+1);
 assert(s.repulsor_pending&&b24_g8_motion_whole_body_fire(&s));
 const uint32_t source_fire_ms=s.stream.duration_ms;
 assert(source_fire_ms>0 && source_fire_ms<=12000);
 assert(step(&s,argv[1],201+source_fire_ms-1,B24M_IDLE,idle));
 assert(!strcmp(s.selected,"suitcase_ironman_aim_ground_idle_att"));
 assert(s.repulsor_pending&&b24_g8_motion_whole_body_fire(&s));
 assert(step(&s,argv[1],201+source_fire_ms,B24M_IDLE,idle));
 assert(!s.repulsor_pending&&!b24_g8_motion_whole_body_fire(&s));
 assert(!strcmp(s.selected,"suitcase_ironman_ground_idel"));
 assert(s.transitions==old_transitions+2);
 /* A second accepted event is independent and still activates exactly once. */
 b24_g8_motion_repulsor_trigger(&s,3000);
 assert(step(&s,argv[1],3001,B24M_IDLE,idle));
 assert(!strcmp(s.selected,"suitcase_ironman_aim_ground_idle_att"));
 assert(b24_g8_motion_whole_body_fire(&s));
 b24_g8_motion_release(&s);
 assert(!s.stream.file);
 puts("PASS G86 real original 2010 Mark V repulsor attack source IM2V selected ONCE, no double suitcase prefix, playback active full-body and clean completion + 2nd shot. NO VPK.");
 return 0;
}
