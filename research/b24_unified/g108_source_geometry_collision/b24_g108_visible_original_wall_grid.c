#include "b24_g108_visible_original_wall_grid.h"
#include <math.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* G128 FIX: The previous -336..336 X and -360..264 Y grid silently
 * discarded any sourced steep original Stark Expo source triangles outside
 * its small central viewport. The ACTUAL 2010 BRES scene G19 ranges roughly
 * x[-1219.11,+414.70], y[-1090.07,+531.98]; preserve full source extent.
 * Keep the same 12-unit spatial index (144 x 144 = 20736 cells, ~83KB CSR).
 * Original world/min-max are additionally extracted from actual G66M bytes,
 * never infer mission's playable flight volume from that geometry AABB.
 */
#define G108_CELL 12.f
#define G108_X0 (-2048.f)
#define G108_Y0 (-2048.f)
#define G108_NX 256
#define G108_NY 256
#define G108_NCELLS (G108_NX*G108_NY)
#define G108_MAX_CANDIDATES 18000u
#define G108_MAX_CELL_REFERENCES 320000u
#define G108_EPS .82f
typedef struct {float xyz[3],uv[2];uint8_t rgba[4];} G108Vertex;
_Static_assert(sizeof(G108Vertex)==24,"original G68 GPU VBO ABI");
static int good(float x){return isfinite(x)&&fabsf(x)<1.e5f;}
static int near(const B24C1OriginalCollision *world,float x,float y,float z){
 if(!world||!world->ready)return 0;
 for(uint32_t i=0;i<world->count;i++){
  const B24C1OriginalCollisionFace *f=&world->faces[i];
  if(f->wall&&x>=f->minx-G108_EPS&&x<=f->maxx+G108_EPS&&
     y>=f->miny-G108_EPS&&y<=f->maxy+G108_EPS&&
     z>=f->minz-G108_EPS&&z<=f->maxz+G108_EPS)return 1;
 }
 return 0;
}
static int cellx(float x){return (int)floorf((x-G108_X0)/G108_CELL);}
static int celly(float y){return (int)floorf((y-G108_Y0)/G108_CELL);}
static int clampcell(int a,int max){return a<0?0:a>=max?max-1:a;}
static int cells_for(const B24G108Wall *f,int *x0,int *x1,int *y0,int *y1){
 int a=cellx(f->minx-.92f),b=cellx(f->maxx+.92f);
 int c=celly(f->miny-.92f),d=celly(f->maxy+.92f);
 if(b<0||a>=G108_NX||d<0||c>=G108_NY)return 0;
 a=clampcell(a,G108_NX);b=clampcell(b,G108_NX);
 c=clampcell(c,G108_NY);d=clampcell(d,G108_NY);
 if((b-a+1)*(d-c+1)>72)return 0;
 *x0=a;*x1=b;*y0=c;*y1=d;return 1;
}
void b24_g108_grid_close(B24G108Grid *g){
 if(!g)return;
 free(g->walls);free(g->cell_offsets);free(g->cell_indices);
 memset(g,0,sizeof(*g));
}
static int append(B24G108Grid *g,const B24G108Wall *w){
 if(g->count>=G108_MAX_CANDIDATES)return 0;
 if(g->count==g->capacity){
  uint32_t n=g->capacity?g->capacity*2u:2048u;
  if(n>G108_MAX_CANDIDATES)n=G108_MAX_CANDIDATES;
  B24G108Wall *p=realloc(g->walls,(size_t)n*sizeof(*p));
  if(!p)return 0;
  g->walls=p;g->capacity=n;
 }
 g->walls[g->count++]=*w;return 1;
}
int b24_g108_grid_load(B24G108Grid *g,const char *path,
 const B24C1OriginalCollision *native){
 if(!g||g->ready||!path||!native||!native->ready)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 uint8_t magic[4]={0};uint32_t h[4]={0},batches[32][4]={0};
 int ok=fread(magic,1,4,f)==4&&!memcmp(magic,"G66M",4)&&
        fread(h,4,4,f)==4&&h[0]==1&&h[1]==67323&&
        h[2]==32&&h[3]==31&&fread(batches,sizeof(batches),1,f)==1;
 if(!ok){fclose(f);return 0;}
 const size_t bytes=(size_t)h[1]*sizeof(G108Vertex);
 G108Vertex *v=malloc(bytes);
 if(!v){fclose(f);return 0;}
 ok=fread(v,1,bytes,f)==bytes&&fgetc(f)==EOF;
 fclose(f);
 if(!ok){free(v);return 0;}
 B24G108Grid tmp={0};
 /* Original actual SOURCE rendered G66 city AABB; do not continue using
  * -325..331 central view clipping while importing all original geometry. */
 tmp.source_minx=tmp.source_maxx=v[0].xyz[0];
 tmp.source_miny=tmp.source_maxy=v[0].xyz[1];
 for(uint32_t j=0;j<h[1];j++){
  float x=v[j].xyz[0],y=v[j].xyz[1],z=v[j].xyz[2];
  if(!good(x)||!good(y)||!good(z))goto fail;
  if(x<tmp.source_minx)tmp.source_minx=x;
  if(x>tmp.source_maxx)tmp.source_maxx=x;
  if(y<tmp.source_miny)tmp.source_miny=y;
  if(y>tmp.source_maxy)tmp.source_maxy=y;
 }
 fprintf(stderr,"G128 REAL original 2010 G66 city exact visual bounds: X=%.3f..%.3f Y=%.3f..%.3f; indexed source rect X=%.3f..%.3f Y=%.3f..%.3f\\n",
   tmp.source_minx,tmp.source_maxx,tmp.source_miny,tmp.source_maxy,
   G108_X0,G108_X0+G108_CELL*G108_NX,
   G108_Y0,G108_Y0+G108_CELL*G108_NY);
 if(tmp.source_minx<G108_X0||tmp.source_maxx>G108_X0+G108_CELL*G108_NX||
    tmp.source_miny<G108_Y0||tmp.source_maxy>G108_Y0+G108_CELL*G108_NY){
   fprintf(stderr,"G128 actual original 2010 source AABB exceeds proposed grid, abort rather than silently discard source walls\\n");
   goto fail;
 }
 uint32_t cursor=0;
 const uint8_t translucent[31]={
  0,1,0,0,0,0,1,1,0,1,0,0,0,0,0,1,
  0,0,0,1,1,0,0,0,0,0,0,0,0,0,0};
 for(uint32_t group=0;group<32;group++){
  const uint32_t first=batches[group][0],count=batches[group][1],tex=batches[group][2];
  if(first!=cursor||!count||count%3||count>67323-cursor||
      (tex!=UINT32_MAX&&tex>=31u))goto fail;
  cursor+=count;
  if(tex==UINT32_MAX||translucent[tex]){tmp.skipped_alpha+=count/3;continue;}
  for(uint32_t j=first;j<first+count;j+=3){
   const G108Vertex *a=&v[j],*b=&v[j+1],*c=&v[j+2];
   B24G108Wall w={0};
   for(int k=0;k<3;k++){
    w.p[k]=a->xyz[k];w.p[3+k]=b->xyz[k];w.p[6+k]=c->xyz[k];
   }
   int valid=1;
   for(int k=0;k<9;k++)if(!good(w.p[k]))valid=0;
   if(!valid)goto fail;
   w.minx=w.maxx=w.p[0];w.miny=w.maxy=w.p[1];
   w.minz=w.maxz=w.p[2];
   for(int k=1;k<3;k++){
    const float x=w.p[k*3],y=w.p[k*3+1],z=w.p[k*3+2];
    if(x<w.minx)w.minx=x;
    if(x>w.maxx)w.maxx=x;
    if(y<w.miny)w.miny=y;
    if(y>w.maxy)w.maxy=y;
    if(z<w.minz)w.minz=z;
    if(z>w.maxz)w.maxz=z;
   }
   const float ux=w.p[3]-w.p[0],uy=w.p[4]-w.p[1],uz=w.p[5]-w.p[2];
   const float vx=w.p[6]-w.p[0],vy=w.p[7]-w.p[1],vz=w.p[8]-w.p[2];
   const float nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
   const float n=nx*nx+ny*ny+nz*nz;
   if(n<1.e-7f||nz*nz>=.3364f*n||w.maxz-w.minz<.1f){
    tmp.skipped_not_steep++;continue;
   }
   const float mx=(w.p[0]+w.p[3]+w.p[6])/3;
   const float my=(w.p[1]+w.p[4]+w.p[7])/3;
   const float mz=(w.p[2]+w.p[5]+w.p[8])/3;
   if(near(native,mx,my,mz)){tmp.skipped_duplicate++;continue;}
   int x0,x1,y0,y1;
   if(!cells_for(&w,&x0,&x1,&y0,&y1)||
      w.maxz-w.minz>180.f){tmp.skipped_large++;continue;}
   w.source_batch=group;
   if(!append(&tmp,&w))goto fail;
  }
 }
 if(cursor!=67323u)goto fail;
 free(v);v=NULL;
 /* Two pass CSR fixed cell index, no heap traversal per physics frame. */
 tmp.cell_offsets=calloc(G108_NCELLS+1,sizeof(uint32_t));
 if(!tmp.cell_offsets)goto fail;
 for(uint32_t i=0;i<tmp.count;i++){
  int x0,x1,y0,y1;const B24G108Wall *w=&tmp.walls[i];
  if(!cells_for(w,&x0,&x1,&y0,&y1))goto fail;
  for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
   uint32_t k=(uint32_t)(y*G108_NX+x)+1;
   if(tmp.cell_offsets[k]==UINT32_MAX)goto fail;
   tmp.cell_offsets[k]++;
  }
 }
 for(int k=1;k<=G108_NCELLS;k++){
  if(G108_MAX_CELL_REFERENCES-tmp.cell_offsets[k-1]<tmp.cell_offsets[k])
   goto fail;
  tmp.cell_offsets[k]+=tmp.cell_offsets[k-1];
 }
 tmp.cell_index_count=tmp.cell_offsets[G108_NCELLS];
 tmp.cell_indices=calloc(tmp.cell_index_count?tmp.cell_index_count:1,sizeof(uint32_t));
 uint32_t *cursor_index=calloc(G108_NCELLS,sizeof(uint32_t));
 if(!tmp.cell_indices||!cursor_index){free(cursor_index);goto fail;}
 memcpy(cursor_index,tmp.cell_offsets,G108_NCELLS*sizeof(uint32_t));
 for(uint32_t i=0;i<tmp.count;i++){
  int x0,x1,y0,y1;const B24G108Wall *w=&tmp.walls[i];
  if(!cells_for(w,&x0,&x1,&y0,&y1)){free(cursor_index);goto fail;}
  for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
   int cell=y*G108_NX+x;
   if(cursor_index[cell]>=tmp.cell_offsets[cell+1]){free(cursor_index);goto fail;}
   tmp.cell_indices[cursor_index[cell]++]=i;
  }
 }
 free(cursor_index);
 tmp.ready=1;*g=tmp;return 1;
fail:
 free(v);b24_g108_grid_close(&tmp);return 0;
}
typedef struct {float x,y;} Vec;
static float distance_segment2(Vec p,Vec a,Vec b){
 const float dx=b.x-a.x,dy=b.y-a.y,d=dx*dx+dy*dy;
 float t=d>1.e-9f?((p.x-a.x)*dx+(p.y-a.y)*dy)/d:0.f;
 if(t<0)t=0;
 if(t>1)t=1;
 const float px=p.x-a.x-t*dx,py=p.y-a.y-t*dy;
 return px*px+py*py;
}
static int wall_slice(const B24G108Wall *w,float z,Vec *a,Vec *b){
 Vec pts[6];int n=0;
 for(int k=0;k<3;k++){
  int h=(k+1)%3;
  float z0=w->p[3*k+2],z1=w->p[3*h+2];
  Vec start={w->p[3*k],w->p[3*k+1]};
  if(fabsf(z-z0)<1.e-5f){
   int dup=0;
   for(int t=0;t<n;t++)if(distance_segment2(start,pts[t],pts[t])<1.e-8f)dup=1;
   if(!dup)pts[n++]=start;
  }
  if((z0<z&&z1>z)||(z0>z&&z1<z)){
   float alpha=(z-z0)/(z1-z0);
   Vec pt={start.x+alpha*(w->p[3*h]-start.x),
           start.y+alpha*(w->p[3*h+1]-start.y)};
   int dup=0;
   for(int t=0;t<n;t++)if(distance_segment2(pt,pts[t],pts[t])<1.e-8f)dup=1;
   if(!dup)pts[n++]=pt;
  }
 }
 if(n<2)return 0;
 float best=-1.f;
 for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){
  const float dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y;
  const float d=dx*dx+dy*dy;
  if(d>best){best=d;*a=pts[i];*b=pts[j];}
 }
 return best>1.e-10f;
}
int b24_g108_grid_clear(const B24G108Grid *g,float x,float y,float footz,
 float radius,float height){
 if(!g||!g->ready)return 1; /* OFF/unknown -> do not invent collision */
 if(!good(x)||!good(y)||!good(footz)||!good(radius)||!good(height)||
    radius<.12f||radius>.9f||height<1.f||height>3.5f)return 0;
 int ix=cellx(x),iy=celly(y);
 if(ix<0||ix>=G108_NX||iy<0||iy>=G108_NY)return 1;
 const uint32_t cell=(uint32_t)(iy*G108_NX+ix);
 for(uint32_t k=g->cell_offsets[cell];k<g->cell_offsets[cell+1];k++){
  const B24G108Wall *w=&g->walls[g->cell_indices[k]];
  if(w->maxz<footz||w->minz>footz+height||
     x<w->minx-radius||x>w->maxx+radius||
     y<w->miny-radius||y>w->maxy+radius)continue;
  const float lo=fmaxf(w->minz,footz+.005f);
  const float hi=fminf(w->maxz,footz+height-.005f);
  if(hi<lo)continue;
  const float z[3]={lo,.5f*(lo+hi),hi};
  for(int j=0;j<3;j++){
   Vec a,b;
   if(wall_slice(w,z[j],&a,&b)&&
      distance_segment2((Vec){x,y},a,b)<radius*radius)return 0;
  }
 }
 return 1;
}
/* G128 source-derived conservative scene envelope, not the original
 * authored MissionPlayableArea or character flight-ability flag. */
int b24_g108_grid_source_bounds_allow(const B24G108Grid *g,
 float x,float y,float radius){
 if(!g||!g->ready||!good(x)||!good(y)||!isfinite(radius)||
    radius<.12f||radius>.9f)return 0;
 return x>=g->source_minx+radius&&x<=g->source_maxx-radius&&
        y>=g->source_miny+radius&&y<=g->source_maxy-radius;
}
int b24_g108_grid_probe(const B24G108Grid *g,float *x,float *y,float *footz){
 if(!g||!g->ready||!g->count||!x||!y||!footz)return 0;
 const B24G108Wall *w=&g->walls[0];
 *x=(w->p[0]+w->p[3]+w->p[6])/3;
 *y=(w->p[1]+w->p[4]+w->p[7])/3;
 *footz=(w->p[2]+w->p[5]+w->p[8])/3-.3f;
 return 1;
}
