/* Synthetic stepped supports and overhangs exercise a PORT collision invariant:
 * the accepted feet/body pose must pass the same wall predicate as the proposal.
 * These are not original scene geometry, spawn coordinates or iOS physics rules. */
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g156_exact_vertical_triangle_contact.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

static void make_face(B24C1OriginalCollisionFace *f,const float v[9],int wall){
 memset(f,0,sizeof(*f));memcpy(f->xyz,v,9*sizeof(float));f->wall=(unsigned char)wall;
 f->minx=f->maxx=v[0];f->miny=f->maxy=v[1];f->minz=f->maxz=v[2];
 for(unsigned i=1;i<3;i++){
  f->minx=fminf(f->minx,v[i*3]);f->maxx=fmaxf(f->maxx,v[i*3]);
  f->miny=fminf(f->miny,v[i*3+1]);f->maxy=fmaxf(f->maxy,v[i*3+1]);
  f->minz=fminf(f->minz,v[i*3+2]);f->maxz=fmaxf(f->maxz,v[i*3+2]);
 }
}
static int wall_hit(const B24C1OriginalCollision *world,float x,float y,float z){
 for(unsigned i=0;i<world->count;i++)if(world->faces[i].wall &&
    b24_g156_exact_vertical_triangle_contact(world->faces[i].xyz,x,y,z,.35f,2.24f))return 1;
 return 0;
}
static void step_case(float base,float delta,int obstructed,int diagonal){
 B24C1OriginalCollisionFace faces[3];
 const float old_floor[]={-10,-10,base,.05f,-10,base,.05f,10,base};
 const float new_floor[]={.05f,-10,base+delta,10,-10,base+delta,.05f,10,base+delta};
 const float wall_low=delta>0?base+2.3f:base-.2f;
 const float wall_high=delta>0?base+4.f:base-.05f;
 const float wall_x=obstructed?.2f:5.f;
 const float wall[]={wall_x,-10,wall_low,wall_x,10,wall_low,wall_x,0,wall_high};
 make_face(&faces[0],old_floor,0);make_face(&faces[1],new_floor,0);make_face(&faces[2],wall,1);
 B24C1OriginalCollision world={0};
 world.ready=1;world.count=3;world.wall_count=1;world.faces=faces;
 assert(!wall_hit(&world,0,0,base));
 const float to_y=diagonal?.1f:0.f;
 float x=0,y=0,z=base;
 assert(b24_g75_capsule_reconcile(&world,0,0,base,.1f,to_y,base,
                                1,.35f,2.24f,&x,&y,&z));
 if(wall_hit(&world,x,y,z))fprintf(stderr,
   "accepted penetrating pose: base=%.4f step=%.4f final=(%.4f,%.4f,%.4f)\n",base,delta,x,y,z);
 assert(!wall_hit(&world,x,y,z));
 if(obstructed){
  assert(fabsf(x)<.0001f && fabsf(z-base)<.0001f);
  assert(fabsf(y-to_y)<.0001f); /* blocked X still permits safe Y slide */
 }else{
  assert(fabsf(x-.1f)<.0001f && fabsf(y-to_y)<.0001f);
  assert(fabsf(z-(base+delta))<.0001f); /* original allowed step unchanged */
 }
}

static void original_geometry(const char *path){
 B24C1OriginalCollision city={0};assert(b24_g70_g68_collision_load(&city,path));
 assert(city.count==1910 && city.wall_count==1690 && city.faces[715].wall);
 const float dirs[][2]={{.05f,0},{-.05f,0},{0,.05f},{0,-.05f},{.2f,0},{-.2f,0},{0,.2f},{0,-.2f}};
 unsigned checked=0;
 for(unsigned i=0;i<city.count;i++){
  if(city.faces[i].wall)continue;
  const float *t=city.faces[i].xyz;
  float x=(t[0]+t[3]+t[6])/3,y=(t[1]+t[4]+t[7])/3,z=(t[2]+t[5]+t[8])/3;
  if(wall_hit(&city,x,y,z))continue; /* not a valid starting body pose */
  for(unsigned j=0;j<8;j++){
   float a=x,b=y,c=z;
   assert(b24_g75_capsule_reconcile(&city,x,y,z,x+dirs[j][0],y+dirs[j][1],z,
                                   1,.35f,2.24f,&a,&b,&c));
   assert(!wall_hit(&city,a,b,c));checked++;
  }
 }
 assert(checked>=1000);
 printf("PASS original G66C: %u checked endpoints from clear native floor centroids; no spawn/device claim\n",checked);
 b24_c1_original_collision_free(&city);
}
int main(int argc,char **argv){
 if(argc==2){original_geometry(argv[1]);return 0;}
 assert(argc==1);
 const float base[]={-40.f,0.f,40.f,200.f};
 for(unsigned i=0;i<4;i++)for(int obstructed=0;obstructed<=1;obstructed++)
  for(int diagonal=0;diagonal<=1;diagonal++){
   step_case(base[i],.4f,obstructed,diagonal);
   step_case(base[i],-.3f,obstructed,diagonal);
  }
 puts("PASS 32 synthetic ground-contact cases: step up/down, final body clearance, safe slide, shifted Z");
 return 0;
}
