#include "im2_flight.h"
#include "im2_camera.h"
#include "im2_thruster.h"
#include "im2_speed_fx.h"
#include "im2_melee_focus.h"
#include <stdio.h>
int main(void){
    Im2FlightState flight;Im2FlightConfig cfg;Im2CameraConfig cc;
    Im2CameraState camera,out;Im2ThrusterState ts;Im2SpeedFx speed;Im2MeleeFocusState melee;
    Im2ThrusterSocket sockets[6]={0};
    im2_flight_defaults(&cfg);im2_flight_init(&flight,(Im2Vec3){0,7,0});
    im2_camera_defaults(&cc);im2_camera_init(&camera);im2_thruster_init(&ts);
    im2_speed_fx_init(&speed);im2_melee_focus_init(&melee);
    for(int k=0;k<6;k++){
        sockets[k].valid=1;sockets[k].model_position=(Im2Vec3){k%2?-.25f:.25f,k<2?.10f:k<4?1.2f:1.7f,0.f};
        sockets[k].model_exhaust_direction=(Im2Vec3){0,k<2?-1.f:0.f,k<2?0.f:-1.f};
    }
    puts("seconds,stage,feet,hands,back,particles,rush_streaks,melee_blend,camera_fov_deg");
    for(int frame=0;frame<720;frame++){
        float t=(float)frame/60.f;
        Im2FlightInput f={0};f.airborne=t>=2.f&&t<10.f;f.delta_seconds=1.f/60.f;
        f.left_y=t<2.f?0.f:t<4.f?.4f:t<10.f?1.f:0.f;
        f.boost=t>=7.f&&t<9.f;
        im2_flight_step(&flight,&cfg,&f);
        Im2ThrusterOutput fx=im2_thruster_step(&ts,&flight,flight.stage,sockets,IM2_PARTICLE_IM_BLUE,f.delta_seconds);
        im2_speed_fx_step(&speed,flight.stage,fx.rush_entry,f.delta_seconds);
        Im2CameraInput ci={0};ci.player_position=flight.position;ci.flight_stage=flight.stage;
        ci.character_heading_yaw_rad=flight.heading_yaw_rad;ci.delta_seconds=f.delta_seconds;
        im2_camera_step(&camera,&cc,&ci);
        Im2MeleeFocusInput mi={0};mi.stage=flight.stage;mi.delta_seconds=f.delta_seconds;
        mi.attack_active=t>=10.4f;mi.target_alive=mi.target_visible=1;mi.target_distance=2.2f;
        mi.player_head=(Im2Vec3){flight.position.x,flight.position.y+1.6f,flight.position.z};
        mi.target_center=(Im2Vec3){flight.position.x,flight.position.y+1.2f,flight.position.z+2.2f};
        im2_melee_focus_apply(&melee,&mi,&camera,&out);
        if(frame%60==59){printf("%.0f,%d,%d,%d,%d,%d,%d,%.3f,%.2f\n",(float)(frame+1)/60.f,(int)flight.stage,
         fx.enabled[0]&&fx.enabled[1],fx.enabled[2]&&fx.enabled[3],fx.enabled[4]&&fx.enabled[5],
         fx.allowed_particle_count,(int)(speed.enabled?(8.f+12.f*speed.strength):0.f),
         melee.focus,out.fov_deg);}
    }
}
