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
    h=update_once(h,
        'float target_z, speed, cooldown, beam_time;',
        'float target_z, speed, cooldown, beam_time;\n'
        ' float authored_move_vx, authored_move_vy; /* G75 homebrew velocity smoothing */',
        'B14 world velocity state')
    s=update_once(s,
        'const float velocity=(w->flying?(w->rush?4.0f:2.0f):(w->rush?2.2f:1.1f));',
        '''/* G75 exact 2010 movement speed still unknown. Gameplay candidate:
    B22's previous 15/29 source-independent design guides safe geometry pace;
    use conservative 8.5 / 16 airborne, 2.7 / 5.2 ground in original
    C1L1 world units, with stage-specific acceleration; no double movement. */
 const float speed_target=w->flying?(w->rush?16.0f:8.5f):
                                     (w->rush?5.2f:2.7f);
 const float smoothing=1.f-expf(-(w->flying?(w->rush?7.f:9.f):14.f)*dt);
 w->authored_move_vx+=(vx*speed_target-w->authored_move_vx)*smoothing;
 w->authored_move_vy+=(vy*speed_target-w->authored_move_vy)*smoothing;
 const float velocity=0.f; /* legacy scalar variable no longer governs XY */''',
        'stage flight ground pace and acceleration')
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
    # velocity is deliberately fixed to 0 to make old interpolation lines
    # easily recognized; no unused-variable compile warnings (const used by
    # optional old unrelated lines would be inert). Remove unused declaration
    # if only source constants no old references.
    if s.count('velocity')==1:
        s=s.replace(' const float velocity=0.f; /* legacy scalar variable no longer governs XY */','')
    # Keep XML / GitHub source modules isolated, write only after all validations.
    world.write_text(s)
    header.write_text(h)
    print('PASS G75 source-only B14 flight/camera candidate, original world coordinates and authored 2010 animations untouched')

if __name__=='__main__':
    q=argparse.ArgumentParser()
    q.add_argument('--b14-source-dir',required=True,type=Path)
    a=q.parse_args()
    calibrate(a.b14_source_dir)
