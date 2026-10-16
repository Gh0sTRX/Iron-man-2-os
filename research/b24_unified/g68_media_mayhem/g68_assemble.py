#!/usr/bin/env python3
"""Make an isolated G68 candidate from exact latest G67 host/Vita C source.
Fail closed on any baseline source drift. Never overwrite the G67 build.
"""
from pathlib import Path
import argparse,shutil

def once(raw,old,new):
 if raw.count(old)!=1:raise ValueError('G67 source marker count changed: '+old[:110])
 return raw.replace(old,new,1)

def assemble(src,dst):
 dst.mkdir(parents=True,exist_ok=True)
 raw=(src/'main.c').read_text()
 raw=once(raw,'static SourceMesh city,armor;',
  'static SourceMesh city,armor;\n#include "g68_suitcase_runtime.h"\n#include "g68_mission.h"\nstatic G68Mission g68_mission;\n'
  'static float g68_motion_clock=0.f,g68_attack_until=0.f;\n'
  'static int g68_attack_clip=2,g68_current_clip=-1,g68_walking=0;')
 raw=once(raw,'free(m->v);m->v=NULL;',
           'if(m!=&armor){free(m->v);m->v=NULL;}')
 raw=once(raw,'player.health=100;player.show_help=1;',
  'player.health=100;player.show_help=1;\n'
  'g68_start(&g68_mission,player.pos.x,player.pos.y,player.pos.z);\n'
  'g68_attack_until=0;g68_motion_clock=0;g68_current_clip=-1;')
 raw=once(raw,'if(length>.13f){player.heading=atan2f(dx,dy);}',
          'g68_walking=length>.13f;\n'
          'if(length>.13f){player.heading=atan2f(dx,dy);}')
 raw=once(raw,'move_swept((Vec){dx*speed*dt,dy*speed*dt,dz*dt});',
  '''move_swept((Vec){dx*speed*dt,dy*speed*dt,dz*dt});
 g68_motion_clock+=dt;
 if(g68_attack_until>0.f)g68_attack_until=fmaxf(0.f,g68_attack_until-dt);
 const int melee=(pad->buttons&SCE_CTRL_LTRIGGER)!=0;
 const int fire=(pad->buttons&SCE_CTRL_SQUARE)!=0;
 if((melee||fire)&&!g68_mission.finished&&!g68_mission.lost){
  const float before=g68_mission.cooldown;
  (void)g68_shoot(&g68_mission,player.pos.x,player.pos.y,player.pos.z,
                  player.camera_heading,player.camera_pitch,melee);
  if(before<=0.f){g68_attack_until=melee?.48f:.28f;
                    g68_attack_clip=melee?5:2;}
 }
 g68_tick(&g68_mission,dt,player.pos.x,player.pos.y,player.pos.z,&player.health);''')
 raw=once(raw,'static float hudcoords[160];',
  '''/* Gameplay enemy render = honest wireframe diagnostic stand-ins.
 * No fake claims about original Drone_Army BRES/rig/original placement.
 * Core player/source city/skin and source floor collision remain original. */
static void g68_draw_enemy_markers(void){
 glDisable(GL_TEXTURE_2D);glColor4f(1.f,.37f,.16f,1.f);
 glEnableClientState(GL_VERTEX_ARRAY);
 for(int i=0;i<G68_ENEMY_MAX;i++){
  const G68Enemy *e=&g68_mission.bots[i];if(!e->alive)continue;
  const float x=e->x,y=e->y,z=e->z;
  const float lines[48]={
   x-1.f,y,z, x,y,z+1.2f,
   x,y,z+1.2f, x+1.f,y,z,
   x+1.f,y,z, x,y,z-1.2f,
   x,y,z-1.2f, x-1.f,y,z,
   x,y-1.f,z, x,y,z+1.2f,
   x,y,z+1.2f, x,y+1.f,z,
   x,y+1.f,z, x,y,z-1.2f,
   x,y,z-1.2f, x,y-1.f,z
  };
  glVertexPointer(3,GL_FLOAT,0,lines);
  glDrawArrays(GL_LINES,0,16);
 }
 glDisableClientState(GL_VERTEX_ARRAY);
}
static float hudcoords[160];''')
 raw=once(raw,'/* Health + flight meter line, compact, no bitmap HUD. */',
  '''/* Health + flight meter line, compact, no bitmap HUD. */
 /* First mission 2-wave progress HUD: five diamonds represented as ticks. */
 for(int k=0;k<5;k++){
  const float x=355.f+k*26.f;
  hud_line(&n,x,505.f,x+(k<g68_mission.knockouts?17.f:6.f),505.f);
 }
 if(g68_mission.finished){
  hud_line(&n,380,475,580,475);hud_line(&n,380,470,580,470);
 }
 if(g68_mission.lost){
  hud_line(&n,425,460,535,360);hud_line(&n,535,460,425,360);
 }''')
 raw=once(raw,'if(load_ok)render_mesh(&city);',
             'if(load_ok)render_mesh(&city);\n g68_draw_enemy_markers();')
 raw=once(raw,'/* Original Mark VI geometry and atlas; animation streams not ported yet. */',
  '''/* Authentic Suitcase Mark V mesh, original 2010 B13 skinned motion clips.
   * Motion-state priority is G68 prototype, NOT native Lua scene execution. */
  int clip=g68_attack_until>0.f?g68_attack_clip:
        (player.flying?((player.cruise)?4:3):(g68_walking?1:0));
  if(clip!=g68_current_clip){g68_motion_clock=0.f;g68_current_clip=clip;}
  g68_pose(&armor,clip,g68_motion_clock);''')
 raw=once(raw,'wall_ok=load_collision();',
             'wall_ok=load_collision();')
 raw=once(raw,'load_mesh(&armor,"app0:assets/G66_armor.g66m","G66_armor");',
  'load_mesh(&armor,"app0:assets/G66_armor.g66m","G66_armor");\n'
  'if(load_ok&&!g68_load_motion(armor.nv))load_ok=0;')
 (dst/'main.c').write_text(raw)
 shutil.copy2(src/'g67_collision.h',dst/'g67_collision.h')
 base=(src/'CMakeLists.txt').read_text()
 base=once(base,'project(IronMan2_B24_G67_Collision C)',
           'project(IronMan2_B24_G68_MarkV_MediaMayhem C)')
 base=once(base,'IM2G67001','IM2G68001')
 base=once(base,'IronMan2_B24_G67_Collision_Beta.vpk',
           'IronMan2_B24_G68_MarkV_Expo_Combat.vpk')
 base=once(base,'Iron Man 2 - B24 G67 Collision Beta',
           'Iron Man 2 - B24 G68 Mark V')
 (dst/'CMakeLists.txt').write_text(base)
 own=Path(__file__).resolve().parent
 shutil.copy2(own/'g68_mission.h',dst/'g68_mission.h')
 shutil.copy2(own/'g68_suitcase_runtime.h',dst/'g68_suitcase_runtime.h')
 assert 'g68_pose(&armor,clip,g68_motion_clock)' in raw
 assert 'G68Mission g68_mission' in raw
 print('G68 isolated G67 full scene, G59 physics, owner Mark V skinned combat candidate ready',dst)

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--src',type=Path,required=True)
 p.add_argument('--dst',type=Path,required=True)
 a=p.parse_args();assemble(a.src,a.dst)
