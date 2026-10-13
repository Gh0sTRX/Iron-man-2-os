#include "b24_c1l1_map.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static void u32le(unsigned char *p,unsigned v){
 p[0]=v&255;p[1]=(v>>8)&255;p[2]=(v>>16)&255;p[3]=(v>>24)&255;
}
int main(int argc,char **argv){
 assert(sizeof(B24C1Triangle)==44);
 assert(argc==2);
 assert(b24_c1l1_count()==0);
 const B24C1Triangle *p=b24_c1l1_triangle(0);
 assert(p==NULL);
 assert(!b24_c1l1_load(NULL));
 assert(!b24_c1l1_load("/missing/not-real.im2map"));
 assert(b24_c1l1_load(argv[1]));
 assert(b24_c1l1_count()>21000u && b24_c1l1_count()<=22919u);
 assert(b24_c1l1_triangle(b24_c1l1_count())==NULL);
 unsigned categories[4]={0};
 for(size_t i=0;i<b24_c1l1_count();i++){
  const B24C1Triangle *q=b24_c1l1_triangle(i);assert(q);
  assert(q->category<4);categories[q->category]++;
 }
 for(unsigned i=0;i<4;i++)assert(categories[i]>0);
 size_t old=b24_c1l1_count();
 /* Corrupt input must be refused without destroying the current good scene. */
 FILE *f=fopen("/tmp/b24-broken-map","wb");assert(f);
 unsigned char head[16]={0};memcpy(head,"C1M1",4);
 u32le(head+4,1);u32le(head+8,30001);u32le(head+12,44);
 assert(fwrite(head,1,16,f)==16);fclose(f);
 assert(!b24_c1l1_load("/tmp/b24-broken-map"));
 assert(b24_c1l1_count()==old);
 b24_c1l1_unload();assert(b24_c1l1_count()==0);
 puts("PASS B24-C1 authentic original triangle map: 21k+ triangles, all 4 source categories, corrupted-file guards");
 return 0;
}
