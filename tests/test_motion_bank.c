/* Exercise actual G83 selection + IM2V reader + G8 Mark V ownership.
 * Original assets optional; source-only checks never fabricate native controls. */
#include "b24_g83_unified_movement_aim.h"
#include "b24_g8_live_original_motion.h"
#include "im2_suit_profile.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const char *transitions[]={NULL,"ground_float","fly_start","fly_end","fly2ground","fly2run","fly_left_dodge","fly_right_dodge"};
static void markv_events(const char *root){
 float vertices[629*3]={0};B24G8LiveOriginalMotion actor={0};
 for(unsigned e=1;e<=7;e++){
  B24G83Input input={0};B24G83Selection choice={0};
  input.suit_index=4;input.transition=(B24G83Event)e;input.grounded_contact_verified=1;
  input.motion=e==1||e==3?B24G83_HOVER:e==4||e==5?B24G83_GROUND:B24G83_FLIGHT;
  assert(b24_g83_select_original_motion(&input,&choice));
  char stem[128];snprintf(stem,sizeof(stem),"ironman_ironman_%s",transitions[e]);
  if(!choice.stem)fprintf(stderr,"missing Mark V source transition: %s\n",stem);
  assert(choice.stem&&!strcmp(choice.stem,stem)&&choice.one_shot_not_looping&&choice.original_source_duration_ms);
  if(root){
   b24_g8_motion_release(&actor);
   const B24MotionStage stage=input.motion==B24G83_GROUND?B24M_LAND:input.motion==B24G83_HOVER?B24M_HOVER:B24M_CRUISE;
   assert(b24_g8_motion_tick_g84(&actor,root,vertices,12,629,4,stage,0,0,1000,choice.stem));
   snprintf(stem,sizeof(stem),"suitcase_ironman_%s",transitions[e]);
   assert(actor.active&&!actor.missing&&actor.stream.nv==629&&!strcmp(actor.selected,stem));
   assert(actor.stream.duration_ms==choice.original_source_duration_ms);
   assert(b24_g8_motion_tick_g84(&actor,root,vertices,12,629,4,stage,0,0,1050,choice.stem));
  }
  if(e==4||e==5){
   input.grounded_contact_verified=0;assert(b24_g83_select_original_motion(&input,&choice));
   assert(!choice.stem); /* Original stream is not permission to invent contact. */
  }
 }
 b24_g8_motion_release(&actor);
}
static void audit(const char *root){
 const float axis[][2]={{0,0},{0,1},{0,-1},{-1,0},{1,0}};
 unsigned checked=0;char seen[5][160][128];unsigned used[5]={0};
 for(int suit=0;suit<5;suit++)for(unsigned mode=0;mode<4;mode++)
  for(unsigned aim=0;aim<5;aim++)for(unsigned dir=0;dir<5;dir++)
   for(unsigned fire=0;fire<2;fire++)for(unsigned prev=0;prev<5;prev++){
    B24G83Input in={0};B24G83Selection out={0};
    in.suit_index=suit;in.motion=(B24G83Mode)mode;in.aim=(B24G83Aim)aim;
    in.axis_x=axis[dir][0];in.axis_y=axis[dir][1];in.accepted_weapon_event=(int)fire;
    in.previous_flight_dir=(B24G83Dir)prev;
    assert(b24_g83_select_original_motion(&in,&out));if(!out.stem)continue;
    char actual[128];
    snprintf(actual,sizeof(actual),suit==4?"suitcase_%s":"%s",suit==4?out.stem+8:out.stem);
    int duplicate=0;for(unsigned i=0;i<used[suit];i++)if(!strcmp(actual,seen[suit][i]))duplicate=1;
    if(duplicate)continue;
    assert(used[suit]<160);strcpy(seen[suit][used[suit]++],actual);
    B24OriginalIM2VStream stream={0};
    if(!b24_original_im2v_open(&stream,root,actual,im2_suit_source_vertices(suit)))fprintf(stderr,"missing/bad original stream: suit=%d %s\n",suit,actual);
    assert(stream.file);
    if(stream.duration_ms!=out.original_source_duration_ms)fprintf(stderr,"duration mismatch: %s metadata=%u IM2V=%u\n",actual,out.original_source_duration_ms,stream.duration_ms);
    assert(stream.duration_ms==out.original_source_duration_ms);
    float *xyz=malloc(stream.nv*3*sizeof(float));assert(xyz);
    assert(b24_original_im2v_sample(&stream,0,0,xyz));
    assert(b24_original_im2v_sample(&stream,stream.duration_ms/2,0,xyz));
    assert(b24_original_im2v_sample(&stream,stream.duration_ms,0,xyz));
    for(unsigned i=0;i<stream.nv*3;i++)assert(isfinite(xyz[i]));
    free(xyz);b24_original_im2v_close(&stream);checked++;
   }
 assert(checked>200);printf("PASS %u original suit/route streams: actual vertex banks, authored durations, first/middle/end samples\n",checked);
}
int main(int argc,char **argv){
 assert(argc==1||argc==2);if(argc==2)audit(argv[1]);markv_events(argc==2?argv[1]:NULL);
 puts("PASS Mark V authored transitions with source-contact guard; no new native input or weapon semantics");return 0;
}
