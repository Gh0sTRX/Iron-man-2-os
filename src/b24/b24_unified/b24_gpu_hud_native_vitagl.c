#include "b24_gpu_hud_native.h"
#include <vitaGL.h>
#include <stddef.h>
_Static_assert(sizeof(B24NativeHudVertex)==12,"HUD GPU vertex ABI must remain 12 bytes");
/* The HUD becomes ONE GPU indexed-free triangle batch, no CPU pixel buffer,
   no glTexSubImage2D and no 480x272 SDL_UpdateTexture. */
int b24_native_hud_draw(const B24NativeHudGeometry *g){
 if(!g||g->overflow||g->count==0||g->count>B24_NATIVE_HUD_VERTICES||
    g->count%3u)return 0;
 glMatrixMode(GL_PROJECTION);
 glPushMatrix();glLoadIdentity();
 glOrthof(0.f,480.f,272.f,0.f,-1.f,1.f);
 glMatrixMode(GL_MODELVIEW);
 glPushMatrix();glLoadIdentity();
 glDisable(GL_DEPTH_TEST);
 glDepthMask(GL_FALSE);
 glDisable(GL_TEXTURE_2D);
 glEnable(GL_BLEND);
 glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
 glEnableClientState(GL_VERTEX_ARRAY);
 glEnableClientState(GL_COLOR_ARRAY);
 glVertexPointer(2,GL_FLOAT,sizeof(B24NativeHudVertex),&g->vertices[0].x);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(B24NativeHudVertex),&g->vertices[0].rgba);
 glDrawArrays(GL_TRIANGLES,0,(GLsizei)g->count);
 glDisableClientState(GL_COLOR_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);
 glDisable(GL_BLEND);
 glDepthMask(GL_TRUE);
 glEnable(GL_DEPTH_TEST);
 glPopMatrix();
 glMatrixMode(GL_PROJECTION);glPopMatrix();
 glMatrixMode(GL_MODELVIEW);
 return 1;
}
