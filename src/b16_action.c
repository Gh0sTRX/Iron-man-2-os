#include "b16_action.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
static unsigned u32(FILE *f,int *ok){unsigned char b[4];if(fread(b,1,4,f)!=4){*ok=0;return 0;}return (unsigned)b[0]|((unsigned)b[1]<<8)|((unsigned)b[2]<<16)|((unsigned)b[3]<<24);}
static int clip_load(B13Clip *c,const char *prefix,const char *suffix,unsigned verts){
 char path[160];
#ifdef __vita__
 snprintf(path,sizeof(path),"app0:animations/%s_%s.im2v",prefix,suffix);
#else
 snprintf(path,sizeof(path),"animations/%s_%s.im2v",prefix,suffix);
#endif
 FILE *f=fopen(path,"rb");if(!f)return 0;
 char magic[4]={0};int ok=1;
 if(fread(magic,1,4,f)!=4||memcmp(magic,"IM2V",4)!=0){fclose(f);return 0;}
 unsigned nv=u32(f,&ok),n=u32(f,&ok),fps=u32(f,&ok),ms=u32(f,&ok);
 if(!ok||nv!=verts||n<2||n>160||fps!=20||ms<100||ms>20000){fclose(f);return 0;}
 size_t count=(size_t)nv*n*3;
 if(count>650000u){fclose(f);return 0;}
 float *xyz=(float*)malloc(count*sizeof(float));
 if(!xyz){fclose(f);return 0;}
 if(fread(xyz,sizeof(float),count,f)!=count||fgetc(f)!=EOF){free(xyz);fclose(f);return 0;}
 fclose(f);
 for(size_t i=0;i<count;i++)if(!isfinite(xyz[i])){free(xyz);return 0;}
 c->xyz=xyz;c->verts=nv;c->frames=n;c->fps=fps;c->duration_ms=ms;return 1;
}
void b16_action_release(B16Action *a){if(!a)return;free(a->air_idle.xyz);free(a->ground_relaxed.xyz);free(a->glide.xyz);
 for(int i=0;i<6;i++)free(a->beam[i].xyz);
 free(a->arm_mask);memset(a,0,sizeof(*a));}
int b16_action_load(B16Action *a,int armor,const IM2Model *model){
 if(!a||!model||!model->nv)return 0;
 b16_action_release(a);a->nverts=model->nv;
 const char *prefix=armor==4?"suitcase":armor==2?"warmachine":"mark6";
 a->palm_l=armor==4?256:armor==2?831:612;
 a->palm_r=armor==4?549:armor==2?967:731;
 if(!clip_load(&a->air_idle,prefix,"air_idle",a->nverts))goto fail;
 if(armor==2){if(!clip_load(&a->ground_relaxed,prefix,"ground_relaxed",a->nverts))goto fail;
              if(!clip_load(&a->glide,prefix,"glide",a->nverts))goto fail;}
 for(int i=0;i<6;i++){
   char suffix[36];snprintf(suffix,sizeof(suffix),"beam_%s_%d",i<3?"ground":"float",(i%3)+1);
   if(!clip_load(&a->beam[i],prefix,suffix,a->nverts))goto fail;
 }
 char path[160];
#ifdef __vita__
 snprintf(path,sizeof(path),"app0:animations/%s_arm_mask.im2m",prefix);
#else
 snprintf(path,sizeof(path),"animations/%s_arm_mask.im2m",prefix);
#endif
 FILE *f=fopen(path,"rb");if(!f)goto fail;
 unsigned char tag[4];int ok=1;
 if(fread(tag,1,4,f)!=4||memcmp(tag,"IM2M",4)){fclose(f);goto fail;}
 unsigned nv=u32(f,&ok);if(!ok||nv!=a->nverts){fclose(f);goto fail;}
 a->arm_mask=(unsigned char*)malloc(nv);if(!a->arm_mask){fclose(f);goto fail;}
 if(fread(a->arm_mask,1,nv,f)!=nv||fgetc(f)!=EOF){fclose(f);goto fail;}
   fclose(f);
  /* Keep genuine upper-body source pose only on the right half of suit.
     Mid-plane inferred from known BOTH original palm vertices; no guessed
     +X/-X naming and no procedural arm pose substitution.
     The original B16 mask continues to isolate arms from ground gait.
     Bind-stage mesh coordinates must remain stable for this precomputation. */
  if(a->palm_l>=model->nv||a->palm_r>=model->nv)goto fail;
  const IM2Vertex left=model->vertices[a->palm_l];
  const IM2Vertex right=model->vertices[a->palm_r];
  const float vx=right.x-left.x,vy=right.y-left.y,vz=right.z-left.z;
  const float span=vx*vx+vy*vy+vz*vz;
  if(!(span>1.e-5f))goto fail;
  const float mx=(left.x+right.x)*.5f,my=(left.y+right.y)*.5f,
              mz=(left.z+right.z)*.5f;
  for(unsigned i=0;i<a->nverts;i++){
      const IM2Vertex v=model->vertices[i];
      const float side=(v.x-mx)*vx+(v.y-my)*vy+(v.z-mz)*vz;
      if(side<0.f)a->arm_mask[i]=0;
  }
  return 1;
fail:b16_action_release(a);return 0;
}
const B13Clip *b16_idle_override(const B16Action *a,B14Mode mode,int armor){
 if(!a)return NULL;
 if(mode==B14_HOVER && a->air_idle.xyz)return &a->air_idle;
 if(mode==B14_IDLE && armor==2 && a->ground_relaxed.xyz)return &a->ground_relaxed;
 if(mode==B14_DRIFT && armor==2 && a->glide.xyz)return &a->glide;
 return NULL;
}
void b16_attack_begin(B16Action *a,unsigned now,int flying,int hand,int variant){
 if(!a)return;
 a->attack_started=now;a->attack_active=1;a->attack_clip=(flying?3:0)+(variant%3);a->hand=hand;
}
void b16_apply_attack(B16Action *a,IM2Model *m,unsigned now){
 if(!a||!m||!a->attack_active||!a->arm_mask)return;
 B13Clip *c=&a->beam[a->attack_clip];
 if(!c->xyz||m->nv!=c->verts)return;
 unsigned age=now-a->attack_started;
 if(age>=c->duration_ms){a->attack_active=0;return;}
 unsigned ix=(unsigned)((uint64_t)age*c->fps/1000u);if(ix>=c->frames)ix=c->frames-1;
 unsigned iy=ix+1<c->frames?ix+1:ix;
 float alpha=((float)age-ix*50.f)/50.f;if(alpha<0)alpha=0;if(alpha>1)alpha=1;
 float envelope=fminf(1.f,fminf(age/95.f,(c->duration_ms-age)/130.f));
 for(unsigned i=0;i<m->nv;i++){
  float mask=(a->arm_mask[i]/255.f)*envelope;
  if(mask<.001f)continue;
  size_t j=(size_t)i*3,k=(size_t)ix*m->nv*3+j,l=(size_t)iy*m->nv*3+j;
  const float x=c->xyz[k]*(1-alpha)+c->xyz[l]*alpha;
  const float y=c->xyz[k+1]*(1-alpha)+c->xyz[l+1]*alpha;
  const float z=c->xyz[k+2]*(1-alpha)+c->xyz[l+2]*alpha;
  m->vertices[i].x+=(x-m->vertices[i].x)*mask;
  m->vertices[i].y+=(y-m->vertices[i].y)*mask;
  m->vertices[i].z+=(z-m->vertices[i].z)*mask;
 }
}
static float cap(float x,float low,float high){return x<low?low:(x>high?high:x);}
static const float targets[3][3]={{0.f,7.f,.55f},{3.f,10.f,.95f},{-3.5f,13.f,1.5f}};
static int damage(B16Combat *c,B14World *w,int i,float points);
void b16_combat_init(B16Combat *c){memset(c,0,sizeof(*c));c->energy=100.f;for(int i=0;i<3;i++)c->hitpoints[i]=100.f;}
void b16_combat_tick(B16Combat *c,B14World *w,float dt){
 dt=cap(dt,0,.12f);c->cooldown=fmaxf(0,c->cooldown-dt);c->hit_flash=fmaxf(0,c->hit_flash-dt);
 c->energy=fminf(100.f,c->energy+dt*9.f);
 if((unsigned)w->waves!=c->wave){c->wave=(unsigned)w->waves;for(int i=0;i<3;i++)c->hitpoints[i]=100.f;c->combo_step=0;c->active_missile=0;}
 if(c->active_missile){
  int i=w->hits<3?w->hits:2;
  float dx=targets[i][0]-c->missile_x,dy=targets[i][1]-c->missile_y,dz=targets[i][2]-c->missile_z;
  float dis=sqrtf(dx*dx+dy*dy+dz*dz);
  if(dis<.55f){c->active_missile=0;damage(c,w,i,100.f);}
  else{float step=fminf(dis,8.0f*dt);if(dis>.0001f){c->missile_x+=step*dx/dis;c->missile_y+=step*dy/dis;c->missile_z+=step*dz/dis;}}
 }
}
void b16_combat_mode(B16Combat *c,int direction){c->mode=(c->mode+direction+B16_WEAPON_COUNT*5)%B16_WEAPON_COUNT;c->combo_step=0;}
int b16_ray_sphere(const float o[3],const float d[3],const float c[3],float radius,float *distance){
 float ox=o[0]-c[0],oy=o[1]-c[1],oz=o[2]-c[2];
 float a=d[0]*d[0]+d[1]*d[1]+d[2]*d[2];if(a<1e-10f)return 0;
 float b=2*(ox*d[0]+oy*d[1]+oz*d[2]),dd=b*b-4*a*(ox*ox+oy*oy+oz*oz-radius*radius);
 if(dd<0)return 0;
 float s=sqrtf(dd);float t=(-b-s)/(2*a);if(t<0)t=(-b+s)/(2*a);if(t<0)return 0;
 if(distance)*distance=t;
 return 1;
}
void b16_model_palm(const IM2Model *m,const B14World *w,unsigned v,float point[3]){
 if(!m||!m->nv){point[0]=w->x;point[1]=w->y;point[2]=w->z;return;}
 if(v>=m->nv)v=0;
 const IM2Vertex p=m->vertices[v];float c=cosf(w->heading),s=sinf(w->heading);
 point[0]=w->x-p.x*c-p.y*s;point[1]=w->y+p.x*s-p.y*c;
 point[2]=w->z+p.z-m->center_z;
}
static int damage(B16Combat *c,B14World *w,int i,float points){
 if(i<0||i>=3||w->completed||i!=w->hits)return 0;
 if(c->hitpoints[i]<=0)return 0;
 c->hitpoints[i]-=points;c->hit_flash=.13f;
 if(c->hitpoints[i]<=0){w->hits++;w->total_hits++;
  if(w->hits==3){w->completed=1;w->wave_timer=1.35f;}else b14_world_target(w);return 1;}
 return 0;
}
static int target_camera_lock(const B14World *w,int target,float *impact){
  /* Reconstruct the camera ray through the HUD reticle using the exact
     third-person world_to_screen inverse, not a screen-space hit radius. */
  const float rcos=cosf(w->orbit),rsin=sinf(w->orbit);
  const float rx=rcos,ry=-rsin,fx=rsin,fy=rcos;
  const float radial=w->camera_distance*cosf(w->pitch);
  const float orig[3]={w->cam_x-fx*radial+rx*.55f,
                       w->cam_y-fy*radial+ry*.55f,
                       w->cam_z+w->camera_distance*sinf(w->pitch)+.07f};
  const float right=(278.f-240.f)/350.f, up=(100.f-110.f)/350.f;
  float dir[3]={fx*(cosf(w->pitch)+up*sinf(w->pitch))+rx*right,
                fy*(cosf(w->pitch)+up*sinf(w->pitch))+ry*right,
                -sinf(w->pitch)+up*cosf(w->pitch)};
  float norm=sqrtf(dir[0]*dir[0]+dir[1]*dir[1]+dir[2]*dir[2]);
  for(int k=0;k<3;k++)dir[k]/=norm;
  float t=0;
  if(!b16_ray_sphere(orig,dir,targets[target],.58f,&t))return 0;
  if(impact)for(int k=0;k<3;k++)impact[k]=orig[k]+t*dir[k];
  return 1;
}
int b16_combat_fire(B16Combat *c,B14World *w,const float muzzle[3]){
 if(c->cooldown>0)return -1;
 if(c->mode==B16_UNIBEAM&&c->energy<50)return -2;
 if(c->mode==B16_MISSILE&&c->energy<25)return -2;
 if(w->completed){
  /* After clearing a wave, the player can still fire into space. */
  c->shots++;w->shots++;c->cooldown=.24f;w->beam_time=.15f;
  return 0;
 }
 int target=w->hits;if(target<0||target>2)return -3;
 float dx=targets[target][0]-muzzle[0],dy=targets[target][1]-muzzle[1],dz=targets[target][2]-muzzle[2];
 float dist=sqrtf(dx*dx+dy*dy+dz*dz);
 /* Genuine world-range and facing test, rather than an on-screen melee hit. */
 if(c->mode==B16_MELEE){
  if(dist>2.2f)return -4;
  c->combo_step=c->combo_step%3+1;
  c->cooldown=.37f;c->shots++;w->shots++;
  damage(c,w,target,30.f+15.f*c->combo_step);return 1;
 }
 float hitpoint[3];int locked=target_camera_lock(w,target,hitpoint);
 if(c->mode==B16_MISSILE){
  if(!locked)return 0;
  c->energy-=25.f;c->cooldown=.8f;c->shots++;w->shots++;
  c->active_missile=1;c->missile_x=muzzle[0];c->missile_y=muzzle[1];c->missile_z=muzzle[2];
  return 1;
 }
 c->shots++;w->shots++;c->cooldown=c->mode==B16_UNIBEAM?1.f:.24f;
 w->beam_time=c->mode==B16_UNIBEAM?.3f:.15f;
 if(c->mode==B16_UNIBEAM)c->energy-=50.f;
 if(!locked)return 0;
 /* The original damage values are not known. 3D camera ray hit confirmed;
    beam originates at current animated palm and converges on the hit point. */
 float vec[3]={hitpoint[0]-muzzle[0],hitpoint[1]-muzzle[1],hitpoint[2]-muzzle[2]};
 float len=sqrtf(vec[0]*vec[0]+vec[1]*vec[1]+vec[2]*vec[2]);
 if(len<1e-4f)return 0;
 for(int k=0;k<3;k++)vec[k]/=len;
 float distance=0;
 if(!b16_ray_sphere(muzzle,vec,targets[target],.58f,&distance))return 0;
 damage(c,w,target,c->mode==B16_UNIBEAM?130.f:35.f);
 return 1;
}
