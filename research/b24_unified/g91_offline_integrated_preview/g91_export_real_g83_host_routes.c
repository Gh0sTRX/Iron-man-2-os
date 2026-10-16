/* G91 source-led: invoke existing actual 2010 clip selector C, NOT a
 * hand-authored JS moveset. Export selected G83 clip names for a browser
 * host diagnostic; 2010 input mapping and hitframes remain unproven.
 * Compile/link against ORIGINAL G83/G82/G8 implementation, NO VPK.
 */
#include "../g83_full_motion_aim/b24_g83_unified_movement_aim.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void){
 puts("{\"G83_selector_called_from_original_C\":true,"
  "\"browser_keyboard_binding_is_DIAGNOSTIC_not_original_iOS\":true,"
  "\"source_routes\":[");
 for(int mode=0;mode<4;mode++)
  for(int aim=0;aim<=1;aim++)
   for(int dir=0;dir<5;dir++){
    if(mode||aim||dir)printf(",");
    B24G83Input in={0};B24G83Selection out={0};
    const float ax[]={0.f,0.f,0.f,-1.f,1.f};
    const float ay[]={0.f,1.f,-1.f,0.f,0.f};
    in.suit_index=B24G83_MARKVI;in.motion=(B24G83Mode)mode;
    in.aim=(B24G83Aim)aim;in.axis_x=ax[dir];in.axis_y=ay[dir];
    if(!b24_g83_select_original_motion(&in,&out)||!out.stem)exit(6);
    if(strncmp(out.stem,"ironman_ironman_",16)!=0)exit(7);
    printf("{\"mode\":%d,\"aim\":%d,\"direction\":%d,"
       "\"source_name\":\"%s\",\"markv\":\"suitcase_%s\"}",
       mode,aim,dir,out.stem,out.stem+8);
   }
 puts("],\"original_markv_author_combat_sequences\":["
      "\"suitcase_ironman_ground_combo_1\","
      "\"suitcase_ironman_ground_combo_2\","
      "\"suitcase_ironman_ground_combo_3\"],"
      "\"original_hit_time_source_recovered\":false,"
      "\"original_attack_damage_source_recovered\":false,"
      "\"NO_VPK\":true}");
 return 0;
}
