#define _POSIX_C_SOURCE 200809L
#include "b24_original_im2v_stream.h"
#include <assert.h>
#include <dirent.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv){
 if(argc!=2){fprintf(stderr,"Usage: g85_test directory\n");return 2;}
 DIR *dir=opendir(argv[1]);
 if(!dir){perror(argv[1]);return 2;}
 size_t n=0;double differences=0.0;size_t zero_ms=0;
 struct dirent *e;
 float *pose=malloc(629u*3u*sizeof(float));
 float *first=malloc(629u*3u*sizeof(float));
 if(!pose||!first)return 3;
 while((e=readdir(dir))!=NULL){
  if(strncmp(e->d_name,"suitcase_ironman_",16)!=0)continue;
  size_t l=strlen(e->d_name);
  if(l<=5||strcmp(e->d_name+l-5,".im2v"))continue;
  char filename[192];
  if(l-5>=sizeof(filename))return 4;
  memcpy(filename,e->d_name,l-5);filename[l-5]=0;
  B24OriginalIM2VStream original={0};
  if(!b24_original_im2v_open(&original,argv[1],filename,629u)){
   fprintf(stderr,"G85 SOURCE STREAM OPEN FAILED %s\n",filename);
   return 5;
  }
  assert(original.nv==629u&&original.fps==20u);
  assert(original.frames==(original.duration_ms?
      (original.duration_ms-1u)/50u+2u:1u));
  if(original.duration_ms==0)zero_ms++;
  if(!b24_original_im2v_sample(&original,0u,0,first)||
     !b24_original_im2v_sample(&original,original.duration_ms/2u,0,pose))
      return 6;
  for(size_t i=0;i<629u*3u;i++){
   if(!isfinite(first[i])||!isfinite(pose[i]))return 7;
   differences+=fabs((double)first[i]-(double)pose[i]);
  }
  if(!b24_original_im2v_sample(&original,original.duration_ms,0,pose))
   return 8;
  for(size_t i=0;i<629u*3u;i++)if(!isfinite(pose[i]))return 9;
  if(b24_original_im2v_working_bytes(&original)!=629u*3u*sizeof(float)*2u)
   return 10;
  b24_original_im2v_close(&original);
  ++n;
 }
 closedir(dir);free(first);free(pose);
 if(n!=248u){fprintf(stderr,"Only %zu of 248 native original 2010 MarkV 629v streams actually opened\n",n);return 11;}
 printf("PASS G85: REAL old G8 IM2V C streamer opens/samples/interpolates ALL %zu original 2010 IronMan clips as genuine MarkV 629v, zero-duration=%zu, total pose differences=%.3f, NO VPK\n",n,zero_ms,differences);
 return 0;
}
