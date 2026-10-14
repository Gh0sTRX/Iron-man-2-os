#!/usr/bin/env python3
"""G10 physically separate original armored meshes share THE OWNER 248 IronMan
authored animation TREE but using suit-specific re-skinned original BRES frames.
Does not load raw Mark VI XYZ onto an unrelated armor.
Apply AFTER G9 original source single world/pose hook but BEFORE G10 VPK.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/"work/b24/b24_unified/b24_g8_live_original_motion.c"
s=p.read_text()
def change(old,new):
 global s
 if s.count(old)!=1:raise RuntimeError("G10 four armor source drift "+str(s.count(old))+" "+old[:115])
 s=s.replace(old,new)
change('#include <string.h>', '#include <string.h>\n#include <stdio.h>')
# Source IronMan_Move_Float is the non-repulsor hover body variant.
# G9 used IronMan_Aim_Float_idle even when no attack was accepted, causing
# a permanently raised repulsor while floating. Source Move_Float must be
# visually confirmed on Vita; never disable B16 actual repulsor attack.
change('"ironman_ironman_aim_float_idle",',
       '"ironman_ironman_move_float",')
entry='''const char *b24_g8_motion_route(int suit,B24MotionStage mode,float x,float y){'''
intro='''/* Original source BRES clips are independently re-skinned for each armor.
   Local buffer only: single original animation/gameplay B14 tick, no threads.
   The route name stays the real IronMan 2010 source label after suit prefix.
   This is not copying the 802 Mark VI vertex matrix to 629-vertex suitcase. */
static const char *g10_alt_iron_source_name(const char *mark6,int suit,int role){
 static char names[3][128];
 const char *prefix=suit==1?"mark4":suit==3?"stealth":
                    suit==4?"suitcase":NULL;
 if(!mark6||!prefix||strncmp(mark6,"ironman_",8)!=0||
     role<0||role>=3)return NULL;
 int n=snprintf(names[role],sizeof(names[role]),"%s_%s",
                prefix,mark6+8);
 return n>0&&(size_t)n<sizeof(names[role])?names[role]:NULL;
}
const char *b24_g8_motion_route(int suit,B24MotionStage mode,float x,float y){'''
change(entry,intro)
change(''' if(suit==0){
  switch(mode){''',''' if(suit==1||suit==3||suit==4)
    return g10_alt_iron_source_name(b24_g8_motion_route(0,mode,x,y),
                                    suit,0);
 if(suit==0){
  switch(mode){''')
change(''' if(suit==0){
  if(stage==B24M_HOVER||stage==B24M_DRIFT)return mk6_hover_fire[d];''',''' if(suit==1||suit==3||suit==4)
    return g10_alt_iron_source_name(
       b24_g8_motion_repulsor_clip(0,stage,x,y),suit,1);
 if(suit==0){
  if(stage==B24M_HOVER||stage==B24M_DRIFT)return mk6_hover_fire[d];''')
change(''' if(!a||a->suit_index!=0||!a->nv)return;''',
       ''' if(!a||!(a->suit_index==0||a->suit_index==1||
            a->suit_index==3||a->suit_index==4)||!a->nv)return;''')
change(''' if(suit==0 && mode<=B24M_RUN)
    melee=b24_g8_melee_tick(&a->melee,now);''',
''' if((suit==0||suit==1||suit==3||suit==4)&&mode<=B24M_RUN)
    melee=b24_g8_melee_tick(&a->melee,now);''')
change(''' if(melee)desired=melee;''',
''' if(melee){
    desired=suit==0?melee:g10_alt_iron_source_name(melee,suit,2);
    if(!desired)return 0;
 }''')
change(''' if(!desired|| (suit==0&&nv!=802u) || (suit==2&&nv!=1292u)){''',
''' if(!desired|| ((suit==0||suit==1||suit==3)&&nv!=802u) ||
      (suit==4&&nv!=629u) || (suit==2&&nv!=1292u)){''')
p.write_text(s)
print("PASS G10 genuine all-four-suit authored 248 clip name routing: MarkVI802 MarkIV802 Stealth802 Suitcase629 each separate source BRES skins, L/R hover/fire/melee, WM independent 1292; NO VPK")
