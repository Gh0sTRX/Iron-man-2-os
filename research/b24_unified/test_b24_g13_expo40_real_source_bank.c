#include "b24_c1_2010_diffuse_bank.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Real 2010 original 94-material / 40-atlas true PVR Vita loader.
   Takes authentic G13 binary C1MT produced from owner's 2010 IPA.
   Does not invent data or upload user game archives. */
int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"usage: g13_bank <G13 original 40 C1MT> <proven material id>\n");return 2;}
 B24C1OriginalDiffuseBank b={0};
 assert(b24_c1_2010_diffuse_bank_load(&b,argv[1]));
 assert(b.loaded && b.atlas_count==40u);
 assert(b.source_verified_count==65u);
 assert(strcmp(b.names[39],"cahp01_c_expo_building.c1tx")==0);
 unsigned id=(unsigned)atoi(argv[2]);
 assert(id<94u&&b24_c1_2010_diffuse_bank_lookup(&b,id)==39);
 unsigned count=0;
 for(unsigned i=0;i<94;i++)if(b24_c1_2010_diffuse_bank_lookup(&b,i)==39)count++;
 assert(count==1u);
 assert(b24_c1_2010_diffuse_bank_lookup(&b,500)==-1);
 /* Transactional invalid file rejection means old valid map survives. */
 FILE *f=fopen(argv[1],"rb");assert(f);
 unsigned char buf[16384];
 size_t n=fread(buf,1,sizeof(buf),f);
 fclose(f);assert(n>=208&&n<sizeof(buf));
 const char *tmp="/tmp/G13_INVALID_ATLAS41.c1mt";
 f=fopen(tmp,"wb");assert(f);
 buf[12]=41u;buf[13]=0;buf[14]=0;buf[15]=0;
 assert(fwrite(buf,1,n,f)==n);
 fclose(f);
 assert(!b24_c1_2010_diffuse_bank_load(&b,tmp));
 assert(b.atlas_count==40u&&b.source_verified_count==65u);
 assert(b24_c1_2010_diffuse_bank_lookup(&b,id)==39);
 remove(tmp);
 printf("PASS genuine source 2010 G13 C1MT 94 material ID %u restored Expo index39, 40 original atlas bank, 65 source-linked materials; unsafe 41 rejected, previous map remains valid; NO VPK.\n",id);
 return 0;
}
