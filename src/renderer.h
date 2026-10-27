#ifndef IM2_RENDERER_H
#define IM2_RENDERER_H
#include <stdint.h>
#define IM2_W 480
#define IM2_H 272
#define IM2_MAXV 16000
#define IM2_MAXT 24000
typedef struct {float x,y,z,u,v;} IM2Vertex;
typedef struct {uint16_t i0,i1,i2;} IM2Triangle;
typedef struct {
    IM2Vertex *vertices;
    IM2Triangle *triangles;
    unsigned char *texture;
    uint32_t nv, nt, tw, th;
    float center_z;
    float native_bind_min_z; /* 2010 authored IM2T source rest minimum, stable during G8 motion */
} IM2Model;
typedef struct {
    float yaw, pitch, zoom;
    int wireframe;
    /* V4 experimental gameplay prototype (not original Iron Man 2 game engine). */
    float move_x, move_y, altitude, hover_bob, fps;
    int flying;
    float raster_ms, display_ms;  /* Retained for B9 compatibility */
    float motion_ms, upload_ms, copy_ms, present_ms;
    int vsync_requested, vsync_active, profile_error;
    /* B14 follow-camera world transform and arcade 3D target overlay. */
    int third_person,target_visible,hits,shots,completed,waves,flight_stage,invert_x,invert_y;
    float player_x,player_y,player_z,player_heading;
    float orbit,cam_x,cam_y,cam_z,camera_distance;
    float aim_x,aim_y,target_screen_x,target_screen_y,target_radius,beam_time;
    int b16_active,weapon_mode,emitter_vertex,combo_step,missile_active;
    float energy,missile_x,missile_y,missile_z;

} IM2Camera;
int im2_load(IM2Model *dst, const char *path);
void im2_free(IM2Model *model);
void im2_render(uint32_t *pixels, float *zbuffer,
                const IM2Model *model, const IM2Camera *camera,
                const char *model_name, unsigned frame_number);
#endif
