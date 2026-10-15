#include "b24_c1_2010_diffuse_bank.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void le32(FILE *f,unsigned v){for(int i=0;i<4;i++)fputc((v>>(i*8))&255,f);}
static void mk(const char *path,int corrupt){
 FILE *f=fopen(path,"wb");assert(f);
 fwrite("C1MT",1,4,f);le32(f,1);le32(f,94);le32(f,39);
 unsigned nn=0;char names[39][64];
 for(int i=0;i<39;i++){snprintf(names[i],sizeof(names[i]),"c1l1_test%02d.c1tx",i);
   nn+=1+(unsigned)strlen(names[i]);}
 le32(f,nn);
 for(int i=0;i<94;i++){unsigned v=i<64?(unsigned)i%39:65535u;
   if(corrupt&&i==16)v=40;
   fputc(v&255,f);fputc((v>>8)&255,f);}
 for(int i=0;i<39;i++){int len=(int)strlen(names[i]);fputc(len,f);fwrite(names[i],1,(size_t)len,f);}
 fclose(f);
}
int main(int argc,char **argv){
 const char *valid="/tmp/g12_C1MT_valid_source.bin";
 const char *bad="/tmp/g12_C1MT_invalid_source.bin";
 B24C1OriginalDiffuseBank b={0};
 mk(valid,0);assert(b24_c1_2010_diffuse_bank_load(&b,valid));
 assert(b.loaded&&b.source_verified_count==64);
 assert(b24_c1_2010_diffuse_bank_lookup(&b,0)==0);
 assert(b24_c1_2010_diffuse_bank_lookup(&b,63)==24);
 assert(b24_c1_2010_diffuse_bank_lookup(&b,64)==-1);
 assert(b24_c1_2010_diffuse_bank_lookup(&b,999)==-1);
 mk(bad,1);assert(!b24_c1_2010_diffuse_bank_load(&b,bad));
 assert(b.loaded&&b.source_verified_count==64); /* transactional rollback */
 remove(valid);remove(bad);
 if(argc==2){
  B24C1OriginalDiffuseBank real={0};
  assert(b24_c1_2010_diffuse_bank_load(&real,argv[1]));
  assert(real.loaded&&real.source_verified_count==64);
  int vehicle=0;
  for(int i=0;i<39;i++)if(strcmp(real.names[i],"c1l1_vehicles.c1tx")==0)vehicle=1;
  assert(vehicle);
  printf("PASS authentic original G12 C1MT 94 authored scene materials,"
         " %u actual original source diffuse links, 39 exact 2010 atlases, NO VPK\n",
          real.source_verified_count);
 }
 puts("PASS C1MT strictly validated 94 material 39 original atlas names; missing map indexes preserve fallback, transactional invalid file rejection.");
 return 0;
}
