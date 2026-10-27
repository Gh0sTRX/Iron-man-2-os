#include "b24_g146_true_2010_QTE_actor.h"
#include <string.h>
int b24_g146_qte_source_init(B24G146QTE *q){
 if(!q)return 0;
 memset(q,0,sizeof(*q));
 q->source_scene_actor_ID=1456;
 q->source_native_class=94; /* original 2010 InteractiveObj */
 q->source_transform_child_ID=1458;
 q->original_local_xyz[0]=172.11399841308594f;
 q->original_local_xyz[1]=-95.2979965209961f;
 q->original_local_xyz[2]=-0.11800000071525574f;
 q->original_local_quat_xyzw[0]=0.f;
 q->original_local_quat_xyzw[1]=0.f;
 q->original_local_quat_xyzw[2]=0.8480432629585266f;
 q->original_local_quat_xyzw[3]=0.5299270749092102f;
 return 1;
}
int b24_g146_qte_show_source_Lua_PC6(
 B24G146QTE *q,const B24G137Event *event,
 B24G146RendererShow render_cb,void *ctx){
 if(!q||!event||
    event->opcode!=B24_G137_CALL_SHOW||
    event->original_lua_pc!=6||
    event->source_arg0!=1456||
    q->source_scene_actor_ID!=1456||
    q->source_native_class!=94||
    q->source_transform_child_ID!=1458)return 0;
 q->original_show_requested=1;
 /* G146 DOES NOT INVENT a QTE overlay/input gesture. The original
  * InteractiveObj_QTE model/HUD/action button must really exist
  * in the source VitaGL/2010 QTE renderer before ACKing PC6. */
 if(!render_cb||!render_cb(ctx,q))return 0;
 q->original_show_actually_rendered=1;
 return 1;
}
