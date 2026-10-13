#include "im2_flight.h"
#include <stdio.h>

int main(void) {
    Im2FlightConfig cfg; im2_flight_defaults(&cfg);
    Im2FlightState state; im2_flight_init(&state,(Im2Vec3){0.f,10.f,0.f});
    Im2FlightInput in={0}; in.airborne=1;in.delta_seconds=1.f/60.f;
    puts("seconds,stage,x,y,z,bank_degrees,pitch_degrees,pose,pose_blend");
    for(int frame=0;frame<60*12;frame++){
        float t=(float)frame/60.f;
        in.left_x=t>=4.f&&t<6.f?-.35f:(t>=8.f&&t<10.f?.35f:0.f);
        in.left_y=t<2.f?.50f:t<11.f?1.f:.40f;
        in.camera_pitch_rad=t>=2.f&&t<4.f?.30f:(t>=6.f&&t<8.f?-.30f:0.f);
        in.boost=t>=8.f&&t<10.f;
        im2_flight_step(&state,&cfg,&in);
        if(frame%60==59){
            printf("%.0f,%d,%.3f,%.3f,%.3f,%.2f,%.2f,%d,%.2f\n",
                   t+1.f,(int)state.stage,state.position.x,state.position.y,state.position.z,
                   state.visual_roll_rad*57.2957795f,state.visual_pitch_rad*57.2957795f,
                   (int)state.pose,state.pose_blend);
        }
    }
    return 0;
}
