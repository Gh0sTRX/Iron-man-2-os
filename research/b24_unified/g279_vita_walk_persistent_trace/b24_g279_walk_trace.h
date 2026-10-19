/* G279: source-only optional PS Vita WALK evidence to ux0:data.
 * Observe the SAME rendered GPU frame already proven by G227/G229/G277/G278.
 * Not original 2010 mechanics. Never changes controls, collision, camera or actor.
 * Two first-boot / 120-render-ground-window diagnostic phases; NO VPK.
 * Uses C stdio with open failure as strictly NON-FATAL.
 */
#ifndef B24_G279_WALK_TRACE_H
#define B24_G279_WALK_TRACE_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
 const char *phase; /* only internal literal BOOT or WALK120 */
 unsigned frame, millis;
 float initial_x,initial_y,initial_z;
 float x,y,z,gpu_x,gpu_y,gpu_z,cam_x,cam_y,stick_x,stick_y;
 float b14_path,accepted_path,native_floor_z;
 unsigned active_stick,coll_reject,root_mismatch;
 unsigned wall_reject,missing_floor,step_reject,has_native_floor;
} B24G279Row;

/* This diagnostic is included ONCE in the real src/main.c translation unit. */
static FILE *b24_g279_trace_stream;
static void b24_g279_trace_close(void) {
 if(b24_g279_trace_stream) {
  (void)fflush(b24_g279_trace_stream);
  (void)fclose(b24_g279_trace_stream);
  b24_g279_trace_stream=NULL;
 }
}
static int b24_g279_trace_open(const char *path) {
 if(!path||!*path||b24_g279_trace_stream)return 0;
 FILE *f=fopen(path,"w");
 if(!f)return 0; /* Missing writable ux0:data must NEVER block boot. */
 b24_g279_trace_stream=f;
 if(fputs("phase,frame,ms,initial_x,initial_y,initial_z,world_x,world_y,world_z,"
          "gpu_x,gpu_y,gpu_z,camera_x,camera_y,stick_x,stick_y,"
          "b14_path,resolved_path,native_floor_z,active_stick,collision_reject,"
          "gpu_root_mismatch,wall_reject,missing_floor,step_reject,has_native_floor\n",f)<0 ||
    fflush(f)!=0) {
  b24_g279_trace_close();return 0;
 }
 (void)atexit(b24_g279_trace_close);
 return 1;
}
static int b24_g279_trace_write(const B24G279Row *r) {
 if(!r||!b24_g279_trace_stream)return 0;
 if(!r->phase || (strcmp(r->phase,"BOOT")!=0 &&
                  strcmp(r->phase,"WALK120")!=0))return 0;
 const float f[]={
  r->initial_x,r->initial_y,r->initial_z,
  r->x,r->y,r->z,r->gpu_x,r->gpu_y,r->gpu_z,
  r->cam_x,r->cam_y,r->stick_x,r->stick_y,
  r->b14_path,r->accepted_path,r->native_floor_z
 };
 for(unsigned i=0;i<sizeof(f)/sizeof(f[0]);++i)
  if(!isfinite(f[i]))return 0;
 int n=fprintf(b24_g279_trace_stream,
  "%s,%u,%u,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,"
  "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,"
  "%.5f,%.5f,%.5f,%u,%u,%u,%u,%u,%u,%u\n",
  r->phase,r->frame,r->millis,
  r->initial_x,r->initial_y,r->initial_z,
  r->x,r->y,r->z,r->gpu_x,r->gpu_y,r->gpu_z,
  r->cam_x,r->cam_y,r->stick_x,r->stick_y,
  r->b14_path,r->accepted_path,r->native_floor_z,
  r->active_stick,r->coll_reject,r->root_mismatch,
  r->wall_reject,r->missing_floor,r->step_reject,r->has_native_floor);
 if(n<0 || fflush(b24_g279_trace_stream)!=0) {
  b24_g279_trace_close();return 0;
 }
 return 1;
}
#endif
