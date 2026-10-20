/* G298 HOST-ONLY tiny vitaGL FFP API shim. Never ship this to Vita. */
#ifndef G298_MOCK_VITAGL_H
#define G298_MOCK_VITAGL_H
#include <stddef.h>
#include <stdint.h>
typedef unsigned GLenum;
typedef unsigned GLuint;
typedef int GLint;
typedef int GLsizei;
typedef int GLboolean;
typedef unsigned char GLubyte;
typedef float GLfloat;
typedef ptrdiff_t GLsizeiptr;
#define GL_NO_ERROR 0u
#define GL_TEXTURE_2D 0x0DE1u
#define GL_RGBA 0x1908u
#define GL_UNSIGNED_BYTE 0x1401u
#define GL_FLOAT 0x1406u
#define GL_LINEAR 0x2601u
#define GL_REPEAT 0x2901u
#define GL_TEXTURE_MIN_FILTER 0x2801u
#define GL_TEXTURE_MAG_FILTER 0x2800u
#define GL_TEXTURE_WRAP_S 0x2802u
#define GL_TEXTURE_WRAP_T 0x2803u
#define GL_ARRAY_BUFFER 0x8892u
#define GL_STATIC_DRAW 0x88E4u
#define GL_DEPTH_TEST 0x0B71u
#define GL_LESS 0x0201u
#define GL_BLEND 0x0BE2u
#define GL_SRC_ALPHA 0x0302u
#define GL_ONE_MINUS_SRC_ALPHA 0x0303u
#define GL_VERTEX_ARRAY 0x8074u
#define GL_TEXTURE_COORD_ARRAY 0x8078u
#define GL_COLOR_ARRAY 0x8076u
#define GL_TRIANGLES 0x0004u
#define GL_TEXTURE_ENV 0x2300u
#define GL_TEXTURE_ENV_MODE 0x2200u
#define GL_REPLACE 0x1E01u
#define GL_MODULATE 0x2100u
void glGenTextures(GLsizei, GLuint *);
void glDeleteTextures(GLsizei,const GLuint *);
void glBindTexture(GLenum,GLuint);
void glTexParameteri(GLenum,GLenum,GLint);
void glTexImage2D(GLenum,GLint,GLint,GLsizei,GLsizei,GLint,GLenum,GLenum,const void *);
GLenum glGetError(void);
void glGenBuffers(GLsizei,GLuint *);
void glDeleteBuffers(GLsizei,const GLuint *);
void glBindBuffer(GLenum,GLuint);
void glBufferData(GLenum,GLsizeiptr,const void *,GLenum);
void glEnable(GLenum);
void glDisable(GLenum);
void glDepthFunc(GLenum);
void glDepthMask(GLboolean);
void glBlendFunc(GLenum,GLenum);
void glColor4f(GLfloat,GLfloat,GLfloat,GLfloat);
void glEnableClientState(GLenum);
void glDisableClientState(GLenum);
void glVertexPointer(GLint,GLenum,GLsizei,const void *);
void glTexCoordPointer(GLint,GLenum,GLsizei,const void *);
void glColorPointer(GLint,GLenum,GLsizei,const void *);
void glGetTexEnviv(GLenum,GLenum,GLint *);
void glTexEnvi(GLenum,GLenum,GLint);
void glDrawArrays(GLenum,GLint,GLsizei);
#endif
