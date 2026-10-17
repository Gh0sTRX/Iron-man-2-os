#include "b24_g152_source_tutorial_loop.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    unsigned waits,voice_stops,show340, allow;
    float last_wait;
    int text_id,native_id,mode,third;
} Mock;
static int native_wait(void *p,float arg) {
    Mock *m=(Mock*)p;m->waits++;m->last_wait=arg;return m->allow;
}
static int native_stop(void *p) {
    Mock *m=(Mock*)p;m->voice_stops++;return m->allow;
}
static int native_show(void *p,int id,int packed,int mode,int third) {
    Mock *m=(Mock*)p;m->show340++;
    m->text_id=id;m->native_id=packed;m->mode=mode;m->third=third;
    return m->allow;
}
int main(void) {
    B24G152TutorialLoop q={0};b24_g152_tutorial_loop_init(&q);
    B24G147Tutorial t={0};b24_g147_tutorial_init(&t);
    Mock m={0};
    assert(b24_g152_tutorial_loop_step(0,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_BLOCKED_NATIVE_BINDING);
    /* Original scene renderer absent -> no fake Wait/success. */
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_BLOCKED_NATIVE_BINDING);
    assert(!m.waits&&!q.source_wait_request_count);
    /* Mock renderer acknowledgement TEST ONLY, not a live Vita QTE. */
    t.tutorial_was_requested=1;
    t.original_renderer_ack=1;
    t.native_translator_verified=1;
    t.source_clara_text_id=339;
    t.current_original_game_ui_text_id=0x1053;
    t.current_original_game_ui_mode=12;
    assert(b24_g152_tutorial_loop_step(&q,&t,0,0,native_stop,
        native_show,&m)==B24_G152_BLOCKED_NATIVE_BINDING);
    assert(!q.source_wait_request_count);
    m.allow=1;
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION);
    assert(q.stage==B24_G152_WAIT_NATIVE_10);
    assert(q.source_wait_request_count==1 && m.waits==1);
    assert(m.last_wait==10.0f && !q.original_pc72_result.lua_boolean);
    for (int i=0;i<20;i++)
        assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
            native_stop,native_show,&m)==B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION);
    assert(m.waits==1); /* no guessed time unit or accidental busy loop */
    assert(b24_g152_tutorial_loop_step(&q,&t,1,native_wait,
        native_stop,native_show,&m)==B24_G152_PC71_REQUERY_READY);
    assert(q.stage==B24_G152_NEED_REAL_PC72);
    /* Still FALSE -> source repeats exactly one new Wait(10). */
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION);
    assert(m.waits==2&&q.source_wait_request_count==2);
    /* A signal must end the outstanding source wait first. */
    t.global_ui_override=1;
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_WAITING_ORIGINAL_WAIT_COMPLETION);
    assert(b24_g152_tutorial_loop_step(&q,&t,1,native_wait,
        native_stop,native_show,&m)==B24_G152_PC71_REQUERY_READY);
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_PC79_ACTION_READY);
    assert(q.original_pc72_result.lua_boolean);
    assert(q.stage==B24_G152_NEED_PC79_STOPVOICE);
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        0,native_show,&m)==B24_G152_BLOCKED_NATIVE_BINDING);
    assert(!m.voice_stops);
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_PC81_ACTION_READY);
    assert(q.source_stop_voice_ack_count==1&&m.voice_stops==1);
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,0,&m)==B24_G152_BLOCKED_NATIVE_BINDING);
    assert(!m.show340);
    assert(b24_g152_tutorial_loop_step(&q,&t,0,native_wait,
        native_stop,native_show,&m)==B24_G152_STOPPED_AT_PC86);
    assert(m.show340==1&&m.text_id==340&&m.native_id==0x1054);
    assert(m.mode==0&&m.third==1);
    assert(q.source_show_tut340_ack_count==1);
    assert(b24_g152_tutorial_loop_step(&q,&t,1,native_wait,
        native_stop,native_show,&m)==B24_G152_STOPPED_AT_PC86);
    assert(m.show340==1&&m.voice_stops==1);
    /* Do not infer PC86+ MissionResume, UI 2/6 or suit flight rights. */
    puts("G152 PASS original Lua PC73 FALSE Wait(10) repeat / TRUE StopVoice ShowTut(340,1,1), exact typed gating, no time guess, no fake Vita renderer, NO VPK");
    return 0;
}
