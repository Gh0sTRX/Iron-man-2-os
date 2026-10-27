#ifndef B24_GPU_CAMERA_H
#define B24_GPU_CAMERA_H
/* B17 world = X/Y ground, Z up. Column-major GL 4x4 matrices.
   Source-authoritative for future HUD aim/weapon ray and GPU scene,
   without turning the old separate B22 Y-up camera into a second world. */
typedef struct {float x,y,z;} B24GpuVec3;
typedef struct {
    B24GpuVec3 eye,target,world_up;
    float fov_y_degrees,aspect,near_z,far_z;
} B24GpuCamera;
typedef struct {float projection[16],view[16];} B24GpuCameraMatrices;
/* Framing ONLY: shift both camera eye and look-at target to the player's
   RIGHT so the real avatar renders left-of-center, while the HUD reticle
   remains at pixel (480,272). 0 = centered cruise/rush, 1 = shoulder view.
   Does not aim weapons, move simulation, or alter lens FOV. */
int b24_gpu_camera_apply_shoulder(B24GpuCamera *camera,
 float world_right_x,float world_right_y,float offset);
int b24_gpu_camera_matrices(const B24GpuCamera *camera,B24GpuCameraMatrices *out);
/* Project a world position to native Vita 960x544 pixel x,y (top-left origin)
   so HUD lock-on and visible 3D scene share one set of matrices. */
int b24_gpu_world_to_screen(const B24GpuCameraMatrices *mat,
    B24GpuVec3 pos,int width,int height,float *x,float *y,float *clip_z);
#endif
