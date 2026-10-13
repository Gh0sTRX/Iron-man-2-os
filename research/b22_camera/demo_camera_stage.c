#include "im2_camera.h"
#include <stdio.h>

int main(void){
    Im2FlightConfig fc; Im2CameraConfig cc;
    im2_flight_defaults(&fc); im2_camera_defaults(&cc);
    Im2FlightState flight; Im2CameraState camera;
    im2_flight_init(&flight,(Im2Vec3){0.f,10.f,0.f});
    im2_camera_init(&camera);
    puts("second,flight_stage,flight_y,flight_x,flight_z,bank_deg,camera_offset_x,camera_offset_y,camera_offset_z,fov_deg,shoulder_to_chase,rush_amount");
    for(int i=0;i<720;i++){
        float second=(float)i/60.f;
        Im2FlightInput f={0};
        f.airborne=1; f.delta_seconds=1.f/60.f;
        f.left_y=(second<2.f||second>=10.f)?0.5f:1.f;
        f.left_x=second>=5.f&&second<7.f?.30f:0.f;
        f.camera_pitch_rad=second>=2.f&&second<5.f?.25f:(second>=8.f&&second<10.f?-.18f:0.f);
        f.boost=second>=5.f&&second<8.f;
        im2_flight_step(&flight,&fc,&f);
        Im2CameraInput v={0};
        v.player_position=flight.position;v.flight_stage=flight.stage;
        v.character_heading_yaw_rad=flight.heading_yaw_rad;
        v.camera_input_yaw_rad=f.camera_yaw_rad;
        v.camera_input_pitch_rad=f.camera_pitch_rad;
        v.manual_right_stick=0;
        v.visual_suit_roll_rad=flight.visual_roll_rad;
        v.delta_seconds=f.delta_seconds;
        im2_camera_step(&camera,&cc,&v);
        if(i%60==59){
            printf("%.0f,%d,%.3f,%.3f,%.3f,%.2f,%.3f,%.3f,%.3f,%.2f,%.3f,%.3f\n",
                second+1.f,(int)flight.stage,flight.position.y,flight.position.x,flight.position.z,
                flight.visual_roll_rad*57.2957795f,
                camera.position.x-flight.position.x,
                camera.position.y-flight.position.y,
                camera.position.z-flight.position.z,
                camera.fov_deg,camera.shoulder_to_chase,camera.rush_amount);
        }
    }
    return 0;
}
