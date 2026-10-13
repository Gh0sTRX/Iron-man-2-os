#include "b24_gpu_camera.h"
#include <math.h>
#include <stddef.h>
typedef B24GpuVec3 V;
static V sub(V a,V b){V c={a.x-b.x,a.y-b.y,a.z-b.z};return c;}
static float dot(V a,V b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static V cross(V a,V b){V c={a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};return c;}
static int normalize(V *v){
 float n=dot(*v,*v);
 if(!isfinite(n)||n<1.e-8f)return 0;
 n=1.f/sqrtf(n);v->x*=n;v->y*=n;v->z*=n;return 1;
}
int b24_gpu_camera_matrices(const B24GpuCamera *c,B24GpuCameraMatrices *out){
 if(!c||!out||!isfinite(c->fov_y_degrees)||!isfinite(c->aspect)||
   !isfinite(c->near_z)||!isfinite(c->far_z)||
   c->fov_y_degrees<15.f||c->fov_y_degrees>130.f||
   c->aspect<.3f||c->aspect>4.f||c->near_z<.02f||
   c->far_z<=c->near_z+.1f||c->far_z>100000.f)return 0;
 V f=sub(c->target,c->eye),u=c->world_up;
 if(!normalize(&f)||!normalize(&u))return 0;
 V r=cross(f,u);if(!normalize(&r))return 0;
 u=cross(r,f);
 float top=c->near_z*tanf(c->fov_y_degrees*.008726646259971648f);
 if(!isfinite(top)||top<=0.f)return 0;
 B24GpuCameraMatrices m={0};
 m.projection[0]=c->near_z/(top*c->aspect);
 m.projection[5]=c->near_z/top;
 m.projection[10]=-(c->far_z+c->near_z)/(c->far_z-c->near_z);
 m.projection[11]=-1.f;
 m.projection[14]=-(2.f*c->far_z*c->near_z)/(c->far_z-c->near_z);
 m.view[0]=r.x;m.view[4]=r.y;m.view[8]=r.z;
 m.view[1]=u.x;m.view[5]=u.y;m.view[9]=u.z;
 m.view[2]=-f.x;m.view[6]=-f.y;m.view[10]=-f.z;
 m.view[12]=-dot(r,c->eye);m.view[13]=-dot(u,c->eye);
 m.view[14]=dot(f,c->eye);m.view[15]=1.f;
 for(int i=0;i<16;i++)if(!isfinite(m.view[i])||!isfinite(m.projection[i]))return 0;
 *out=m;return 1;
}
static void mul(const float *m,const float *v,float *o){
 for(int i=0;i<4;i++)o[i]=m[i]*v[0]+m[4+i]*v[1]+m[8+i]*v[2]+m[12+i]*v[3];
}
int b24_gpu_world_to_screen(const B24GpuCameraMatrices *m,B24GpuVec3 p,
 int w,int h,float *x,float *y,float *z){
 if(!m||!x||!y||!z||w<=0||h<=0||w>4096||h>4096||
 !isfinite(p.x)||!isfinite(p.y)||!isfinite(p.z))return 0;
 float src[4]={p.x,p.y,p.z,1.f},view[4],clip[4];
 mul(m->view,src,view);mul(m->projection,view,clip);
 if(!isfinite(clip[3])||clip[3]<=.0001f)return 0;
 float a=clip[0]/clip[3],b=clip[1]/clip[3],c=clip[2]/clip[3];
 if(!isfinite(a)||!isfinite(b)||!isfinite(c)||fabsf(a)>1.f||
 fabsf(b)>1.f||fabsf(c)>1.f)return 0;
 *x=(a*.5f+.5f)*(float)w;*y=(.5f-b*.5f)*(float)h;*z=c;return 1;
}
