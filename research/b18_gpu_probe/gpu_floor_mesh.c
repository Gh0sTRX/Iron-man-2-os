#include "gpu_floor_mesh.h"
#include <math.h>
#include <stddef.h>
static void vertex(Im2GpuFloorVertex *v,float x,float y,float z,
                   float r,float g,float b,float u,float t) {
    *v=(Im2GpuFloorVertex){x,y,z,r,g,b,u,t};
}
int im2_gpu_floor_build(Im2GpuFloorMesh *m,float player_x,float player_y) {
    if(!m||!isfinite(player_x)||!isfinite(player_y)||
       fabsf(player_x)>100000.f||fabsf(player_y)>100000.f)return 0;
    const int base_x=(int)floorf(player_x/2.f)*2;
    const int base_y=(int)floorf(player_y/2.f)*2;
    unsigned v=0,ix=0;
    /* Keep B17's world-space 11x11 checkerboard dimensions and coloring. */
    for(int j=-5;j<=5;j++)for(int i=-5;i<=5;i++){
        float x=(float)(base_x+2*i),y=(float)(base_y+2*j);
        int edge=(i%4==0||j%4==0);
        float r=edge?28.f:((i+j)&1)?20.f:43.f;
        float g=edge?83.f:((i+j)&1)?59.f:96.f;
        float b=edge?112.f:((i+j)&1)?82.f:117.f;
        if(i==0&&j==0){r=73.f;g=117.f;b=91.f;}
        r/=255.f;g/=255.f;b/=255.f;
        vertex(&m->vertices[v+0],x,    y,    -1.f,r,g,b,0.f,0.f);
        vertex(&m->vertices[v+1],x+2.f,y,    -1.f,r,g,b,1.f,0.f);
        vertex(&m->vertices[v+2],x+2.f,y+2.f,-1.f,r,g,b,1.f,1.f);
        vertex(&m->vertices[v+3],x,    y+2.f,-1.f,r,g,b,0.f,1.f);
        const uint16_t indices[6]={(uint16_t)v,(uint16_t)(v+1),(uint16_t)(v+2),
                                    (uint16_t)v,(uint16_t)(v+2),(uint16_t)(v+3)};
        for(int k=0;k<6;k++)m->indices[ix++]=indices[k];
        v+=4;
    }
    m->vertex_count=v;m->index_count=ix;m->tile_x=base_x;m->tile_y=base_y;
    return v==IM2_GPU_FLOOR_VERTS&&ix==IM2_GPU_FLOOR_INDICES;
}
