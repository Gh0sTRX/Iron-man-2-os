#include "im2_test_opponent_vitagl.h"
#include <vitaGL.h>
#include <stdlib.h>
#include <string.h>
static const char *const clips[]={"ironman_ironman_ground_idel","ironman_ironman_ground_hurt1",
 "ironman_ironman_ground_combo_1","ironman_ironman_ground_death"};
void im2_test_opponent_close(Im2TestOpponentDraw *s){
 if(!s)return;
 b24_gpu_suit_release(&s->gpu);b24_gpu_im2_stream_free(&s->mesh);b24_original_im2v_close(&s->animation);
 im2_free(&s->model);free(s->xyz);memset(s,0,sizeof(*s));
}
int im2_test_opponent_open(Im2TestOpponentDraw *s){
 if(!s||s->loaded)return 0;
 im2_test_opponent_reset(&s->state);
 if(!im2_load(&s->model,"app0:models/mark4.im2t")||s->model.nv!=802)goto fail;
 for(unsigned i=0;i<4;i++){
  B24OriginalIM2VStream probe={0};
  if(!b24_original_im2v_open(&probe,"app0:animations",clips[i],802))goto fail;
  b24_original_im2v_close(&probe);
 }
 s->xyz=malloc(802*3*sizeof(float));if(!s->xyz)goto fail;
 if(!b24_gpu_im2_stream_init(&s->mesh,&s->model)||!b24_gpu_im2_stream_update(&s->mesh,&s->model)||
    !b24_gpu_suit_prepare(&s->gpu,&s->mesh.source))goto fail;
 s->loaded=1;return 1;
 fail:im2_test_opponent_close(s);return 0;
}
int im2_test_opponent_pose(Im2TestOpponentDraw *s,uint32_t now){
 if(!s||!s->loaded)return 0;
 s->now=now;
 if(!s->state.spawned)return 1;
 if((unsigned)s->state.phase>3)return 0;
 const char *clip=clips[s->state.phase];
 if(strcmp(s->selected,clip)){
  if(!b24_original_im2v_open(&s->animation,"app0:animations",clip,802))return 0;
  strcpy(s->selected,clip);
 }
 const uint32_t age=now-s->state.phase_since;
 if(!b24_original_im2v_sample(&s->animation,age,s->state.phase==IM2_TEST_IDLE,s->xyz))return 0;
 for(unsigned i=0;i<802;i++){
  s->model.vertices[i].x=s->xyz[i*3];s->model.vertices[i].y=s->xyz[i*3+1];s->model.vertices[i].z=s->xyz[i*3+2];
 }
 if(s->state.phase!=IM2_TEST_IDLE&&s->state.phase!=IM2_TEST_DOWN&&age>=s->animation.duration_ms)
  im2_test_opponent_animation_done(&s->state,now);
 return b24_gpu_im2_stream_update(&s->mesh,&s->model);
}
int im2_test_opponent_draw(const Im2TestOpponentDraw *s){
 if(!s||!s->loaded||!s->state.spawned)return 1;
 const B24GpuSuitPose pose={s->state.x,s->state.y,s->state.z,s->state.heading,0,0};
 if(!b24_gpu_suit_draw(&s->gpu,&s->mesh.source,&pose))return 0;
 if(s->shot_visible&&(uint32_t)(s->now-s->shot_since)<150u){
  glDisable(GL_TEXTURE_2D);glEnable(GL_DEPTH_TEST);glColor4f(1.f,.84f,.12f,1.f);
  glEnableClientState(GL_VERTEX_ARRAY);glVertexPointer(3,GL_FLOAT,0,s->shot_line);
  glDrawArrays(GL_LINES,0,2);glDisableClientState(GL_VERTEX_ARRAY);glColor4f(1,1,1,1);
 }
 if(s->projectile_visible){
  const float x=s->projectile[0],y=s->projectile[1],z=s->projectile[2];
  const float marker[]={x-.08f,y,z,x+.08f,y,z,x,y-.08f,z,x,y+.08f,z,x,y,z-.08f,x,y,z+.08f};
  glDisable(GL_TEXTURE_2D);glEnable(GL_DEPTH_TEST);glColor4f(1,.84f,.12f,1);
  glEnableClientState(GL_VERTEX_ARRAY);glVertexPointer(3,GL_FLOAT,0,marker);
  glDrawArrays(GL_LINES,0,6);glDisableClientState(GL_VERTEX_ARRAY);glColor4f(1,1,1,1);
 }
 return 1;
}
