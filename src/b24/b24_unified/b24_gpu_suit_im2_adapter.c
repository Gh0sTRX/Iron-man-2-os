#include "b24_gpu_suit_im2_adapter.h"
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
_Static_assert(sizeof(IM2Vertex)==sizeof(B24GpuSuitVertex),"original IM2T vertex layout drift");
_Static_assert(sizeof(IM2Triangle)==sizeof(B24GpuSuitTriangle),"original IM2T triangle layout drift");

void b24_gpu_im2_stream_free(B24GpuIM2Stream *s){
 if(!s)return;
 free(s->dynamic_vertices);free(s->static_triangles);
 memset(s,0,sizeof(*s));
}
static int source_valid(const IM2Model *m){
 if(!m||!m->vertices||!m->triangles||!m->texture||
    m->nv<3||m->nv>16000||!m->nt||m->nt>24000||
    !m->tw||m->tw>2048||!m->th||m->th>2048||
    !isfinite(m->center_z))return 0;
 for(uint32_t k=0;k<m->nv;k++){
  const IM2Vertex v=m->vertices[k];
  if(!isfinite(v.x)||!isfinite(v.y)||!isfinite(v.z)||
     !isfinite(v.u)||!isfinite(v.v))return 0;
 }
 for(uint32_t k=0;k<m->nt;k++){
  const IM2Triangle t=m->triangles[k];
  if(t.i0>=m->nv||t.i1>=m->nv||t.i2>=m->nv)return 0;
 }
 return 1;
}
int b24_gpu_im2_stream_init(B24GpuIM2Stream *s,const IM2Model *m){
 if(!s||s->dynamic_vertices||s->static_triangles||!source_valid(m))return 0;
 B24GpuSuitVertex *v=malloc((size_t)m->nv*sizeof(*v));
 B24GpuSuitTriangle *t=malloc((size_t)m->nt*sizeof(*t));
 if(!v||!t){free(v);free(t);return 0;}
 memcpy(v,m->vertices,(size_t)m->nv*sizeof(*v));
 memcpy(t,m->triangles,(size_t)m->nt*sizeof(*t));
 s->dynamic_vertices=v;s->static_triangles=t;
 s->source=(B24GpuSuitSource){v,t,m->texture,m->nv,m->nt,m->tw,m->th,m->center_z};
 s->atlas_source=m->texture;
 return 1;
}
int b24_gpu_im2_stream_update(B24GpuIM2Stream *s,const IM2Model *m){
 if(!s||!s->dynamic_vertices||!s->static_triangles||!m||
    !m->vertices||m->nv!=s->source.nv||m->nt!=s->source.nt||
    m->texture!=s->atlas_source||m->tw!=s->source.tw||m->th!=s->source.th||
    !isfinite(m->center_z))return 0;
 /* B14 original baked mesh animation + B16 right-arm blend already wrote
    IM2Model.vertices. Preserve its XYZ and UV in a persistent draw buffer.
    No independent animation clock; update EXACTLY ONCE after game pose update.
    One per-frame memcpy, NOT a CPU screen raster and NOT an RGBA upload. */
 memcpy(s->dynamic_vertices,m->vertices,(size_t)m->nv*sizeof(*s->dynamic_vertices));
 s->source.center_z=m->center_z;
 s->source.native_bind_min_z=m->native_bind_min_z;
 return 1;
}
