#include "b24_unified.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

/* B24-C1 readable in-game pause labels, replacing B22's silent blank panel.
 * The HUD is a drawing layer, not a claim to have restored original iOS menus. */
static const unsigned char b24_font[26][5]={
 {0x7e,0x11,0x11,0x11,0x7e}, /* A */
 {0x7f,0x49,0x49,0x49,0x36}, /* B */
 {0x3e,0x41,0x41,0x41,0x22}, /* C */
 {0x7f,0x41,0x41,0x22,0x1c}, /* D */
 {0x7f,0x49,0x49,0x49,0x41}, /* E */
 {0x7f,0x09,0x09,0x09,0x01}, /* F */
 {0x3e,0x41,0x49,0x49,0x7a}, /* G */
 {0x7f,0x08,0x08,0x08,0x7f}, /* H */
 {0x41,0x41,0x7f,0x41,0x41}, /* I */
 {0x20,0x40,0x41,0x3f,0x01}, /* J */
 {0x7f,0x08,0x14,0x22,0x41}, /* K */
 {0x7f,0x40,0x40,0x40,0x40}, /* L */
 {0x7f,0x02,0x0c,0x02,0x7f}, /* M */
 {0x7f,0x04,0x08,0x10,0x7f}, /* N */
 {0x3e,0x41,0x41,0x41,0x3e}, /* O */
 {0x7f,0x09,0x09,0x09,0x06}, /* P */
 {0x3e,0x41,0x51,0x21,0x5e}, /* Q */
 {0x7f,0x09,0x19,0x29,0x46}, /* R */
 {0x46,0x49,0x49,0x49,0x31}, /* S */
 {0x01,0x01,0x7f,0x01,0x01}, /* T */
 {0x3f,0x40,0x40,0x40,0x3f}, /* U */
 {0x1f,0x20,0x40,0x20,0x1f}, /* V */
 {0x7f,0x20,0x18,0x20,0x7f}, /* W */
 {0x63,0x14,0x08,0x14,0x63}, /* X */
 {0x03,0x04,0x78,0x04,0x03}, /* Y */
 {0x61,0x51,0x49,0x45,0x43}  /* Z */
};
static void b24_label(uint32_t *px,int stride,int x,int y,
                      const char *text,uint32_t rgb,int scale){
    if(!px||!text||scale<1||scale>3)return;
    for(const unsigned char *c=(const unsigned char*)text;*c;c++,x+=6*scale){
        if(*c==' ')continue;
        if(*c<'A'||*c>'Z')continue;
        const unsigned char *font=b24_font[*c-'A'];
        for(int col=0;col<5;col++)for(int row=0;row<7;row++)
            if(font[col]&(1u<<row))
                for(int dy=0;dy<scale;dy++)for(int dx=0;dx<scale;dx++){
                    int sx=x+col*scale+dx,sy=y+row*scale+dy;
                    if(sx>=0&&sx<480&&sy>=0&&sy<272)px[(size_t)sy*stride+sx]=rgb;
                }
    }
}


static float lim(float x,float lo,float hi) {
    return !isfinite(x)?lo:(x<lo?lo:x>hi?hi:x);
}
static Im2Vec3 zup_to_yup(Im2Vec3 p){
    /* B17: Z vertical; B24 flight lab: Y vertical. Camera heading convention
       must be verified against game matrices before rendering full view. */
    return (Im2Vec3){p.x,p.z,p.y};
}
static Im2FlightStage stage_of(int s){
    return s==1?IM2_FLIGHT_HOVER:s==2?IM2_FLIGHT_CRUISE:
           s==3?IM2_FLIGHT_RUSH:IM2_FLIGHT_GROUND;
}
static B23Weapon weapon_of(int weapon){
    return weapon==1?B23_UNIBEAM:weapon==2?B23_MISSILE:
           weapon==3?B23_MELEE:B23_REPULSOR;
}
void b24_unified_init(B24Unified *g) {
    if(!g)return;
    memset(g,0,sizeof(*g));
    im2_controls_init(&g->controls);
    b23_init(&g->missile);
    im2_flight_defaults(&g->flight_cfg);
    im2_flight_init(&g->visual_root,(Im2Vec3){0.f,0.f,0.f});
    im2_camera_defaults(&g->camera_cfg);
    im2_camera_init(&g->camera_base);
    im2_camera_init(&g->camera_final);
    im2_speed_fx_init(&g->speed_fx);
    im2_melee_focus_init(&g->melee_focus);
    im2_thruster_init(&g->thruster);
    b19_init(&g->mission);
    g->last_stage=0;
    g->hud.mode=B22_HYBRID;
    g->hud.page=B22_GAME;
    g->hud.show_objective=1;
    g->hud.show_minimap=0; /* no original radar map or actual enemies loaded */
}
void b24_unified_set_sockets(B24Unified *g,
        const Im2ThrusterSocket six[IM2_THRUSTER_SOCKETS]) {
    if(!g)return;
    if(six)memcpy(g->sockets,six,sizeof(g->sockets));
    else memset(g->sockets,0,sizeof(g->sockets));
}
void b24_unified_tick(B24Unified *g,const B24Observation *obs) {
    if(!g||!obs)return;
    float dt=lim(obs->dt,0.f,.05f);
    /* B21 is THE input decoder: B17 external event code must not independently
       consume the same buttons after B24 integration. */
    im2_controls_tick(&g->controls,obs->buttons,obs->left_x,
                      obs->left_forward,obs->right_x,obs->right_y);
    g->hud.page=g->controls.state==IM2_PAUSED?B22_PAUSE:B22_GAME;
    if(g->controls.state==IM2_PAUSED){
        /* Real game world/timer/audio pause remains the caller's responsibility. */
        return;
    }
    Im2FlightStage stage=stage_of(obs->stage);
    Im2Vec3 player=zup_to_yup(obs->player_z_up);
    g->visual_root.position=player;
    g->visual_root.stage=stage;
    g->visual_root.heading_yaw_rad=lim(obs->heading_rad,-1000.f,1000.f);
    /* Follow the B17 existing movement, do not integrate a second trajectory.
       Root bank is a pose HINT until B7 animated model transform is hooked. */
    float bank=stage==IM2_FLIGHT_CRUISE?-.349066f*lim(obs->left_x,-1.f,1.f):
                stage==IM2_FLIGHT_RUSH?-.523599f*lim(obs->left_x,-1.f,1.f):0.f;
    float pitch=(stage==IM2_FLIGHT_CRUISE||stage==IM2_FLIGHT_RUSH)?
                  -lim(obs->pitch_rad,-.523599f,.523599f):0.f;
    float smooth=1.f-expf(-5.5f*dt);
    g->visual_root.visual_roll_rad+=(bank-g->visual_root.visual_roll_rad)*smooth;
    g->visual_root.visual_pitch_rad+=(pitch-g->visual_root.visual_pitch_rad)*smooth;
    g->visual_root.pose=stage==IM2_FLIGHT_RUSH?IM2_POSE_RUSH:
        stage==IM2_FLIGHT_CRUISE?IM2_POSE_FLY_F:
        stage==IM2_FLIGHT_HOVER?IM2_POSE_HOVER:IM2_POSE_GROUND;

    Im2CameraInput ci={0};
    ci.player_position=player;
    ci.flight_stage=stage;
    ci.character_heading_yaw_rad=obs->heading_rad;
    ci.camera_input_yaw_rad=obs->orbit_rad;
    ci.camera_input_pitch_rad=obs->pitch_rad;
    ci.manual_right_stick=fabsf(obs->right_x)+fabsf(obs->right_y)>.15f;
    ci.visual_suit_roll_rad=g->visual_root.visual_roll_rad;
    ci.delta_seconds=dt;
    im2_camera_step(&g->camera_base,&g->camera_cfg,&ci);

    Im2MeleeFocusInput mi={0};
    mi.stage=stage;
    mi.attack_active=obs->melee_anim_active!=0;
    mi.target_alive=obs->target_alive!=0;
    mi.target_visible=obs->target_visible!=0 && obs->target_world_valid!=0;
    mi.target_distance=obs->target_distance;
    mi.player_head=(Im2Vec3){player.x,player.y+g->camera_cfg.anchor_head_height,player.z};
    mi.target_center=zup_to_yup(obs->target_z_up);
    mi.manual_camera_input=ci.manual_right_stick;
    mi.delta_seconds=dt;
    im2_melee_focus_apply(&g->melee_focus,&mi,
                          &g->camera_base,&g->camera_final);

    int enter_rush=stage==IM2_FLIGHT_RUSH&&g->last_stage!=IM2_FLIGHT_RUSH;
    im2_speed_fx_step(&g->speed_fx,stage,enter_rush,dt);
    g->thruster_out=im2_thruster_step(&g->thruster,&g->visual_root,
                   stage,g->sockets,
                   obs->suit_index==2?IM2_PARTICLE_WM_AMBER:IM2_PARTICLE_IM_BLUE,dt);
    /* Strong source invariant: no back effects in Stage 1/2, even if
       original dummy bones remain present in suit skeleton. */
    if(stage!=IM2_FLIGHT_RUSH){
        g->thruster_out.enabled[IM2_BACK_L]=0;
        g->thruster_out.enabled[IM2_BACK_R]=0;
    }

    B23Target target={0};
    size_t candidates=0;
    if(obs->target_visible&&obs->target_alive&&obs->target_id>=0){
        target.id=obs->target_id;
        target.visible=1;target.alive=1;
        target.occluded=obs->target_occluded!=0;
        target.distance=lim(obs->target_distance,0.f,100000.f);
        /* Approximate cone ONLY for current B17 target demo. Real B19 enemy
           projection and wall occlusion must replace this before gameplay. */
        float delta_x=(float)obs->target_screen_x-278.f;
        float delta_y=(float)obs->target_screen_y-110.f;
        float dist2=delta_x*delta_x+delta_y*delta_y;
        target.aim_cos=lim(1.f-dist2/(200.f*200.f),-1.f,1.f);
        target.screen_x=obs->target_screen_x;
        target.screen_y=obs->target_screen_y;
        target.health_percent=obs->target_health_percent;
        candidates=1;
    }
    b23_tick(&g->missile,weapon_of(obs->weapon_index),
             (g->controls.held&IM2_BT_L)!=0,
             candidates?&target:NULL,candidates,dt);

    g->hud.suit=obs->suit_index==2?B22_WARMACHINE:B22_IRONMAN;
    g->hud.armor=obs->player_health_known?lim(obs->armor_percent,0.f,100.f):0.f;
    g->hud.shield=obs->player_health_known?lim(obs->shield_percent,0.f,100.f):0.f;
    g->hud.energy=lim(obs->energy_percent,0.f,100.f);
    g->hud.charge=lim(obs->energy_percent,0.f,100.f);
    g->hud.ammo=(int)lim(obs->ammo,0.f,100.f);
    g->hud.wave=obs->wave;
    g->hud.mission_success=obs->mission_won!=0;
    g->hud.target_x=obs->target_screen_x;
    g->hud.target_y=obs->target_screen_y;
    g->hud.target_hp=obs->target_health_percent;
    b23_prepare_b22_ui(&g->hud); /* suppress weapon-agnostic lock */
    /* Original B19 enemy mission cannot be invisibly simulated while B17
       still renders a sphere target. A genuine enemy scene adapter must opt in. */
    if(obs->real_enemies_loaded){
        b19_set_player_position(&g->mission,(B19Vec3){player.x,player.y,player.z});
        b19_tick(&g->mission,dt);
    }
    g->last_stage=(int)stage;
}
void b24_unified_draw_overlay(B24Unified *g,uint32_t *pixels,int stride) {
    if(!g||!pixels||stride<B22_W)return;
    if(g->controls.state==IM2_PLAYING)
        im2_speed_fx_draw(pixels,stride,&g->speed_fx,g->hud.suit==B22_WARMACHINE);
    b22_draw_hud(pixels,stride,&g->hud);
    if(g->hud.page==B22_PAUSE){
        b24_label(pixels,stride,169,69,"PAUSED",0x55dff8u,2);
        b24_label(pixels,stride,141,111,"START RESUME",0xe8bb5du,1);
        b24_label(pixels,stride,141,139,"CIRCLE RESUME",0xc8e5eeu,1);
        b24_label(pixels,stride,141,164,"CROSS OPTIONS",0xc8e5eeu,1);
        b24_label(pixels,stride,141,187,"BETA MENU",0x7cb2c5u,1);
    }
    b23_draw_missile_hud(pixels,stride,&g->missile,
                          g->hud.suit,g->hud.mode,g->hud.page);
}
float b24_unified_chase_distance(const B24Unified *g) {
    if(!g)return 3.15f;
    /* Existing B17 projection must consume this smooth DISTANCE, not
       swap to an unrelated Y-up view matrix mid-frame. */
    float chase=g->camera_base.shoulder_to_chase;
    float rush=g->camera_base.rush_amount;
    return g->camera_cfg.shoulder_distance+
           (g->camera_cfg.cruise_distance-g->camera_cfg.shoulder_distance)*chase+
           (g->camera_cfg.rush_distance-g->camera_cfg.cruise_distance)*rush;
}
int b24_unified_should_fire(const B24Unified *g){
    return g&&g->controls.state==IM2_PLAYING&&g->controls.fire;
}
int b24_unified_should_melee(const B24Unified *g){
    return g&&g->controls.state==IM2_PLAYING&&g->controls.melee;
}
int b24_unified_paused(const B24Unified *g){
    return g&&g->controls.state==IM2_PAUSED;
}
