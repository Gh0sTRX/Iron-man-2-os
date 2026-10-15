#include "b24_c1_2010_diffuse_bank.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t u32(const unsigned char *p){
 return (uint32_t)p[0]|(uint32_t)p[1]<<8|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static uint16_t u16(const unsigned char *p){return (uint16_t)((unsigned)p[0]|((unsigned)p[1]<<8));}
static int safe_char(unsigned char c){
 return (c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='.';
}
void b24_c1_2010_diffuse_bank_reset(B24C1OriginalDiffuseBank *b){
 if(b)memset(b,0,sizeof(*b));
}
int b24_c1_2010_diffuse_bank_lookup(const B24C1OriginalDiffuseBank *b,unsigned m){
 if(!b||!b->loaded||m>=B24_C1_2010_MATERIALS)return -1;
 const unsigned v=b->texture_for_material[m];
 return v==B24_C1_2010_NO_TEXTURE?-1:(int)v;
}
int b24_c1_2010_diffuse_bank_load(B24C1OriginalDiffuseBank *b,const char *path){
 if(!b||!path)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 B24C1OriginalDiffuseBank tmp={0};
 int ok=1;
 unsigned char header[20];
 if(fread(header,1,20,f)!=20)ok=0;
 unsigned len=0;
 if(ok){
  len=u32(header+16);
  tmp.atlas_count=u32(header+12);
  if(memcmp(header,"C1MT",4)!=0||u32(header+4)!=1u||
     u32(header+8)!=B24_C1_2010_MATERIALS||
     (tmp.atlas_count!=B24_C1_2010_LEGACY_ATLASES&&
      tmp.atlas_count!=B24_C1_2010_ATLASES)||
     len<tmp.atlas_count*3u||
     len>tmp.atlas_count*B24_C1_2010_NAME_MAX)ok=0;
 }
 if(ok){
  for(unsigned i=0;i<B24_C1_2010_MATERIALS;i++){
   unsigned char bb[2];
   if(fread(bb,1,2,f)!=2){ok=0;break;}
   unsigned v=u16(bb);
   if(v!=B24_C1_2010_NO_TEXTURE&&v>=tmp.atlas_count){ok=0;break;}
   tmp.texture_for_material[i]=(uint16_t)v;
   if(v!=B24_C1_2010_NO_TEXTURE)tmp.source_verified_count++;
  }
 }
 unsigned used=0;
 for(unsigned i=0;i<tmp.atlas_count&&ok;i++){
  int n=fgetc(f);
  if(n<8||(unsigned)n>=B24_C1_2010_NAME_MAX||(unsigned)n>len-used-1u){ok=0;break;}
  used++;
  if(fread(tmp.names[i],1,(size_t)n,f)!=(size_t)n){ok=0;break;}
  tmp.names[i][n]=0;used+=(unsigned)n;
  const char *s=tmp.names[i];
  size_t slen=strlen(s);
  if(slen!=(size_t)n||strcmp(s+slen-5u,".c1tx")!=0){ok=0;break;}
  for(int j=0;j<n;j++)if(!safe_char((unsigned char)s[j])){ok=0;break;}
  for(unsigned prev=0;prev<i;prev++)if(strcmp(s,tmp.names[prev])==0){ok=0;break;}
 }
 if(used!=len)ok=0;
 if(ok&&fgetc(f)!=EOF)ok=0;
 if(ferror(f))ok=0;
 fclose(f);
 if(!ok)return 0;
 tmp.loaded=1;
 *b=tmp;
 return 1;
}
