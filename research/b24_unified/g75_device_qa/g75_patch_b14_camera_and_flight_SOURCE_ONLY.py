#!/usr/bin/env python3
"""G75 source-only, opt-in rebuild of homebrew B14 movement/camera pacing.
Does NOT infer source 2010 engine movement speed from in-place 2010 .anim.
Works on extracted B14 files or on a pre-built G9 work/src tree.
No VPK produced. Fail-closed if source strings drift.
"""
import argparse
from pathlib import Path

def update_once(s,old,new,name):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"G75 {name}: expected one original source anchor, got {n}: {old[:95]!r}")
    return s.replace(old,new,1)

def calibrate(directory:Path):
    world=directory/'b14_world.c'
    header=directory/'b14_world.h'
    if not world.is_file() or not header.is_file():
        raise FileNotFoundError('G75 requires authored B14 world.c and .h in same directory')
    s=world.read_text()
    h=header.read_text()
    if 'G75_SOURCE_ONLY_CALIBRATION' in s or 'G75_SOURCE_ONLY_CALIBRATION' in h:
        raise RuntimeError('G75 already applied; do not stack physics')
    s=update_once(s,
        'w->pitch=cl(w->pitch+cl(looky,-1,1)*.95f*dt,-.12f,.43f);',
        '/* G75_SOURCE_ONLY_CALIBRATION: widen right-stick to -52.7/+60 degrees. */\n'
        'w->pitch=cl(w->pitch+cl(looky,-1,1)*1.65f*dt,-.92f,1.05f);',
        'camera pitch limits')
    # B14 source as shipped in original overlay has a compact struct,
    # but B17/B24 dynamically extend it before G9 gameplay. Insert at
    # the typedef end rather than matching fragile internal field order.
    h=update_once(h,
        '} B14World;',
        ' float authored_move_vx, authored_move_vy; /* G75 one B14 owner */\n'
        '} B14World;',
        'B17/G9 assembled world velocity state')
    # Actual 2026-10-16 G73 merges DIFFER from old B14 v1 physics.
    # Runtime-recovered main loop uses stages (hover 1.15, cruise 2.6,
    # rush 5.0); never overwrite it with the simpler original B14
    # w->rush branch and silently discard stage1/stage2 differences.
    velocity_variants=[
       ('const float velocity=w->flying?(w->flight_stage==3?5.0f:(w->flight_stage==2?2.6f:1.15f)):(len>=.96f?2.4f:1.1f);',
        'const float speed_target=w->flying?(w->flight_stage==3?24.f:(w->flight_stage==2?12.f:4.2f)):(len>=.96f?5.2f:2.7f);'),
       ('const float velocity=(w->flying?(w->rush?4.0f:2.0f):(w->rush?2.2f:1.1f));',
        'const float speed_target=w->flying?(w->rush?24.f:12.f):(w->rush?5.2f:2.7f);')
    ]
    found=[(a,b) for a,b in velocity_variants if a in s]
    if len(found)!=1:raise RuntimeError('G75 merged B14 flight controller speed branch changed; inspect actual source')
    old,new=found[0]
    s=update_once(s,old,'''/* G75 proposed iOS-feel flight pace, not decoded Gameloft C++.
       Keep authentic merged stage1 HOVER stage2 CRUISE stage3 RUSH.
       Existing B14 CPU main loop remains sole integrator. */
 '''+new+'''
 const float smoothing=1.f-expf(-(w->flying?(w->flight_stage==3?7.f:9.f):14.f)*dt);
 w->authored_move_vx+=(vx*speed_target-w->authored_move_vx)*smoothing;
 w->authored_move_vy+=(vy*speed_target-w->authored_move_vy)*smoothing;
'''.replace('w->flight_stage==3?7.f:9.f','w->rush?7.f:9.f' if old==velocity_variants[1][0] else 'w->flight_stage==3?7.f:9.f'),
         'merged G9 stage-specific ground hover normal RUSH velocity calibration')
    # B14 G8 expanded native source map clamp, or original tiny stand-alone B14.
    variants=[
        ('w->x=cl(w->x+vx*velocity*dt,-324.f,330.f);',
         'w->x=cl(w->x+w->authored_move_vx*dt,-324.f,330.f);'),
        ('w->x=cl(w->x+vx*velocity*dt,-270.f,273.f);',
         'w->x=cl(w->x+w->authored_move_vx*dt,-270.f,273.f);'),
        ('w->x=cl(w->x+vx*velocity*dt,-20,20);',
         'w->x=cl(w->x+w->authored_move_vx*dt,-20,20);'),
    ]
    old=[(a,b) for a,b in variants if a in s]
    if len(old)!=1:raise RuntimeError('G75 cannot find unique G8 B14 X travel line')
    s=update_once(s,*old[0],name='B14 world X travel')
    variants_y=[
        ('w->y=cl(w->y+vy*velocity*dt,-351.f,254.f);',
         'w->y=cl(w->y+w->authored_move_vy*dt,-351.f,254.f);'),
        ('w->y=cl(w->y+vy*velocity*dt,-297.f,191.f);',
         'w->y=cl(w->y+w->authored_move_vy*dt,-297.f,191.f);'),
        ('w->y=cl(w->y+vy*velocity*dt,-20,20);',
         'w->y=cl(w->y+w->authored_move_vy*dt,-20,20);'),
    ]
    old=[(a,b) for a,b in variants_y if a in s]
    if len(old)!=1:raise RuntimeError('G75 cannot find unique G8 B14 Y travel line')
    s=update_once(s,*old[0],name='B14 world Y travel')
    # Original B14 altitude rate 1.6 and interpolation 2.5 units/s led to
    # slow takeoff / falling into roofs, independent of rendered flight pose.
    s=update_once(s,
        'vertical*1.6f*dt',
        'vertical*6.0f*dt',
        'source flight vertical rise/descent')
    s=update_once(s,
        'w->z+=cl(w->target_z-w->z,-2.5f*dt,2.5f*dt);',
        'w->z+=cl(w->target_z-w->z,-7.f*dt,7.f*dt);',
        'vertical acceleration cap')
    # Keep XML / GitHub source modules isolated, write only after all validations.
    world.write_text(s)
    header.write_text(h)
    print('PASS G75 source-only B14 flight/camera candidate, original world coordinates and authored 2010 animations untouched')

if __name__=='__main__':
    q=argparse.ArgumentParser()
    q.add_argument('--b14-source-dir',required=True,type=Path)
    a=q.parse_args()
    calibrate(a.b14_source_dir)
