#ifndef B24_MOCK_VITAGL_H
#define B24_MOCK_VITAGL_H
/* CI mock only: NEVER place this header on the VitaSDK include path.
   Verifies call contract, NOT real VitaGL ABI, shader, contexts or display. */
#include <stddef.h>
#define GL_DEPTH_TEST 0x0B71
#define GL_TEXTURE_2D 0x0DE1
#define GL_VERTEX_ARRAY 0x8074
#define GL_COLOR_ARRAY 0x8076
#define GL_FLOAT 0x1406
#define GL_UNSIGNED_BYTE 0x1401
#define GL_UNSIGNED_SHORT 0x1403
#define GL_TRIANGLES 0x0004
typedef int GLsizei;
typedef int GLenum;
extern unsigned b24_mock_draws,b24_mock_indices,b24_mock_vertex_calls,b24_mock_color_calls;
void glEnable(GLenum);
void glDisable(GLenum);
void glEnableClientState(GLenum);
void glDisableClientState(GLenum);
void glVertexPointer(int,GLenum,GLsizei,const void *);
void glColorPointer(int,GLenum,GLsizei,const void *);
void glDrawElements(GLenum,GLsizei,GLenum,const void *);
#define GL_FALSE 0
#define GL_TRUE 1
#define GL_COLOR_BUFFER_BIT 0x00004000
#define GL_DEPTH_BUFFER_BIT 0x00000100
#define GL_LESS 0x0201
#define GL_PROJECTION 0x1701
#define GL_MODELVIEW 0x1700
typedef unsigned char GLboolean;
typedef unsigned GLbitfield;
GLboolean vglInit(int);
void vglSwapBuffers(GLboolean);
void glViewport(int,int,GLsizei,GLsizei);
void glDepthFunc(GLenum);
void glClearColor(float,float,float,float);
void glClear(GLbitfield);
void glMatrixMode(GLenum);
void glLoadMatrixf(const float *);
#endif
