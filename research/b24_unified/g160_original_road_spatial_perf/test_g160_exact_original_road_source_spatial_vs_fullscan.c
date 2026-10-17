#include "b24_g159_real_source_road.h"
#include "b24_g160_original_road_spatial.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>

/* This is not a synthetic box/mock. G66M is the original 2010 scene
 * artifact; G159 owns actual c1l1_road atlas12=753 source triangles.
 * Turn off the index IN MEMORY in a shallow borrowed read-only struct
 * to compare EXACT same C floor query to the old linear scan, every
 * support value and every no-hit across representative full XY/Z.
 */
static uint64_t comparisons=0;
static void check_at(B24G159Road *fast,const B24G159Road *slow,
                     float x,float y,float z){
 float a=-777.25f,b=-777.25f;
 const int ra=b24_g159_road_near(fast,x,y,z,&a);
 const int rb=b24_g159_road_near(slow,x,y,z,&b);
 assert(ra==rb);
 if(ra)assert(fabsf(a-b)<.00001f);
 else assert(a==-777.25f&&b==-777.25f);
 comparisons++;
}
static void check_cross(B24G159Road *fast,const B24G159Road *slow,
                        float x,float y,float high,float low){
 float a=-321.25f,b=-321.25f;
 const int ra=b24_g159_road_crossed(fast,x,y,high,low,&a);
 const int rb=b24_g159_road_crossed(slow,x,y,high,low,&b);
 assert(ra==rb);
 if(ra)assert(fabsf(a-b)<.00001f);
 else assert(a==-321.25f&&b==-321.25f);
 comparisons++;
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 B24G159Road fast={0};
 assert(b24_g159_road_open(&fast,argv[1]));
 assert(fast.count==753u);
 assert(fast.spatial_index_ready==1u);
 assert(fast.cell_cols>1&&fast.cell_rows>1);
 assert(fast.cell_ref_count>0u&&fast.cell_ref_count<=500000u);
 assert(fast.cell_offsets!=NULL&&fast.cell_face_ids!=NULL);
 /* Copy shares the owned faces/index allocations but NEVER free slow.
  * Changing ONLY the selected code path is a direct old/new oracle. */
 B24G159Road slow=fast;
 slow.spatial_index_ready=0u;
 uint64_t total_fast=0u,total_baseline=0u;
 const float zs[]={.0725f,2.6937f,2.82955f,6.67306f,30.f};
 for(int y=-160;y<=160;y+=4){
  for(int x=-160;x<=160;x+=4){
   uint32_t begin=0,end=0;
   const int lookup=b24_g160_index_query(&fast,(float)x,(float)y,
                                         &begin,&end);
   if(lookup){
    assert(end>=begin&&end<=fast.cell_ref_count);
    total_fast+=(uint64_t)(end-begin);
   }
   total_baseline+=(uint64_t)fast.count;
   for(unsigned z=0;z<sizeof(zs)/sizeof(zs[0]);z++)
    check_at(&fast,&slow,(float)x,(float)y,zs[z]);
   check_cross(&fast,&slow,(float)x,(float)y,4.f,2.f);
   check_cross(&fast,&slow,(float)x,(float)y,2.5f,1.f);
   check_cross(&fast,&slow,(float)x,(float)y,20.f,19.f);
   check_cross(&fast,&slow,(float)x,(float)y,0.f,-1.f);
  }
 }
 /* Source-triangle centroids detect bad index cells even far beyond
  * central Stark Expo ROI, plus source face AABB epsilon boundaries. */
 for(uint32_t k=0;k<fast.count;k++){
  const B24G159RoadFace *f=&fast.faces[k];
  const float x=(f->p[0]+f->p[3]+f->p[6])/3.f;
  const float y=(f->p[1]+f->p[4]+f->p[7])/3.f;
  const float z=(f->p[2]+f->p[5]+f->p[8])/3.f;
  check_at(&fast,&slow,x,y,z);
  check_cross(&fast,&slow,x,y,z+.4f,z-.4f);
  check_at(&fast,&slow,f->minx-.00008f,y,z);
  check_at(&fast,&slow,f->maxx+.00008f,y,z);
 }
 check_at(&fast,&slow,-160.f,-160.f,2.6937f);
 check_at(&fast,&slow,10000.f,10000.f,2.6937f);
 check_cross(&fast,&slow,-160.f,-160.f,4.f,2.2f);
 check_cross(&fast,&slow,-160.f,-160.f,2.5f,1.f);
 assert(comparisons>=59000u);
 assert(total_fast<total_baseline/2u);
 const double reduction=100.0*(1.0-(double)total_fast/
                                      (double)total_baseline);
 printf("G160 original C1L1 source road 753 tris, CSR %ux%u cells, "
        "%u real source face refs; 6561 XY x 5 foot Z + 4 vertical sweeps; "
        "%llu old-vs-indexed output exact parity queries.\n",
        fast.cell_cols,fast.cell_rows,fast.cell_ref_count,
        (unsigned long long)comparisons);
 printf("G160 source candidate count: legacy %llu vs indexed %llu, "
        "%.2f percent fewer candidate faces in grid sample (NOT Vita FPS)\n",
        (unsigned long long)total_baseline,
        (unsigned long long)total_fast,reduction);
 b24_g159_road_close(&fast);
 assert(!fast.ready&&!fast.faces&&!fast.cell_offsets);
 puts("G160 PASS actual owner 2010 road source CRC-through-loader, "
      "native old-vs-CSR collision returned identical output, "
      "never extra floors, never excluded authentic triangle. NO VPK.");
 return 0;
}
