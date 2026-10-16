/* Iron Man 2 (2010) -> PS Vita B24 G65 SOURCE PLAYABLE BETA.
 * Standalone hardware validation to avoid altering prior known-good G10.
 * G65: real owner-authored BRES/PVR/UV world from scene GLB, G59 native
 * source wall/floor collisions, owner Mark VI armored player mesh.
 * Native source animations/mission scripting are NOT yet integrated.
 * Collision is CPU, visual is VitaGL; no fabricated collision walls.
 */
#include <vitaGL.h>
#include "g67_collision.h"
#include <psp2/ctrl.h>
#include <psp2/kernel/threadmgr.h>
#include <psp2/kernel/processmgr.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W 960
#define H 544
#define VERT_STRIDE 24
#define MAX_BATCH 80
#define MAX_TEXTURES 48
#define MAX_COLLISION 4096
#define PI 3.14159265358979f
#define RAD 0.39f
#define PLAYER_HEIGHT 2.15f

typedef G67Vec Vec;
typedef struct {float p[3], uv[2];unsigned char rgba[4];} Vertex;
typedef struct {uint32_t first,count,tex,flags;} Batch;
typedef struct {
 Vertex *v;
 uint32_t nv,nb,nt;
 Batch groups[MAX_BATCH];
 GLuint tex[MAX_TEXTURES];
 GLuint vertex_buffer;
} SourceMesh;
typedef G67Tri Tri;
typedef struct {
 Vec pos; float heading,camera_heading,camera_pitch,velocity_z;
 int flying,paused,show_help,cruise;
 float health,flight_time;
} Player;
static SourceMesh city,armor;
static Tri walls[MAX_COLLISION];
static uint32_t nwalls=0;
static Player player;
static int load_ok=0,wall_ok=0;
static int draw_calls=0;
static int lastfps=0;

static Vec sub(Vec a,Vec b){return (Vec){a.x-b.x,a.y-b.y,a.z-b.z};}
static Vec plus(Vec a,Vec b){return (Vec){a.x+b.x,a.y+b.y,a.z+b.z};}
static Vec mul(Vec a,float k){return (Vec){a.x*k,a.y*k,a.z*k};}
static float dot(Vec a,Vec b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static Vec cross(Vec a,Vec b){return (Vec){a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
static Vec norm(Vec a){float l=sqrtf(dot(a,a));return l>1e-9f?mul(a,1.f/l):(Vec){0,0,1};}
static float clampf(float x,float lo,float hi){return x<lo?lo:x>hi?hi:x;}

static int read_exact(FILE *f,void *dst,size_t bytes){return f&&fread(dst,1,bytes,f)==bytes;}
static int load_texture(GLuint *out,const char *path){
 FILE *f=fopen(path,"rb");if(!f)return 0;
 char magic[4];uint32_t meta[3];
 if(!read_exact(f,magic,4)||memcmp(magic,"G66T",4)||!read_exact(f,meta,12)||meta[0]!=1||
    meta[1]<8||meta[1]>1024||meta[2]<8||meta[2]>1024){fclose(f);return 0;}
 size_t length=(size_t)meta[1]*meta[2]*4;
 unsigned char *pixels=(unsigned char *)malloc(length);
 if(!pixels||!read_exact(f,pixels,length)||fgetc(f)!=EOF){free(pixels);fclose(f);return 0;}
 fclose(f);
 glGenTextures(1,out);if(!*out){free(pixels);return 0;}
 glBindTexture(GL_TEXTURE_2D,*out);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT);
 glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT);
 glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,(GLsizei)meta[1],(GLsizei)meta[2],0,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
 free(pixels);
 return glGetError()==GL_NO_ERROR;
}
static int load_mesh(SourceMesh *m,const char *file,const char *prefix){
 FILE *f=fopen(file,"rb");if(!f)return 0;
 char magic[4];uint32_t header[4];
 if(!read_exact(f,magic,4)||memcmp(magic,"G66M",4)||!read_exact(f,header,sizeof(header))||
     header[0]!=1||header[1]<3||header[1]>250000||header[2]>MAX_BATCH||header[3]>MAX_TEXTURES){fclose(f);return 0;}
 m->nv=header[1];m->nb=header[2];m->nt=header[3];
 if(!read_exact(f,m->groups,sizeof(Batch)*m->nb)){fclose(f);return 0;}
 m->v=(Vertex *)malloc((size_t)m->nv*sizeof(Vertex));
 if(!m->v||sizeof(Vertex)!=VERT_STRIDE||!read_exact(f,m->v,(size_t)m->nv*sizeof(Vertex))||fgetc(f)!=EOF){fclose(f);return 0;}
 fclose(f);
 for(uint32_t i=0;i<m->nb;i++){
  const Batch *g=&m->groups[i];
  if(g->first>m->nv||g->count>m->nv-g->first||g->count%3||
     (g->tex!=UINT32_MAX&&g->tex>=m->nt))return 0;
 }
 for(uint32_t i=0;i<m->nt;i++){
  char path[160];snprintf(path,sizeof(path),"app0:assets/%s_tex_%02u.g66t",prefix,i);
  if(!load_texture(&m->tex[i],path))return 0;
 }
 glGenBuffers(1,&m->vertex_buffer);
 if(!m->vertex_buffer)return 0;
 glBindBuffer(GL_ARRAY_BUFFER,m->vertex_buffer);
 glBufferData(GL_ARRAY_BUFFER,(GLsizeiptr)(m->nv*sizeof(Vertex)),m->v,GL_STATIC_DRAW);
 glBindBuffer(GL_ARRAY_BUFFER,0);
 free(m->v);m->v=NULL;
 return glGetError()==GL_NO_ERROR;
}
static int load_collision(void){
 FILE *f=fopen("app0:assets/G66_original_collision.g66c","rb");if(!f)return 0;
 char magic[4];uint32_t header[2];
 if(!read_exact(f,magic,4)||memcmp(magic,"G66C",4)||!read_exact(f,header,8)||
     header[0]!=1||header[1]!=1910||header[1]>MAX_COLLISION){fclose(f);return 0;}
 nwalls=header[1];
 for(uint32_t i=0;i<nwalls;i++){
  Tri *t=&walls[i];
  if(!read_exact(f,t->p,9*sizeof(float))){fclose(f);return 0;}
  t->minx=t->maxx=t->p[0].x;t->miny=t->maxy=t->p[0].y;t->minz=t->maxz=t->p[0].z;
  for(int j=1;j<3;j++){
   Vec p=t->p[j];
   t->minx=fminf(t->minx,p.x);t->maxx=fmaxf(t->maxx,p.x);
   t->miny=fminf(t->miny,p.y);t->maxy=fmaxf(t->maxy,p.y);
   t->minz=fminf(t->minz,p.z);t->maxz=fmaxf(t->maxz,p.z);
  }
  t->normal=cross(sub(t->p[1],t->p[0]),sub(t->p[2],t->p[0]));
  if(dot(t->normal,t->normal)<1.e-8f){fclose(f);return 0;}
  t->normal=norm(t->normal);
  t->wall=fabsf(t->normal.z)<.58f && t->maxz-t->minz>.1f;
 }
 int okay=fgetc(f)==EOF;fclose(f);return okay;
}
/* Find the original source walkable support triangle directly under player.
 * Only accept physically nearby elevations, never snap to arbitrary roof. */
static int source_floor(float x,float y,float feet_z,float *height){
 int found=0;float best=-1e6f;
 for(uint32_t i=0;i<nwalls;i++){
  const Tri *t=&walls[i];
  if(fabsf(t->normal.z)<.65f||x<t->minx-.001f||x>t->maxx+.001f||
     y<t->miny-.001f||y>t->maxy+.001f)continue;
  Vec a=t->p[0],b=t->p[1],c=t->p[2];
  float det=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
  if(fabsf(det)<1e-7f)continue;
  float u=((x-a.x)*(c.y-a.y)-(y-a.y)*(c.x-a.x))/det;
  float v=((b.x-a.x)*(y-a.y)-(b.y-a.y)*(x-a.x))/det;
  if(u<-.0002f||v<-.0002f||u+v>1.0002f)continue;
  float z=a.z+u*(b.z-a.z)+v*(c.z-a.z);
  if(z<=feet_z+.45f&&z>best){found=1;best=z;}
 }
 if(found)*height=best;
 return found;
}
/* At torso height, intersect actual triangle edges with a horizontal Z plane.
 * Prevents crossing source walls; collision data may be broad so use both a
 * coarse broadphase and an exact point-to-intersection-segment distance. */
static int sphere_clear_at(float x,float y,float foot_z,float radius){
 return g67_wall_clear_at(walls,nwalls,x,y,foot_z,radius,PLAYER_HEIGHT);
}
/* Fixed 60Hz with <= 0.22m substeps: RUSH cannot skip thin geometry.
 * Attempt full displacement, then X or Y tangent slide if blocked. */
static void move_swept(Vec displacement){
 int n=(int)ceilf(sqrtf(dot(displacement,displacement))/.22f);
 if(n<1)n=1;if(n>80)n=80;
 Vec step=mul(displacement,1.f/n);
 for(int i=0;i<n;i++){
  Vec old=player.pos;
  float floor_before=0,fx=0,fy=0;
  (void)source_floor(old.x,old.y,old.z,&floor_before);
  if(step.x!=0||step.y!=0){
   float tx=old.x+step.x,ty=old.y+step.y;
   if(g67_horizontal_ok(player.flying,sphere_clear_at(tx,ty,old.z,RAD),!player.flying&&source_floor(tx,ty,old.z+.25f,&fx),old.z,fx)){
    player.pos.x=tx;player.pos.y=ty;
   }else if(g67_horizontal_ok(player.flying,sphere_clear_at(tx,old.y,old.z,RAD),!player.flying&&source_floor(tx,old.y,old.z+.25f,&fx),old.z,fx)){
    player.pos.x=tx;
   }else if(g67_horizontal_ok(player.flying,sphere_clear_at(old.x,ty,old.z,RAD),!player.flying&&source_floor(old.x,ty,old.z+.25f,&fy),old.z,fy)){
    player.pos.y=ty;
   }
  }
  float candidate=player.pos.z+step.z;
  float ground=0;
  if(source_floor(player.pos.x,player.pos.y,candidate+.4f,&ground)){
   if(candidate<ground)candidate=ground;
   /* Downward gravity resolves contact without teleporting to far roofs. */
  }
  /* Ceiling test on upward movement against native walkable geometry
     directly above the player head, excluding original ground. */
  if(step.z>0){
   float h=0;
   if(source_floor(player.pos.x,player.pos.y,candidate+PLAYER_HEIGHT+.1f,&h)&&
      h>old.z+PLAYER_HEIGHT-.05f&&h<candidate+PLAYER_HEIGHT){
       candidate=h-PLAYER_HEIGHT-.05f;player.velocity_z=0;
   }
  }
  if(sphere_clear_at(player.pos.x,player.pos.y,candidate,RAD))player.pos.z=candidate;
  else player.velocity_z=0;
 }
}

static float stick(unsigned char axis){float n=((int)axis-127)/128.f;return fabsf(n)<.17f?0.f:n;}
static void reset_player(void){
 memset(&player,0,sizeof(player));
 player.pos=(Vec){-52.3f,-264.6f,.072501f};
 player.heading=1.1f;player.camera_heading=1.1f;player.camera_pitch=.15f;
 player.health=100;player.show_help=1;
}
static void update(const SceCtrlData *pad,uint32_t *prev_buttons,float dt){
 uint32_t pressed=pad->buttons&~*prev_buttons;
 *prev_buttons=pad->buttons;
 if(pressed&SCE_CTRL_START)player.paused=!player.paused;
 if(pressed&SCE_CTRL_SELECT)player.show_help=!player.show_help;
 if(pressed&SCE_CTRL_UP)reset_player();
 if(player.paused)return;
 float rx=stick(pad->rx),ry=stick(pad->ry);
 player.camera_heading+=rx*dt*1.8f;
 player.camera_pitch=clampf(player.camera_pitch-ry*dt*1.1f,-.38f,1.1f);
 if(pressed&SCE_CTRL_CROSS){player.flying=!player.flying;player.velocity_z=0;player.flight_time=0;}
 float lx=stick(pad->lx),ly=-stick(pad->ly);
 float heading=player.camera_heading;
 float forward_x=sinf(heading),forward_y=cosf(heading);
 float right_x=cosf(heading),right_y=-sinf(heading);
 float dx=forward_x*ly+right_x*lx,dy=forward_y*ly+right_y*lx;
 float length=sqrtf(dx*dx+dy*dy);
 if(length>1.f){dx/=length;dy/=length;}
 if(length>.13f){player.heading=atan2f(dx,dy);}
 float rush=(pad->buttons&SCE_CTRL_RTRIGGER)&&player.flying?1.f:0.f;
 player.cruise=player.flying&&player.flight_time>1.1f;
 float speed=player.flying?(rush?33.f:player.cruise?12.f:6.5f):4.2f;
 float dz=0;
 if(player.flying){
  if(pad->buttons&SCE_CTRL_TRIANGLE)dz+=5.5f;
  if(pad->buttons&SCE_CTRL_CIRCLE)dz-=5.5f;
  if(rush&&ly>.3f)dz+=sinf(player.camera_pitch)*rush*speed;
  player.flight_time+=dt;
 }else{
  float ground=0;
  if(source_floor(player.pos.x,player.pos.y,player.pos.z+.2f,&ground)){
   if(player.pos.z<=ground+.03f){player.pos.z=ground;player.velocity_z=0;}
  }
  player.velocity_z-=13.f*dt;
  dz=player.velocity_z;
 }
 move_swept((Vec){dx*speed*dt,dy*speed*dt,dz*dt});
}
static void mat_perspective(float *p,float fov,float aspect,float zn,float zf){
 memset(p,0,16*sizeof(float));
 float t=1.f/tanf(fov*PI/360.f);
 p[0]=t/aspect;p[5]=t;p[10]=-(zf+zn)/(zf-zn);p[11]=-1.f;p[14]=-2.f*zf*zn/(zf-zn);
}
static void mat_lookat(float *m,Vec eye,Vec target){
 Vec z=norm(sub(eye,target)),x=norm(cross((Vec){0,0,1},z)),y=cross(z,x);
 memset(m,0,16*sizeof(float));
 m[0]=x.x;m[4]=x.y;m[8]=x.z;m[12]=-dot(x,eye);
 m[1]=y.x;m[5]=y.y;m[9]=y.z;m[13]=-dot(y,eye);
 m[2]=z.x;m[6]=z.y;m[10]=z.z;m[14]=-dot(z,eye);
 m[15]=1.f;
}
static void render_mesh(SourceMesh *m){
 glBindBuffer(GL_ARRAY_BUFFER,m->vertex_buffer);
 glEnableClientState(GL_VERTEX_ARRAY);
 glVertexPointer(3,GL_FLOAT,sizeof(Vertex),(const void *)(uintptr_t)0);
 glEnableClientState(GL_TEXTURE_COORD_ARRAY);
 glTexCoordPointer(2,GL_FLOAT,sizeof(Vertex),(const void *)(uintptr_t)12);
 glEnableClientState(GL_COLOR_ARRAY);
 glColorPointer(4,GL_UNSIGNED_BYTE,sizeof(Vertex),(const void *)(uintptr_t)20);
 for(uint32_t i=0;i<m->nb;i++){
  Batch *b=&m->groups[i];
  if(b->tex!=UINT32_MAX){
   glEnable(GL_TEXTURE_2D);glBindTexture(GL_TEXTURE_2D,m->tex[b->tex]);
  }else{glDisable(GL_TEXTURE_2D);}
  glDrawArrays(GL_TRIANGLES,(GLint)b->first,(GLsizei)b->count);
  draw_calls++;
 }
 glDisableClientState(GL_COLOR_ARRAY);glDisableClientState(GL_TEXTURE_COORD_ARRAY);
 glDisableClientState(GL_VERTEX_ARRAY);glDisable(GL_TEXTURE_2D);
 glBindBuffer(GL_ARRAY_BUFFER,0);
}
static float hudcoords[160];
static void hud_line(int *n,float a,float b,float c,float d){
 hudcoords[(*n)++]=a;hudcoords[(*n)++]=b;hudcoords[(*n)++]=c;hudcoords[(*n)++]=d;
}
static void draw_hud(void){
 int n=0;
 hud_line(&n,W*.5f-13.f,H*.5f,W*.5f-4.f,H*.5f);
 hud_line(&n,W*.5f+4.f,H*.5f,W*.5f+13.f,H*.5f);
 hud_line(&n,W*.5f,H*.5f-12.f,W*.5f,H*.5f-4.f);
 hud_line(&n,W*.5f,H*.5f+4.f,W*.5f,H*.5f+12.f);
 /* Health + flight meter line, compact, no bitmap HUD. */
 hud_line(&n,38,510,38+player.health*2,510);
 hud_line(&n,38,503,player.flying?215.f:70.f,503);
 if(player.paused){hud_line(&n,280,280,680,280);hud_line(&n,280,265,680,265);}
 glDisable(GL_DEPTH_TEST);glDisable(GL_TEXTURE_2D);
 glMatrixMode(GL_PROJECTION);glPushMatrix();glLoadIdentity();
 glOrthof(0.f,W,0.f,H,-1.f,1.f);
 glMatrixMode(GL_MODELVIEW);glPushMatrix();glLoadIdentity();
 glColor4f(.25f,.92f,1.f,1.f);
 glEnableClientState(GL_VERTEX_ARRAY);glVertexPointer(2,GL_FLOAT,0,hudcoords);
 glLineWidth(2.f);glDrawArrays(GL_LINES,0,n/2);
 glDisableClientState(GL_VERTEX_ARRAY);
 glPopMatrix();glMatrixMode(GL_PROJECTION);glPopMatrix();
 glMatrixMode(GL_MODELVIEW);glEnable(GL_DEPTH_TEST);
}
static void frame_render(void){
 glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
 Vec pos=player.pos;
 float a=player.camera_heading,p=player.camera_pitch;
 float fx=sinf(a),fy=cosf(a),cp=cosf(p),sp=sinf(p);
 Vec follow={pos.x,pos.y,pos.z+1.45f};
 int center=player.cruise||(player.flying&&(player.flight_time>1.1f));
 float shoulder=center?0.f:1.05f;
 /* Character left of centered reticle; centered camera when cruising / RUSH. */
 Vec eye={pos.x-5.8f*fx*cp+shoulder*cosf(a),
          pos.y-5.8f*fy*cp-shoulder*sinf(a),pos.z+2.05f+5.8f*sp};
 Vec aim={follow.x+shoulder*cosf(a),follow.y-shoulder*sinf(a),follow.z};
 float projection[16],view[16];
 mat_perspective(projection,71.f,(float)W/H,.11f,2350.f);
 mat_lookat(view,eye,aim);
 glMatrixMode(GL_PROJECTION);glLoadMatrixf(projection);
 glMatrixMode(GL_MODELVIEW);glLoadMatrixf(view);
 glEnable(GL_DEPTH_TEST);glDepthFunc(GL_LESS);
 draw_calls=0;
 if(load_ok)render_mesh(&city);
 if(load_ok){
  glMatrixMode(GL_MODELVIEW);glPushMatrix();
  glTranslatef(pos.x,pos.y,pos.z);
  glRotatef(player.heading*180.f/PI,0.f,0.f,-1.f);
  /* Original Mark VI geometry and atlas; animation streams not ported yet. */
  render_mesh(&armor);
  glPopMatrix();
 }
 draw_hud();
}
int main(void){
 sceCtrlSetSamplingMode(SCE_CTRL_MODE_ANALOG);
 reset_player();
 /* Normal native 960x544 init can return false despite successful setup. */
 (void)vglInit(0x1800000);
 glViewport(0,0,W,H);glEnable(GL_DEPTH_TEST);glDisable(GL_CULL_FACE);
 glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
 glClearColor(.011f,.025f,.078f,1.f);
 wall_ok=load_collision();
 load_ok=load_mesh(&city,"app0:assets/G66_city.g66m","G66_city")&&
         load_mesh(&armor,"app0:assets/G66_armor.g66m","G66_armor");
 uint32_t previous=0;
 uint64_t last=sceKernelGetSystemTimeWide(),meter=last;
 int meter_frames=0;
 while(1){
  SceCtrlData p={0};
  sceCtrlPeekBufferPositive(0,&p,1);
  uint64_t now=sceKernelGetSystemTimeWide();
  float dt=clampf((now-last)/1000000.f,0.f,.07f);last=now;
  /* Fixed CPU physics rate with bounded catch-up for Vita hiccups. */
  static float accumulator=0.f;
  accumulator+=dt;if(accumulator>.12f)accumulator=.12f;
  uint32_t newly=p.buttons&~previous;
  if(newly&SCE_CTRL_START)player.paused=!player.paused;
  if(newly&SCE_CTRL_SELECT)player.show_help=!player.show_help;
  if(newly&SCE_CTRL_UP)reset_player();
  /* Only process toggles once per display frame, even if physics takes multiple steps. */
  if(newly&SCE_CTRL_CROSS){player.flying=!player.flying;player.flight_time=0;player.velocity_z=0;}
  while(accumulator>=1.f/60.f){
   if(load_ok&&wall_ok&&!player.paused){
    SceCtrlData hold=p;
    hold.buttons&=~(SCE_CTRL_START|SCE_CTRL_SELECT|SCE_CTRL_UP|SCE_CTRL_CROSS);
    static uint32_t held_prev=0;
    update(&hold,&held_prev,1.f/60.f);
   }
   accumulator-=1.f/60.f;
  }
  previous=p.buttons;
  frame_render();
  vglSwapBuffers(GL_FALSE);
  meter_frames++;
  if(now-meter>=1000000){lastfps=meter_frames;meter_frames=0;meter=now;}
  sceKernelDelayThread(500);
 }
 sceKernelExitProcess(0);
 return 0;
}