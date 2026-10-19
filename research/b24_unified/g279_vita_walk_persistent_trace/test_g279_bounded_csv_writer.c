/* Host C11 test for the EXACT optional Vita file writer, NO original assets. */
#include "b24_g279_walk_trace.h"
#include <assert.h>
#include <string.h>
#include <math.h>

int main(void) {
 const char *path="g279_host_walk_test.csv";
 assert(!b24_g279_trace_open("/nonexistent_g279_118318/dev/null/file.csv"));
 assert(b24_g279_trace_open(path));
 assert(!b24_g279_trace_open(path)); /* No duplicate descriptor */
 B24G279Row boot={0};
 boot.phase="BOOT";boot.frame=1u;boot.millis=16u;
 boot.initial_x=0.f;boot.initial_y=0.f;boot.initial_z=0.f;
 boot.x=.012f;boot.y=.032f;boot.z=.0725f;
 boot.gpu_x=.012f;boot.gpu_y=.032f;boot.gpu_z=.0725f;
 boot.cam_x=1.5f;boot.cam_y=3.5f;boot.has_native_floor=1u;
 boot.native_floor_z=.0725f;
 assert(b24_g279_trace_write(&boot));
 boot.phase="bad,phase";
 assert(!b24_g279_trace_write(&boot)); /* No CSV injection */
 boot.phase="BOOT";
 boot.gpu_y=NAN;
 assert(!b24_g279_trace_write(&boot)); /* No poison nonfinite */
 boot.gpu_y=.032f;
 B24G279Row walk=boot;
 boot.verdict="BAD,CSV";
 assert(!b24_g279_trace_write(&boot)); /* verdict injection blocked */
 walk.phase="WALK120";walk.frame=120u;walk.millis=2000u;
 walk.b14_path=10.0702f;walk.accepted_path=10.0702f;
 walk.active_stick=120u;walk.coll_reject=0u;walk.root_mismatch=0u;
 walk.wall_reject=0u;walk.missing_floor=0u;walk.step_reject=0u;
 walk.net_world_dx=0.f;walk.net_world_dy=10.0702f;
 walk.net_camera_dx=0.f;walk.net_camera_dy=10.0691f;
 walk.verdict="WORLD_AND_CAMERA_POSITIONS_TRANSLATE_TOGETHER";
 walk.x=0.f;walk.y=10.0702f;walk.z=.0725f;
 walk.gpu_x=0.f;walk.gpu_y=10.0702f;walk.gpu_z=.0725f;
 assert(b24_g279_trace_write(&walk));
 b24_g279_trace_close();
 assert(!b24_g279_trace_write(&walk));
 FILE *f=fopen(path,"r");assert(f);
 char row[1024]={0};
 assert(fgets(row,sizeof(row),f));
 assert(strstr(row,"phase,frame,ms,initial_x,"));
 unsigned cols=1;
 for(const char *p=row;*p;p++) if(*p==',')cols++;
 assert(cols==31u);
 assert(fgets(row,sizeof(row),f));
 assert(strstr(row,"BOOT,1,16,") == row);
 unsigned bootcols=1;
 for(const char *p=row;*p;p++)if(*p==',')bootcols++;
 assert(bootcols==cols);
 assert(fgets(row,sizeof(row),f));
 assert(strstr(row,"WALK120,120,2000,") == row);
 assert(strstr(row,",10.07020,10.07020,"));
 assert(strstr(row,"WORLD_AND_CAMERA_POSITIONS_TRANSLATE_TOGETHER"));
 assert(strstr(row,",0.00000,10.07020,0.00000,10.06910,"));
 unsigned walkcols=1;
 for(const char *p=row;*p;p++)if(*p==',')walkcols++;
 assert(walkcols==cols);
 assert(!fgets(row,sizeof(row),f));
 assert(!fclose(f));
 assert(!remove(path));
 puts("G279 PASS optional Vita diagnostic csv: correct 31 columns, 3-frame boot and 120-frame walk layout, 120-input, original collision data, nonfinite/phase error rejection, no duplicate opener, NO VPK");
 return 0;
}
