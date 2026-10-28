#ifndef IM2_TEST_OPPONENT_VITAGL_H
#define IM2_TEST_OPPONENT_VITAGL_H
#include "im2_test_opponent.h"
#include "b24_gpu_suit_im2_adapter.h"
#include "b24_original_im2v_stream.h"
typedef struct {
 Im2TestOpponent state;IM2Model model;B24GpuSuit gpu;B24GpuIM2Stream mesh;
 B24OriginalIM2VStream animation;float *xyz;char selected[128];
 float shot_line[6],projectile[3];uint32_t shot_since,now;int shot_visible,projectile_visible,loaded;
} Im2TestOpponentDraw;
int im2_test_opponent_open(Im2TestOpponentDraw *s);
void im2_test_opponent_close(Im2TestOpponentDraw *s);
int im2_test_opponent_pose(Im2TestOpponentDraw *s,uint32_t now);
int im2_test_opponent_draw(const Im2TestOpponentDraw *s);
#endif
