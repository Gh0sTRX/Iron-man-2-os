#include "b24_gpu_runtime.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int prepares=0,releases=0;
int b24_gpu_suit_prepare(B24GpuSuit *cache,const B24GpuSuitSource *src){
 assert(cache&&!cache->prepared&&src&&src->texture_rgba);
 cache->prepared=1;cache->texture_id=(unsigned)(++prepares);
 cache->nv=src->nv;cache->nt=src->nt;
 cache->tw=src->tw;cache->th=src->th;
 return 1;
}
void b24_gpu_suit_release(B24GpuSuit *cache){
 assert(cache);if(cache->prepared)releases++;
 memset(cache,0,sizeof(*cache));
}
int main(void){
 IM2Vertex verts[4]={{0,0,0,0,0},{1,0,0,1,0},{0,1,0,0,1},{1,1,0,1,1}};
 IM2Triangle tri[2]={{0,1,2},{1,3,2}};
 unsigned char atlas[16]={1,2,3,255,4,5,6,255,7,8,9,255,10,11,12,255};
 IM2Model original={0};
 original.vertices=verts;original.triangles=tri;original.texture=atlas;
 original.nv=4;original.nt=2;original.tw=2;original.th=2;
 B24GpuRuntime gpu={0};
 gpu.initialized=1;gpu.loaded_suit_index=-1;
 assert(!b24_gpu_runtime_sync_model(&gpu,&original,-1));
 assert(!b24_gpu_runtime_sync_model(&gpu,&original,5));
 assert(b24_gpu_runtime_sync_model(&gpu,&original,0));
 assert(gpu.suit_rebinds==1&&prepares==1&&releases==0);
 assert(b24_gpu_runtime_sync_model(&gpu,&original,0));
 assert(gpu.suit_rebinds==1);
 /* Kritically: 2010 model loader can free/realloc at the EXACT SAME address.
    Different armor identity MUST invalidate GPU texture and skinning buffers. */
 assert(b24_gpu_runtime_sync_model(&gpu,&original,1));
 assert(gpu.suit_rebinds==2&&prepares==2&&releases==1);
 assert(gpu.loaded_suit_index==1);
 verts[0].z=1.8f;
 assert(b24_gpu_runtime_sync_model(&gpu,&original,1));
 assert(gpu.stream.source.vertices[0].z==1.8f);
 assert(prepares==2);
 assert(b24_gpu_runtime_sync_model(&gpu,&original,2));
 assert(gpu.suit_rebinds==3&&prepares==3&&releases==2);
 b24_gpu_suit_release(&gpu.suit);
 b24_gpu_im2_stream_free(&gpu.stream);
 puts("PASS B24 five-suit GPU runtime: real IM2Model reload, same malloc/atlas pointer, explicit suit id forces rebind, anim frames still stream");
 return 0;
}
