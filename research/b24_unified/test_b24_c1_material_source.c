#include "b24_c1_material_source.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static void put(const char *path,const unsigned char *data,size_t count){
 FILE *f=fopen(path,"wb");assert(f);
 assert(fwrite(data,1,count,f)==count);
 assert(fclose(f)==0);
}
int main(int argc,char **argv){
 assert(argc==2);
 B24C1MaterialSource scene={0};
 assert(b24_c1_material_source_load(&scene,argv[1]));
 assert(scene.loaded&&scene.nmaterials==94u);
 assert(scene.meshes[0].group==0u);
 assert(scene.meshes[15].group==0u);
 assert(scene.meshes[16].group==1u);
 assert(scene.meshes[136].group==1u);
 assert(scene.meshes[137].group==2u);
 assert(scene.meshes[158].group==2u);
 assert(scene.meshes[159].group==3u);
 assert(scene.meshes[369].group==3u);
 assert(scene.meshes[369].first_triangle+
         scene.meshes[369].triangle_count==22919u);
 uint32_t counts[4]={0},tris[4]={0};
 for(unsigned k=0;k<B24_C1_MAT_NMESH;k++){
  const B24C1MatMesh *m=&scene.meshes[k];
  counts[m->group]++;tris[m->group]+=m->triangle_count;
 }
 assert(counts[0]==16&&counts[1]==121&&counts[2]==22&&counts[3]==211);
 assert(tris[0]==3280&&tris[1]==11141&&tris[2]==5116&&tris[3]==3382);
 for(unsigned i=0;i<B24_C1_MAT_NTRI;i++){
  const char *name=b24_c1_material_label(&scene,scene.triangle_material[i]);
  assert(name&&strstr(name,".bdae:"));
 }
 assert(!b24_c1_material_label(&scene,65535u));
 FILE *f=fopen(argv[1],"rb");assert(f);
 assert(fseek(f,0,SEEK_END)==0);long n=ftell(f);assert(n>55000&&n<100000);
 assert(fseek(f,0,SEEK_SET)==0);
 unsigned char *buf=malloc((size_t)n),*mut=malloc((size_t)n);assert(buf&&mut);
 assert(fread(buf,1,(size_t)n,f)==(size_t)n);fclose(f);
 char *output=malloc(strlen(argv[1])+16u);assert(output);
 strcpy(output,argv[1]);strcat(output,".corrupt");
 for(int c=0;c<7;c++){
  memcpy(mut,buf,(size_t)n);
  if(c==0)mut[0]='Q'; /* wrong magic */
  if(c==1)mut[20]=93; /* wrong material dictionary length */
  if(c==2)mut[28]=5; /* invalid scene group */
  if(c==3)mut[28+4]=10; /* first vertex must start at zero */
  if(c==4){mut[28+370*20]=255;mut[28+370*20+1]=255;} /* invalid material */
  if(c==5){mut[28+370*20+22919*2]=0;mut[28+370*20+22919*2+1]=0;} /* zero label */
  size_t size=c==6?(size_t)n-1u:(size_t)n;
  put(output,mut,size);
  assert(!b24_c1_material_source_load(&scene,output));
  assert(scene.loaded&&scene.nmaterials==94u); /* transactional parse */
 }
 assert(remove(output)==0);
 free(output);free(buf);free(mut);
 b24_c1_material_source_free(&scene);
 assert(!scene.loaded&&!scene.triangle_material&&!scene.labels);
 puts("PASS original B24 C1MA: 370 source meshes, 22919 original triangle material IDs, 94 file-qualified material identities, 7 corruption guards, no atlas guesses");
 return 0;
}
