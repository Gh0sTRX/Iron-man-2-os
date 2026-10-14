#include "b24_c1_wall_index.h"
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
/* Stable sparse 2D grid with sorted cells, no per-frame heap allocations.
   Building/rebuilding this index is intentionally a loading-screen action. */
static int coord(float v,int32_t *out){
 if(!isfinite(v)||!out||fabsf(v)>100000.f)return 0;
 float q=floorf(v/B24_C1_WALL_CELL_SIZE);
 if(q<(float)INT32_MIN||q>(float)INT32_MAX)return 0;
 *out=(int32_t)q;return 1;
}
static int cmp_ref(const void *a,const void *b){
 const B24C1WallRef *x=a,*y=b;
 if(x->cx!=y->cx)return x->cx<y->cx?-1:1;
 if(x->cy!=y->cy)return x->cy<y->cy?-1:1;
 return x->wall<y->wall?-1:x->wall>y->wall?1:0;
}
void b24_c1_wall_index_free(B24C1WallIndex *p){
 if(!p)return;
 free(p->walls);free(p->refs);memset(p,0,sizeof(*p));
}
int b24_c1_wall_index_build(B24C1WallIndex *dst,const B24GpuC1Mesh *scene){
 if(!dst||!scene||!scene->vertices||!scene->indices||
  scene->vertex_count!=B24_GPU_C1_VERTS||
  scene->index_count!=B24_GPU_C1_INDICES||!scene->original_z_up)return 0;
 B24C1WallIndex tmp={0};
 tmp.walls=calloc(B24_GPU_C1_INDICES/3u,sizeof(*tmp.walls));
 if(!tmp.walls)return 0;
 size_t cap=8192;
 tmp.refs=malloc(cap*sizeof(*tmp.refs));
 if(!tmp.refs){b24_c1_wall_index_free(&tmp);return 0;}
 size_t previous=0;
 for(uint32_t g=0;g<B24_GPU_C1_BATCHES;g++){
  const B24GpuC1Batch *b=&scene->batches[g];
  if(b->kind!=g||b->first_index!=previous||b->index_count%3u||
     b->first_index+b->index_count>scene->index_count){
    b24_c1_wall_index_free(&tmp);return 0;
  }
  previous=b->first_index+b->index_count;
  for(uint32_t i=b->first_index;i<b->first_index+b->index_count;i+=3){
   tmp.scanned_faces++;
   const uint16_t a=scene->indices[i],c=scene->indices[i+1],d=scene->indices[i+2];
   if(a>=scene->vertex_count||c>=scene->vertex_count||d>=scene->vertex_count){
    b24_c1_wall_index_free(&tmp);return 0;
   }
   /* Authentic category semantics: 0 floor, 1 structures, 2 vehicles,
      3 props. Ground and vehicle geometry remain separately unhandled.
      A building surface is NOT a collider without slope validation. */
   if(g!=1u&&g!=3u){tmp.rejected_nonground++;continue;}
   const B24GpuC1Vertex *u=&scene->vertices[a],
                        *v=&scene->vertices[c],*w=&scene->vertices[d];
   float ax=v->x-u->x,ay=v->y-u->y,az=v->z-u->z,
         bx=w->x-u->x,by=w->y-u->y,bz=w->z-u->z;
   float nx=ay*bz-az*by,ny=az*bx-ax*bz,nz=ax*by-ay*bx;
   float len2=nx*nx+ny*ny+nz*nz;
   float minz=fminf(u->z,fminf(v->z,w->z));
   float maxz=fmaxf(u->z,fmaxf(v->z,w->z));
   float minx=fminf(u->x,fminf(v->x,w->x)),maxx=fmaxf(u->x,fmaxf(v->x,w->x));
   float miny=fminf(u->y,fminf(v->y,w->y)),maxy=fmaxf(u->y,fmaxf(v->y,w->y));
   if(!isfinite(len2)||len2<.0001f||!isfinite(minz)||!isfinite(maxz)||
      !isfinite(minx)||!isfinite(miny)||!isfinite(maxx)||!isfinite(maxy)||
      maxz-minz<.5f||nz*nz>.30f*len2){
    tmp.rejected_degenerate++;continue;
   }
   int32_t cx0,cy0,cx1,cy1;
   /* Radius <= 0.9 world units is the query contract. Pre-expanded
      bounds ensure neighboring cells include real wall surfaces. */
   if(!coord(minx-.9f,&cx0)||!coord(maxx+.9f,&cx1)||
      !coord(miny-.9f,&cy0)||!coord(maxy+.9f,&cy1)){
    b24_c1_wall_index_free(&tmp);return 0;
   }
   uint64_t nxcell=(uint64_t)(cx1-cx0+1),nycell=(uint64_t)(cy1-cy0+1);
   uint64_t added=nxcell*nycell;
   if(!added||added>B24_C1_WALL_MAX_REFS-tmp.ref_count){
    b24_c1_wall_index_free(&tmp);return 0;
   }
   while(tmp.ref_count+(size_t)added>cap){
    size_t next=cap*2u;
    if(next>B24_C1_WALL_MAX_REFS)next=B24_C1_WALL_MAX_REFS;
    if(next<=cap){b24_c1_wall_index_free(&tmp);return 0;}
    B24C1WallRef *nr=realloc(tmp.refs,next*sizeof(*nr));
    if(!nr){b24_c1_wall_index_free(&tmp);return 0;}
    cap=next;tmp.refs=nr;
   }
   uint32_t id=tmp.wall_count++;
   B24C1WallFace *f=&tmp.walls[id];
   const B24GpuC1Vertex *vertex[3]={u,v,w};
   for(int j=0;j<3;j++){
    f->xyz[3*j]=vertex[j]->x;
    f->xyz[3*j+1]=vertex[j]->y;
    f->xyz[3*j+2]=vertex[j]->z;
   }
   f->minz=minz;f->maxz=maxz;f->original_face=i/3u;f->source_group=g;
   for(int32_t gx=cx0;gx<=cx1;gx++){
    for(int32_t gy=cy0;gy<=cy1;gy++){
      tmp.refs[tmp.ref_count++]=(B24C1WallRef){gx,gy,id};
    }
   }
  }
 }
 if(previous!=scene->index_count){b24_c1_wall_index_free(&tmp);return 0;}
 qsort(tmp.refs,tmp.ref_count,sizeof(*tmp.refs),cmp_ref);
 b24_c1_wall_index_free(dst);*dst=tmp;return 1;
}
static size_t first_ref(const B24C1WallIndex *idx,int32_t cx,int32_t cy){
 size_t lo=0,hi=idx->ref_count;
 while(lo<hi){
  size_t mid=lo+(hi-lo)/2u;
  const B24C1WallRef *r=&idx->refs[mid];
  if(r->cx<cx||(r->cx==cx&&r->cy<cy))lo=mid+1u;
  else hi=mid;
 }
 return lo;
}
int b24_c1_wall_index_query(const B24C1WallIndex *idx,
 float x,float y,float torso_z,float radius,
 uint32_t *ids,size_t capacity,size_t *count){
 if(!idx||!count||!isfinite(x)||!isfinite(y)||!isfinite(torso_z)||
   !isfinite(radius)||radius<.05f||radius>.9f||!idx->walls||!idx->refs||
   (!ids&&capacity))return 0;
 int32_t cx0,cy0,cx1,cy1;
 if(!coord(x-radius,&cx0)||!coord(x+radius,&cx1)||
    !coord(y-radius,&cy0)||!coord(y+radius,&cy1))return 0;
 size_t n=0;
 for(int32_t cx=cx0;cx<=cx1;cx++)for(int32_t cy=cy0;cy<=cy1;cy++){
  for(size_t i=first_ref(idx,cx,cy);i<idx->ref_count;i++){
   const B24C1WallRef *ref=&idx->refs[i];
   if(ref->cx!=cx||ref->cy!=cy)break;
   const B24C1WallFace *w=&idx->walls[ref->wall];
   if(torso_z<w->minz||torso_z>w->maxz)continue;
   size_t k=0;while(k<n&&ids[k]!=ref->wall)k++;
   if(k==n){
    if(n>=capacity)return 0; /* fail closed, no silently lost walls */
    ids[n++]=ref->wall;
   }
  }
 }
 *count=n;return 1;
}
