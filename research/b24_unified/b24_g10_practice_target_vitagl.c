#include "b24_g10_practice_target.h"
#include <vitaGL.h>
#include <math.h>
#include <stddef.h>
/* Only a visible geometry marker, NOT original enemy model.
   Use one existing GXM draw context and no additional present/swap. */
int b24_g10_practice_target_draw(const B24G10PracticeTarget *t){
 if(!b24_g10_practice_target_valid(t))return 0;
 const float x=t->x,y=t->y,z=t->z,r=t->radius;
 const float lines[][3]={
    {x-r,y-r,z-r},{x+r,y-r,z-r},
    {x+r,y-r,z-r},{x+r,y+r,z-r},
    {x+r,y+r,z-r},{x-r,y+r,z-r},
    {x-r,y+r,z-r},{x-r,y-r,z-r},
    {x-r,y-r,z+r},{x+r,y-r,z+r},
    {x+r,y-r,z+r},{x+r,y+r,z+r},
    {x+r,y+r,z+r},{x-r,y+r,z+r},
    {x-r,y+r,z+r},{x-r,y-r,z+r},
    {x-r,y-r,z-r},{x-r,y-r,z+r},
    {x+r,y-r,z-r},{x+r,y-r,z+r},
    {x+r,y+r,z-r},{x+r,y+r,z+r},
    {x-r,y+r,z-r},{x-r,y+r,z+r},
    {x-r,y,z},{x+r,y,z},
    {x,y-r,z},{x,y+r,z},
    {x,y,z-r},{x,y,z+r}
 };
 glDisable(GL_TEXTURE_2D);
 glEnable(GL_DEPTH_TEST);
 glColor4f(.2f,1.f,.9f,1.f);
 glEnableClientState(GL_VERTEX_ARRAY);
 glVertexPointer(3,GL_FLOAT,0,lines);
 glDrawArrays(GL_LINES,0,(GLsizei)(sizeof(lines)/sizeof(lines[0])));
 glDisableClientState(GL_VERTEX_ARRAY);
 glColor4f(1.f,1.f,1.f,1.f);
 return 1;
}
