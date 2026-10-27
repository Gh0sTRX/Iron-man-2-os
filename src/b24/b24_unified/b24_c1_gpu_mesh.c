#include "b24_c1_gpu_mesh.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t u32(const unsigned char *p){
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
_Static_assert(sizeof(B24GpuC1Vertex)==16,"B24 GPU vertex layout changed");
_Static_assert(sizeof(B24GpuC1Batch)==40,"B24 GPU batch layout changed");

void b24_gpu_c1_free(B24GpuC1Mesh *s){
    if(!s)return;
    free(s->vertices);free(s->indices);
    memset(s,0,sizeof(*s));
}
int b24_gpu_c1_load(B24GpuC1Mesh *mesh,const char *path){
    if(!mesh||!path)return 0;
    FILE *f=fopen(path,"rb");
    if(!f)return 0;
    unsigned char h[28];
    int ok=fread(h,1,28,f)==28 && memcmp(h,"C1G2",4)==0;
    if(ok)ok=u32(h+4)==2&&u32(h+8)==sizeof(B24GpuC1Vertex)&&
          u32(h+12)==B24_GPU_C1_VERTS && u32(h+16)==B24_GPU_C1_INDICES &&
          u32(h+20)==B24_GPU_C1_BATCHES&&u32(h+24)==sizeof(B24GpuC1Batch);
    const size_t nverts=B24_GPU_C1_VERTS,nix=B24_GPU_C1_INDICES;
    const size_t len=28+4*sizeof(B24GpuC1Batch)+nverts*sizeof(B24GpuC1Vertex)+nix*sizeof(uint16_t);
    if(ok && fseek(f,0,SEEK_END))ok=0;
    long filelen=ok?ftell(f):-1;
    if(filelen<0 || (size_t)filelen!=len)ok=0;
    if(ok && fseek(f,28,SEEK_SET))ok=0;
    B24GpuC1Mesh candidate={0};
    if(ok && fread(candidate.batches,sizeof(B24GpuC1Batch),4,f)!=4)ok=0;
    if(ok){
       candidate.vertices=malloc(nverts*sizeof(*candidate.vertices));
       candidate.indices=malloc(nix*sizeof(*candidate.indices));
       if(!candidate.vertices||!candidate.indices)ok=0;
    }
    if(ok && fread(candidate.vertices,sizeof(*candidate.vertices),nverts,f)!=nverts)ok=0;
    if(ok && fread(candidate.indices,sizeof(*candidate.indices),nix,f)!=nix)ok=0;
    fclose(f);
    if(ok){
      size_t previous=0,total=0;
      for(unsigned g=0;g<4;g++){
        const B24GpuC1Batch *b=&candidate.batches[g];
        if(b->kind!=g||b->first_index!=previous||
           b->index_count==0||b->index_count%3 ||
           b->source_meshes==0||b->first_index+b->index_count>nix){ok=0;break;}
        for(unsigned k=0;k<6;k++)if(!isfinite(b->bbox[k])){ok=0;break;}
        if(!ok)break;
        previous=b->first_index+b->index_count; total+=b->index_count;
      }
      if(total!=nix)ok=0;
      for(size_t k=0;k<nix&&ok;k++)if(candidate.indices[k]>=nverts)ok=0;
      for(size_t k=0;k<nverts&&ok;k++){
        const B24GpuC1Vertex *v=&candidate.vertices[k];
        if(!isfinite(v->x)||!isfinite(v->y)||!isfinite(v->z)||
           fabsf(v->x)>100000.f||fabsf(v->y)>100000.f||fabsf(v->z)>100000.f)ok=0;
      }
    }
    if(!ok){b24_gpu_c1_free(&candidate);return 0;}
    candidate.vertex_count=nverts;
    candidate.index_count=nix;
    candidate.original_z_up=1;
    b24_gpu_c1_free(mesh);
    *mesh=candidate;
    return 1;
}
