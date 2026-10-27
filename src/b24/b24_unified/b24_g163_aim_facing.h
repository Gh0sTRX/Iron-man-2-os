#ifndef B24_G163_AIM_FACING_H
#define B24_G163_AIM_FACING_H
/* G163: Only ORIENTATION adjustment, not any movement/camera/weapon owner.
 * B14 still moves player with camera-relative stick axes; G83/G8 still
 * selects 2010 directional strafe animation. Heading adopts camera aim
 * only while L+repulsor aim on ground or upright hover; no flight changes.
 * Source iOS aim input mapping not natively proven; port QA policy.
 */
float b24_g163_aim_heading(float heading,float orbit,float dt,
                          int aim_pressed,int ground_or_hover);
#endif
