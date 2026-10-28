#include "im2_gameplay_clock.h"
#include "b24_g83_authentic_timed_router.h"
#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void clip(const char *name){
 char path[256];snprintf(path,sizeof(path),"%s.im2v",name);FILE *f=fopen(path,"wb");assert(f);
 const uint32_t header[]={0x56324d49,802,5,20,200};assert(fwrite(header,1,20,f)==20);
 for(unsigned t=0;t<5;t++)for(unsigned i=0;i<802;i++){
  const float v[]={(float)t,(float)i,0.f};assert(fwrite(v,1,12,f)==12);
 }
 assert(!fclose(f));
}
int main(void){
 Im2GameplayClock clock={0};B24G83Timeline timeline={0};B24G83Input in={0};B24G83Selection selected;
 in.suit_index=0;in.motion=B24G83_FLIGHT;in.axis_x=-1.f;in.previous_flight_dir=B24G83_DIR_F;
 uint32_t now=im2_gameplay_clock_tick(&clock,1000,0);
 assert(b24_g83_timeline_tick(&timeline,NULL,now,&in,&selected));
 assert(selected.one_shot_not_looping&&!strcmp(selected.stem,"ironman_ironman_fly_ftol"));
 assert(im2_gameplay_clock_tick(&clock,1016,0)==1016);
 const uint32_t before_pause=clock.game_ms;
 assert(im2_gameplay_clock_tick(&clock,1032,1)==before_pause);
 assert(im2_gameplay_clock_tick(&clock,20000,1)==before_pause);
 now=im2_gameplay_clock_tick(&clock,20016,0);
 assert(now==before_pause);
 in.previous_flight_dir=B24G83_DIR_L;
 assert(b24_g83_timeline_tick(&timeline,NULL,now,&in,&selected));
 assert(!strcmp(selected.stem,"ironman_ironman_fly_ftol")&&timeline.completed_one_shots==0);
 now=im2_gameplay_clock_tick(&clock,20800,0);
 assert(b24_g83_timeline_tick(&timeline,NULL,now,&in,&selected));
 assert(!strcmp(selected.stem,"ironman_ironman_fly_l")&&timeline.completed_one_shots==1);
 /* G8 accepted shot must retain original age and presented pose over pause. */
 const char *idle="ironman_ironman_ground_idel",*shot="ironman_ironman_aim_ground_idle_att";
 clip(idle);clip(shot);float vertices[802*3]={0};B24G8LiveOriginalMotion a={0};
 clock=(Im2GameplayClock){0};now=im2_gameplay_clock_tick(&clock,1000,0);
 assert(b24_g8_motion_tick_g84(&a,".",vertices,12,802,0,B24M_IDLE,0,0,now,idle));
 b24_g8_motion_repulsor_trigger(&a,now);
 now=im2_gameplay_clock_tick(&clock,1016,0);
 assert(b24_g8_motion_tick_g84(&a,".",vertices,12,802,0,B24M_IDLE,0,0,now,idle));
 assert(a.whole_body_repulsor_active&&!strcmp(a.selected,shot));
 float previous[802*3];memcpy(previous,vertices,sizeof(previous));
 (void)im2_gameplay_clock_tick(&clock,1032,1);(void)im2_gameplay_clock_tick(&clock,20000,1);
 now=im2_gameplay_clock_tick(&clock,20016,0);
 assert(b24_g8_motion_tick_g84(&a,".",vertices,12,802,0,B24M_IDLE,0,0,now,idle));
 assert(a.whole_body_repulsor_active&&!strcmp(a.selected,shot)&&a.started_ms==1016);
 assert(!memcmp(previous,vertices,sizeof(previous)));
 now=im2_gameplay_clock_tick(&clock,20216,0);
 assert(b24_g8_motion_tick_g84(&a,".",vertices,12,802,0,B24M_IDLE,0,0,now,idle));
 assert(!a.whole_body_repulsor_active&&!strcmp(a.selected,idle));b24_g8_motion_release(&a);
 char path[256];snprintf(path,sizeof(path),"%s.im2v",idle);assert(!remove(path));
 snprintf(path,sizeof(path),"%s.im2v",shot);assert(!remove(path));
 /* Unsigned SDL tick wrap must still produce one real frame delta. */
 clock=(Im2GameplayClock){0};assert(im2_gameplay_clock_tick(&clock,UINT32_MAX-8,0)==UINT32_MAX-8);
 assert(im2_gameplay_clock_tick(&clock,7,0)==7);
 assert(im2_gameplay_clock_tick(&clock,23,1)==7);
 assert(im2_gameplay_clock_tick(&clock,39,0)==7);
 assert(im2_gameplay_clock_tick(&clock,55,0)==23);
 puts("PASS actual G83/G8 owners: source turn/shot age and pose freeze over user pause; SDL wrap preserved");
 return 0;
}
