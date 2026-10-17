/* G173 live source integration test with ORIGINAL owner 2010 IM2V assets
 * already reconstructed under work/animations from verified G9/G85.
 * No fake texture/animation input and NO Vita VPK. Vita hardware not tested.
 * Validate G169 3 phases -> EXACT G8 single-owner loaded native pose,
 * even when a previous legacy repulsor pose request is pending, and
 * Mark V already-correct suitcase source filename is not double-prefix.
 */
#include "b24_g8_live_original_motion.h"
#include "b24_g169_native_source_unibeam.h"
#include "b24_g173_authored_beam_priority.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {float x,y,z,u,v;} G173Vertex;
static void run(const char *original_asset_dir,int suit,int hover){
 const size_t nv=suit==4?629u:802u;
 G173Vertex *verts=calloc(nv,sizeof(*verts));
 assert(verts);
 B24G8LiveOriginalMotion stream={0};
 B24G169Beam beam={0};
 assert(b24_g169_native_beam_begin(&beam,suit,hover,1000u));
 const unsigned when[3]={
 1000u,1000u+(hover?600u:400u),1000u+(hover?1000u:800u)};
 for(unsigned i=0;i<3;i++){
  const char *name=b24_g169_native_beam_clip(&beam,suit,hover,
                                              hover?1:0,when[i]);
  assert(name&&b24_g173_is_authored_beam(suit,name));
  if(i==1)b24_g8_motion_repulsor_trigger(&stream,when[i]-1u);
  assert(b24_g8_motion_tick_g84(&stream,original_asset_dir,
                                verts,sizeof(*verts),nv,suit,
                                hover?B24M_HOVER:B24M_WALK,
                                0.f,0.f,when[i],name));
  assert(stream.active&&!stream.missing&&stream.stream.file);
  assert(strcmp(stream.selected,name)==0);
  assert(!stream.repulsor_pending);
  assert(!stream.whole_body_repulsor_active);
  assert(stream.stream.duration_ms>0);
  assert(stream.successful_frames==i+1u);
 }
 unsigned at=when[2]+50u;
 const char *name=b24_g169_native_beam_clip(&beam,suit,hover,
                                             hover?1:0,at);
 assert(name&&strstr(name,"beam3"));
 b24_g8_motion_melee_trigger(&stream,at);
 if(!hover){
  assert(b24_g8_motion_tick_g84(&stream,original_asset_dir,
                                verts,sizeof(*verts),nv,suit,
                                B24M_WALK,0.f,0.f,at,name));
  /* Existing G8 close-range melee must outrank Beam3; no extra fire. */
  assert(strstr(stream.selected,"ground_combo_1")!=NULL);
  assert(!stream.whole_body_repulsor_active);
 }
 printf("G173 original 2010 body frames suit=%d hover=%d three authentic Beam phases, one live G8 stream with valid IM2V body, no MarkV double-prefix\n",suit,hover);
 b24_g8_motion_release(&stream);
 free(verts);
}
int main(int argc,char **argv){
 if(argc!=2){fprintf(stderr,"Usage: test_g173_REAL_2010_IM2V_G169_G8_G85_full_host_owner work/animations\n");return 2;}
 run(argv[1],4,0);
 run(argv[1],4,1);
 run(argv[1],0,0);
 run(argv[1],0,1);
 puts("G173 original source host end-to-end PASS: native G169 12 real IM2V variants select and render via corrected G85, stale repulsor does not override; live Vita device still untested, NO VPK.");
 return 0;
}
