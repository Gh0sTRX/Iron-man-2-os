#ifndef IM2_SUIT_PROFILE_H
#define IM2_SUIT_PROFILE_H
/* The current owner-derived Mark VI/IV/Stealth IM2T files have identical
 * position/UV/index bytes (not merely equal vertex counts). B9 already uses
 * this shared bank. Geometry+UV+triangle SHA256:
 * a8b1bccd72c494797ae5470d6d1bb0a7537c67078cb1f15b75d0bad212071f90.
 * This proves pose-layout compatibility, not original weapon/input semantics.
 * Keep actual suit IDs as event owners even when the pose bank is shared. */
static inline int im2_suit_uses_802_bank(int suit){
 return suit==0||suit==1||suit==3;
}
static inline unsigned im2_suit_source_vertices(int suit){
 return im2_suit_uses_802_bank(suit)?802u:suit==2?1292u:suit==4?629u:0u;
}
#endif
