#include "b24_g146_true_2010_QTE_actor.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static int real_renderer_mock(void *ctx,const B24G146QTE *q){
 int *hits=(int*)ctx;(*hits)++;
 return q->source_scene_actor_ID==1456&&
   q->source_native_class==94&&
   q->source_transform_child_ID==1458;
}
int main(void){
 B24G146QTE q={0};
 assert(b24_g146_qte_source_init(&q));
 assert(q.source_scene_actor_ID==1456&&q.source_native_class==94);
 assert(q.source_transform_child_ID==1458);
 assert(fabsf(q.original_local_xyz[0]-172.114f)<.001f);
 assert(fabsf(q.original_local_xyz[1]+95.298f)<.001f);
 assert(fabsf(q.original_local_xyz[2]+.118f)<.001f);
 assert(fabsf(q.original_local_quat_xyzw[2]-.848043f)<.00001f);
 B24G137Event event={0};
 event.opcode=B24_G137_CALL_SHOW;
 event.original_lua_pc=6;
 event.source_arg0=1456;
 assert(!b24_g146_qte_show_source_Lua_PC6(&q,&event,NULL,NULL));
 assert(q.original_show_requested&&!q.original_show_actually_rendered);
 int calls=0;
 assert(b24_g146_qte_show_source_Lua_PC6(&q,&event,real_renderer_mock,&calls));
 assert(q.original_show_actually_rendered&&calls==1);
 event.source_arg0=1457;
 assert(!b24_g146_qte_show_source_Lua_PC6(&q,&event,real_renderer_mock,&calls));
 assert(calls==1);
 puts("G146 PASS original 2010 Level1 InteractiveObj_QTE ID1456 class94 native child1458 actual local source xyz/q, PC6 Show ID sourced; no fake QTE render without actual bound callback. NO VPK.");
 return 0;
}
