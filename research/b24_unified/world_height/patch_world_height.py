#!/usr/bin/env python3
"""Fix B14's prototype altitude frame, after the full G171 reconstruction.

Uses existing port pacing, not decoded original Gameloft flight constants.
Does not select a story spawn, change source geometry, or create a VPK.
"""
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"World-height source drift: {old[:100]!r}")
    return source.replace(old, new, 1)


def patch(work):
    paths = {name: work / name for name in (
        'src/main.c', 'src/b14_world.c', 'src/b14_world.h',
        'b24/b24_unified/b24_g75_source_capsule.c',
        'b24/b24_unified/b24_g75_source_capsule.h')}
    text = {name: path.read_text() for name, path in paths.items()}
    if any('B14_WORLD_HEIGHT_SUPPORT' in s for s in text.values()):
        raise ValueError('World-height patch already present; refusing to stack it')
    main = text['src/main.c']
    world = text['src/b14_world.c']
    header = text['src/b14_world.h']
    capsule = text['b24/b24_unified/b24_g75_source_capsule.c']
    ch = text['b24/b24_unified/b24_g75_source_capsule.h']
    header = once(header, '} B14World;', ''' /* B14_WORLD_HEIGHT_SUPPORT: accepted support and fixed takeoff datum.
  * No second integrator; no inferred original mission spawn/flight rules. */
 float ground_z, flight_base_z;
 int ground_supported;
} B14World;''')
    header = once(header, '#endif', '''#define B14_WORLD_HEIGHT_SUPPORT 1
void b14_world_toggle_flight(B14World *w);
void b14_world_accept_ground_support(B14World *w,int found,float support_z);
#endif''')
    world = once(world,
        'w->target_z=cl(w->target_z+vertical*6.0f*dt,.35f,36.f);',
        '''
#ifdef B24_G75_SOURCE_CAPSULE
     /* Existing prototype hover/travel range, relative to actual takeoff
      * feet. A high/negative source floor must not force flight toward Z=0. */
     w->target_z=cl(w->target_z+vertical*6.0f*dt,
                    w->flight_base_z+.35f,w->flight_base_z+36.f);
#else
     w->target_z=cl(w->target_z+vertical*6.0f*dt,.35f,36.f);
#endif''')
    world = once(world, 'else w->target_z=0;', '''else
#ifdef B24_G75_SOURCE_CAPSULE
  /* B14_WORLD_HEIGHT_SUPPORT: remain on accepted source support, or
   * continue the existing bounded descent until G75 catches a real floor.
   * Never manufacture a support plane at absolute world zero. */
  w->target_z=w->ground_supported?w->ground_z:w->z-7.f*dt;
#else
  w->target_z=0;
#endif''')
    world += '\n' + (HERE / 'world_height_functions.c.inc').read_text()
    # Keep the existing pause guard and landing animation timestamps.
    main = once(main,
        'world.flying=!world.flying;world.target_z=world.flying?fmaxf(world.target_z,.8f):0.f;',
        'b14_world_toggle_flight(&world);')
    main = once(main, '''world.flying=!world.flying;
                    world.target_z=world.flying?fmaxf(world.target_z,.8f):0.f;''',
        'b14_world_toggle_flight(&world);')
    main = once(main, 'world.x=b75_x;world.y=b75_y;world.z=b75_z;',
        '''world.x=b75_x;world.y=b75_y;world.z=b75_z;
          /* Source support is observed AFTER the single G75 reconciliation.
           * A nearby floor is insufficient: feet must actually be on it. */
          float b75_support_z=0.f;
          const int b75_supported=!world.flying && b24_g75_support_at(
              &b24_original_walls,world.x,world.y,world.z,&b75_support_z);
          b14_world_accept_ground_support(&world,b75_supported,b75_support_z);''')
    anchor = 'int b24_g75_capsule_reconcile('
    capsule = once(capsule, anchor, '''/* B14_WORLD_HEIGHT_SUPPORT: same native-first/optional-road authority as
 * reconciliation, read-only. Do not snap to a different scene layer. */
int b24_g75_support_at(const B24C1OriginalCollision *world,
 float x,float y,float feet_z,float *support_z){
 if(!world||!world->ready||!support_z||!finite3(x,y,feet_z))return 0;
 float h=0.f;
 if(!g159_authoritative_first_native_then_source_road(world,x,y,feet_z,&h)
     ||fabsf(h-feet_z)>.0001f)return 0;
 *support_z=h;
 return 1;
}
''' + anchor)
    capsule = once(capsule, '''   if(!g159_authoritative_first_native_then_source_road(world,x,y,z,&original_support))
     z=nextz;''', '''   if(!g159_authoritative_first_native_then_source_road(world,x,y,z,&original_support))
     z=nextz;
   else if(stepz<0.f && z>original_support+.0001f){
     /* A NEAR floor is not contact. Old G75 stopped descent in the
      * .35-.50 gap between the step guard and near-floor search.
      * Keep descending at the existing bounded rate; never pass through
      * that actual surface, move upwards to a roof, or delete a wall. */
     z=fmax2(nextz,original_support);
   }''')
    ch = once(ch, '#endif', '''/* Exact accepted feet/support agreement, never just a nearby floor. */
int b24_g75_support_at(const B24C1OriginalCollision *world,
 float x,float y,float feet_z,float *support_z);
#endif''')
    if main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)') != 1:
        raise ValueError('Expected exactly one B14 movement owner')
    if main.count('b24_g75_capsule_reconcile(') != 1:
        raise ValueError('Expected exactly one G75 reconciliation owner')
    for name, value in zip(paths, (main, world, header, capsule, ch)):
        paths[name].write_text(value)
    print('PASS B14 world-height frame: source support, takeoff datum, bounded landing; no VPK')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, default=ROOT / 'work')
    patch(parser.parse_args().work)
