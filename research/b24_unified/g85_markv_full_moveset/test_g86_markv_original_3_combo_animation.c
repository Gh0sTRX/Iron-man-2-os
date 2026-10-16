/* G86B: verify real G85 original 2010 Mark V 629-skinned IM2V clips
 * play through full original 3-combo and authored source durations.
 * This tests G8 animation state ONLY, not genuine hit-active frames or AI.
 * Full previous G73 physics & G68 Expo preserved; NO VPK.
 */
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float xyz[3];float uv[2];} Vertex;
static Vertex vertices[629];
static int tick(B24G8LiveOriginalMotion *s,const char *dir,
                uint32_t now){
 for(unsigned i=0;i<629;i++){
  vertices[i].xyz[0]=(float)i*.02f;
  vertices[i].xyz[1]=(float)i*.01f;
  vertices[i].xyz[2]=1.f;
 }
 return b24_g8_motion_tick_g84(s,dir,vertices,sizeof(vertices[0]),629u,
     4,B24M_IDLE,0.f,0.f,now,"ironman_ironman_ground_idel");
}
static void check(B24G8LiveOriginalMotion *m,const char *stem){
 assert(m->active&&!m->missing&&m->stream.file);
 if(strcmp(m->selected,stem)!=0){
  fprintf(stderr,"G86B wrong native Mark V phase expected %s got %s\n",stem,m->selected);
  exit(2);
 }
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 B24G8LiveOriginalMotion a={0};
 assert(tick(&a,argv[1],100u));
 check(&a,"suitcase_ironman_ground_idel");
 b24_g8_motion_melee_trigger(&a,200u);
 assert(tick(&a,argv[1],201u));
 check(&a,"suitcase_ironman_ground_combo_1");
 assert(a.melee.phase==1u&&a.stream.duration_ms==266u);
 assert(b24_g8_motion_melee_source_active(&a));
 b24_g8_motion_melee_trigger(&a,220u); /* buffered next combo */
 assert(tick(&a,argv[1],465u));
 check(&a,"suitcase_ironman_ground_combo_1");
 assert(tick(&a,argv[1],466u));
 check(&a,"suitcase_ironman_ground_combo_2");
 assert(a.melee.phase==2u&&a.stream.duration_ms==300u);
 b24_g8_motion_melee_trigger(&a,500u);
 assert(tick(&a,argv[1],766u));
 check(&a,"suitcase_ironman_ground_combo_3");
 assert(a.melee.phase==3u&&a.stream.duration_ms==500u);
 assert(tick(&a,argv[1],1266u));
 check(&a,"suitcase_ironman_ground_idel");
 assert(a.melee.phase==0u&&!b24_g8_motion_melee_source_active(&a));
 assert(a.melee.completed_attacks==3u);
 assert(!a.repulsor_pending&&!b24_g8_motion_whole_body_fire(&a));
 b24_g8_motion_release(&a);
 puts("PASS G86B genuine original Mark V 629v G8 real animation file 266/300/500ms combo 1->2->3->idle, buffered inputs, no repeated projectile or invented damage, NO VPK");
 return 0;
}
