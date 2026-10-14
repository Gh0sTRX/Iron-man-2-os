#include "b24_c1_true_source_floor.h"
#include <math.h>
#include <stddef.h>
static int within(float a,float x,float b){return a<=x&&x<=b;}
int b24_c1_true_floor_at(const B24GpuC1Mesh *city,
                         float x,float y,float z,
                         float range,float *out){
 if(!city||!city->vertices||!city->indices||!out||
    !city->original_z_up||city->vertex_count<3||
    !isfinite(x)||!isfinite(y)||!isfinite(z)||!isfinite(range)||
    range<.05f||range>50.f)return 0;
 /* Only the original author-labeled C1L1_ground* meshes.
    Building rooftops must NOT turn into invisible ground contacts. */
 const B24GpuC1Batch *ground=&city->batches[0];
 if(ground->kind!=0||ground->first_index!=0u||
    ground->index_count<3u||ground->index_count%3u||
    ground->index_count>city->index_count)return 0;
 float best=0.f,best_dist=INFINITY;
 int found=0;
 for(size_t i=0;i<ground->index_count;i+=3u){
  const uint16_t i0=city->indices[i],i1=city->indices[i+1],i2=city->indices[i+2];
  if(i0>=city->vertex_count||i1>=city->vertex_count||i2>=city->vertex_count)return 0;
  const B24GpuC1Vertex *a=&city->vertices[i0],*b=&city->vertices[i1],*c=&city->vertices[i2];
  if(!within(fminf(a->x,fminf(b->x,c->x))-.001f,x,
             fmaxf(a->x,fmaxf(b->x,c->x))+.001f)||
     !within(fminf(a->y,fminf(b->y,c->y))-.001f,y,
             fmaxf(a->y,fmaxf(b->y,c->y))+.001f))continue;
  float ux=b->x-a->x,uy=b->y-a->y,uz=b->z-a->z;
  float vx=c->x-a->x,vy=c->y-a->y,vz=c->z-a->z;
  float nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
  float nn=nx*nx+ny*ny+nz*nz;
  if(nn<1e-10f||nz*nz<.36f*nn)continue; /* slopes <= ~53deg */
  float den=(b->y-c->y)*(a->x-c->x)+(c->x-b->x)*(a->y-c->y);
  if(fabsf(den)<1e-8f)continue;
  float wa=((b->y-c->y)*(x-c->x)+(c->x-b->x)*(y-c->y))/den;
  float wb=((c->y-a->y)*(x-c->x)+(a->x-c->x)*(y-c->y))/den;
  float wc=1.f-wa-wb;
  if(wa<-.0001f||wb<-.0001f||wc<-.0001f)continue;
  float height=wa*a->z+wb*b->z+wc*c->z;
  float difference=fabsf(height-z);
  if(!isfinite(height)||difference>range)continue;
  /* Prefer closest real supporting polygon to player's previous ground;
     never teleport to unrelated roadway/bridge roofs. */
  if(!found||difference<best_dist){
    best=height;best_dist=difference;found=1;
  }
 }
 if(found)*out=best;
 return found;
}
