#include "im2_original_tables.h"
#include "b24_g137_source_mission000_intro.h"
#include <assert.h>
#include <stdio.h>
int main(int argc,char **argv){
 assert(argc==2&&im2_original_tables_load(argv[1]));
 for(unsigned i=0;i<4;i++)printf("N\t%s\n",b24g217_original_suit_source_names[i]);
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<194;j++){
  const B24G217_SourceState *s=&b24g217_true_2010_owner_states[i][j];
  printf("S\t%s\t%u\t%u\t%u\t%u\t%u\t%u\n",s->original_source_state_name,
   s->original_AttackType_or_UNKNOWN,s->original_next_state_or_UNKNOWN,s->original_state_type_or_UNKNOWN,
   s->original_loop_or_UNKNOWN,s->native_source_state_index,s->original_state_track_count);
 }
 for(unsigned i=0;i<224;i++){
  const B24G217_SourceEvent *e=&b24g217_source_attack_trail_events[i];
  printf("E\t%s\t%u\t%u\t%u\t%u\t%u\n",e->native_original_track_name,
   e->raw_original_2010_start,e->raw_original_2010_duration,e->raw_original_2010_third_field_UNCLASSIFIED,
   e->native_suit_group_index,e->native_original_state_index);
 }
 for(unsigned i=0;i<b24_g137_source_lua_event_count;i++){
  const B24G137Event *e=&b24_g137_source_lua_events[i];
  printf("L\t%u\t%u\t%d\t%d\t%d\t%s\t%u\t%u\n",e->original_lua_pc,e->opcode,
   e->source_arg0,e->source_arg1,e->source_arg2,e->source_arg1_string?e->source_arg1_string:"<NULL>",
   e->original_arg1_boolean,e->original_args_reliable);
 }
 B24G137Mission000 m={0};assert(b24_g137_mission000_init(&m));
 im2_original_tables_close();return 0;
}
