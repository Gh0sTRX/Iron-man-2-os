/* G299 HOST-only VitaGL FFP symbols; never copy this mock into VitaSDK. */
#ifndef G299_HOST_FAKE_VITAGL_H
#define G299_HOST_FAKE_VITAGL_H
#include <stddef.h>
#include <stdint.h>
typedef unsigned GLenum;
typedef unsigned GLuint;
typedef int GLint;
typedef int GLsizei;
typedef float GLfloat;
typedef unsigned char GLboolean;
#define GL_TEXTURE_2D 0x0DE1u
#define GL_UNSIGNED_BYTE 0x1401u
#define GL_UNSIGNED_SHORT 0x1403u
#define GL_FLOAT 0x1406u
#define GL_RGBA 0x1908u
#define GL_LINEAR 0x2601u
#define GL_CLAMP_TO_EDGE 0x812Fu
#define GL_TEXTURE_MIN_FILTER 0x2801u
#define GL_TEXTURE_MAG_FILTER 0x2800u
#define GL_TEXTURE_WRAP_S 0x2802u
#define GL_TEXTURE_WRAP_T 0x2803u
#define GL_MODELVIEW 0x1700u
#define GL_DEPTH_TEST 0x0B71u
#define GL_VERTEX_ARRAY 0x8074u
#define GL_TEXTURE_COORD_ARRAY 0x8078u
#define GL_TRIANGLES 0x0004u
#define GL_TEXTURE_ENV 0x2300u
#define GL_TEXTURE_ENV_MODE 0x2200u
#define GL_MODULATE 0x2100u
#define GL_REPLACE 0x1E01u
void glGenTextures(GLsizei,GLuint *);
void glDeleteTextures(GLsizei,const GLuint *);
void glBindTexture(GLenum,GLuint);
void glTexParameteri(GLenum,GLenum,GLint);
void glTexImage2D(GLenum,GLint,GLint,GLsizei,GLsizei,GLint,GLenum,GLenum,const void *);
void glMatrixMode(GLenum);
void glPushMatrix(void);
void glPopMatrix(void);
void glMultMatrixf(const GLfloat *);
void glEnable(GLenum);
void glDisable(GLenum);
void glColor4f(GLfloat,GLfloat,GLfloat,GLfloat);
void glEnableClientState(GLenum);
void glDisableClientState(GLenum);
void glVertexPointer(GLint,GLenum,GLsizei,const void *);
void glTexCoordPointer(GLint,GLenum,GLsizei,const void *);
void glDrawElements(GLenum,GLsizei,GLenum,const void *);
void glGetTexEnviv(GLenum,GLenum,GLint *);
void glTexEnvi(GLenum,GLenum,GLint);
#endif
