#include "b24_c1l1_map.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define C1L1_TRI_LIMIT 30000u
static B24C1Triangle *s_mesh = NULL;
static size_t s_count = 0;

static unsigned u32_le(const unsigned char *p) {
    return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);
}
void b24_c1l1_unload(void) {
    free(s_mesh);s_mesh=NULL;s_count=0;
}
int b24_c1l1_load(const char *path) {
    if(!path)return 0;
    /* Vita uses explicit app0: asset URLs (as do the original .im2t loaders).
       Never rely on SDL's process current-working-directory for bundled maps. */
    FILE *f=NULL;
#ifdef __vita__
    if(strncmp(path,"app0:",5)==0)f=fopen(path,"rb");
    else {
        char resolved[256];
        if(snprintf(resolved,sizeof(resolved),"app0:%s",path)<(int)sizeof(resolved))
            f=fopen(resolved,"rb");
    }
#else
    f=fopen(path,"rb");
#endif
    if(!f)return 0;
    unsigned char header[16]={0};
    int ok=fread(header,1,sizeof(header),f)==sizeof(header);
    if(ok)ok=memcmp(header,"C1M1",4)==0 &&
        u32_le(header+4)==1u &&
        u32_le(header+12)==sizeof(B24C1Triangle);
    unsigned count=ok?u32_le(header+8):0u;
    if(!count || count>C1L1_TRI_LIMIT)ok=0;
    if(ok && fseek(f,0,SEEK_END)!=0)ok=0;
    long size=ok?ftell(f):-1;
    if(size<0 || (unsigned long)size!=16ul+(unsigned long)count*sizeof(B24C1Triangle))ok=0;
    if(ok && fseek(f,16,SEEK_SET)!=0)ok=0;
    B24C1Triangle *next=ok?(B24C1Triangle*)malloc((size_t)count*sizeof(*next)):NULL;
    if(ok&&!next)ok=0;
    if(ok && fread(next,sizeof(*next),count,f)!=count)ok=0;
    fclose(f);
    if(ok) {
        for(unsigned i=0;i<count;i++){
            if(next[i].category>3u || (next[i].rgb&0xff000000u)) {ok=0;break;}
            for(unsigned j=0;j<9;j++)if(!isfinite(next[i].p[j]) ||
                fabsf(next[i].p[j])>10000.f) {ok=0;break;}
            if(!ok)break;
        }
    }
    if(!ok){free(next);return 0;}
    b24_c1l1_unload();
    s_mesh=next;s_count=count;return 1;
}
size_t b24_c1l1_count(void){return s_count;}
const B24C1Triangle *b24_c1l1_triangle(size_t index) {
    return index<s_count?&s_mesh[index]:NULL;
}
