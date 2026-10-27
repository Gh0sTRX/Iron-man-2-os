#ifndef B24_G173_AUTHORED_BEAM_PRIORITY_H
#define B24_G173_AUTHORED_BEAM_PRIORITY_H
#include <string.h>
/* Names below are EXACT authored iOS 2010 G169 original IM2V names.
 * We only correct a Vita source animation-selection conflict; these
 * identifiers DO NOT recover Gameloft's input/weapon/damage event mapping.
 * Verified G169 actor phase has already been gated by the accepted
 * existing B16 Unibeam event. The G8 owner must not create another event. */
static inline int b24_g173_is_authored_beam(int suit,const char *name){
 const char *prefix=suit==0?"ironman_ironman_aim_":
                    suit==4?"suitcase_ironman_aim_":0;
 if(!prefix||!name)return 0;
 const size_t length=strlen(prefix);
 if(strncmp(name,prefix,length))return 0;
 const char *suffix=name+length;
 return !strcmp(suffix,"ground_beam1")||
        !strcmp(suffix,"ground_beam2")||
        !strcmp(suffix,"ground_beam3")||
        !strcmp(suffix,"float_beam1")||
        !strcmp(suffix,"float_beam2")||
        !strcmp(suffix,"float_beam3");
}
/* Melee retains existing ownership even during the port's UniBeam.
 * No hit event or damage is implied by the return value. */
static inline int b24_g173_authored_beam_pose_priority(int suit,
                                                        const char *name,
                                                        int melee_active){
 return !melee_active&&b24_g173_is_authored_beam(suit,name);
}
#endif
