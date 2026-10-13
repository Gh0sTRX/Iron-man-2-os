/* HOST TEST STUB ONLY, NOT a vitaGL replacement. Real VitaSDK header takes precedence in actual build. */
#ifndef VITA_GL_STUB_H
#define VITA_GL_STUB_H
#include <stddef.h>
typedef int GLsizei;typedef unsigned GLen;
#define GL_DEPTH_TEST 0x0B71u
#define GL_TEXTURE_2D 0x0DE1u
#define GL_VERTEX_ARRAY 0x8074u
#define GL_COLOR_ARRAY 0x8076u
#define GL_FLOAT 0x1406u
#define GL_TRIANGLES 0x0004u
#define GL_UNSIGNED_SHORT 0x1403u
void glEnable(unsigned);void glDisable(unsigned);void glEnableClientState(unsigned);void glDisableClientState(unsigned);
void glVertexPointer(int,unsigned,int,const void*);void glColorPointer(int,unsigned,int,const void*);
void glDrawElements(unsigned,int,unsigned,const void*);
#endif
