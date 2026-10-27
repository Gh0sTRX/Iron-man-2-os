#include "b24_g160_original_road_spatial.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#define G160_STEP 16.f
#define G160_MAX_CELLS 65536u
#define G160_MAX_REFS 500000u
static int cell_of(const B24G159Road *r,float x,float y,
                   uint32_t *cx,uint32_t *cy){
 const float fx=floorf((x-r->cell_origin_x)/G160_STEP);
 const float fy=floorf((y-r->cell_origin_y)/G160_STEP);
 if(!isfinite(fx)||!isfinite(fy)||fx<0.f||fy<0.f||
    fx>=(float)r->cell_cols||fy>=(float)r->cell_rows)return 0;
 *cx=(uint32_t)fx;*cy=(uint32_t)fy;
 return 1;
}
static int face_cells(const B24G159Road *r,const B24G159RoadFace *f,
                      uint32_t *x0,uint32_t *x1,uint32_t *y0,uint32_t *y1){
 /* G159 native tri_z permits .0001 source XY boundary epsilon. Do NOT
  * cull those valid positions by an over-tight spatial lookup. */
 return cell_of(r,f->minx-.0002f,f->miny-.0002f,x0,y0)&&
        cell_of(r,f->maxx+.0002f,f->maxy+.0002f,x1,y1);
}
void b24_g160_index_close(B24G159Road *r){
 if(!r)return;
 free(r->cell_offsets);
 free(r->cell_face_ids);
 r->cell_offsets=NULL;
 r->cell_face_ids=NULL;
 r->cell_cols=0;r->cell_rows=0;
 r->cell_ref_count=0;r->spatial_index_ready=0;
}
int b24_g160_index_build(B24G159Road *r){
 if(!r||!r->count||!r->faces||r->spatial_index_ready||
    r->cell_offsets||r->cell_face_ids)return 0;
 float xlo=r->faces[0].minx,xhi=r->faces[0].maxx;
 float ylo=r->faces[0].miny,yhi=r->faces[0].maxy;
 for(uint32_t i=1;i<r->count;i++){
  const B24G159RoadFace *f=&r->faces[i];
  if(f->minx<xlo)xlo=f->minx;
  if(f->maxx>xhi)xhi=f->maxx;
  if(f->miny<ylo)ylo=f->miny;
  if(f->maxy>yhi)yhi=f->maxy;
 }
 r->cell_origin_x=floorf(xlo/G160_STEP)*G160_STEP-G160_STEP;
 r->cell_origin_y=floorf(ylo/G160_STEP)*G160_STEP-G160_STEP;
 const float xf=floorf((xhi-r->cell_origin_x)/G160_STEP)+2.f;
 const float yf=floorf((yhi-r->cell_origin_y)/G160_STEP)+2.f;
 if(!isfinite(xf)||!isfinite(yf)||xf<1.f||yf<1.f||
    xf>(float)G160_MAX_CELLS||yf>(float)G160_MAX_CELLS)goto fail;
 r->cell_cols=(uint32_t)xf;r->cell_rows=(uint32_t)yf;
 if(r->cell_cols>G160_MAX_CELLS/r->cell_rows)goto fail;
 const uint32_t cells=r->cell_cols*r->cell_rows;
 r->cell_offsets=calloc((size_t)cells+1u,sizeof(uint32_t));
 if(!r->cell_offsets)goto fail;
 for(uint32_t i=0;i<r->count;i++){
  uint32_t x0,x1,y0,y1;
  if(!face_cells(r,&r->faces[i],&x0,&x1,&y0,&y1))goto fail;
  for(uint32_t y=y0;y<=y1;y++)for(uint32_t x=x0;x<=x1;x++){
   const uint32_t k=y*r->cell_cols+x+1u;
   if(r->cell_offsets[k]==UINT32_MAX)goto fail;
   r->cell_offsets[k]++;
  }
 }
 for(uint32_t k=1;k<=cells;k++){
  const uint32_t previous=r->cell_offsets[k-1];
  if(previous>G160_MAX_REFS||
     r->cell_offsets[k]>G160_MAX_REFS-previous)goto fail;
  r->cell_offsets[k]+=previous;
 }
 r->cell_ref_count=r->cell_offsets[cells];
 r->cell_face_ids=calloc((size_t)r->cell_ref_count+1u,sizeof(uint32_t));
 uint32_t *cursor=malloc((size_t)cells*sizeof(uint32_t));
 if(!cursor||!r->cell_face_ids){free(cursor);goto fail;}
 memcpy(cursor,r->cell_offsets,(size_t)cells*sizeof(uint32_t));
 for(uint32_t i=0;i<r->count;i++){
  uint32_t x0,x1,y0,y1;
  if(!face_cells(r,&r->faces[i],&x0,&x1,&y0,&y1)){
   free(cursor);goto fail;
  }
  for(uint32_t y=y0;y<=y1;y++)for(uint32_t x=x0;x<=x1;x++){
   const uint32_t k=y*r->cell_cols+x;
   if(cursor[k]>=r->cell_offsets[k+1]){
    free(cursor);goto fail;
   }
   r->cell_face_ids[cursor[k]++]=i;
  }
 }
 free(cursor);
 r->spatial_index_ready=1;
 return 1;
fail:
 b24_g160_index_close(r);
 return 0;
}
int b24_g160_index_query(const B24G159Road *r,float x,float y,
                        uint32_t *begin,uint32_t *end){
 if(!r||!begin||!end)return 0;
 if(!r->spatial_index_ready){
  *begin=0;*end=r->count;
  return 1;
 }
 uint32_t cx,cy;
 if(!cell_of(r,x,y,&cx,&cy))return 0;
 const uint32_t cell=cy*r->cell_cols+cx;
 *begin=r->cell_offsets[cell];
 *end=r->cell_offsets[cell+1u];
 return 1;
}
