#!/usr/bin/env python3
"""Compile actual generated gameplay and extract its actual Circle event."""
import argparse
import importlib.util
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def event_block(source):
    anchor = 'if(!b24_unified_paused(&b24_game) && e.cbutton.button==SDL_CONTROLLER_BUTTON_B){'
    assert source.count(anchor) == 1
    start = source.index(anchor)
    opening = source.index('{', start)
    depth = 0
    for end in range(opening, len(source)):
        depth += (source[end] == '{') - (source[end] == '}')
        if not depth:
            return source[start:end + 1]
    raise AssertionError('Unclosed actual Circle event')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, default=ROOT / 'work')
    parser.add_argument('--sanitize', action='store_true')
    parser.add_argument('--expect-baseline-failure', action='store_true')
    parser.add_argument('--baseline-case', choices=('takeoff', 'landing'), default='takeoff')
    args = parser.parse_args()
    work = args.work.resolve()
    current = ROOT / 'work'
    with tempfile.TemporaryDirectory(prefix='im2_world_height_') as temp:
        temp = Path(temp)
        (temp / 'actual_circle_event.inc').write_text(event_block((work / 'src/main.c').read_text()))
        b24 = work / 'b24/b24_unified'
        deps = current / 'b24/b24_unified'
        command = shlex.split(os.environ.get('CC', 'cc')) + [
            '-std=c11', '-Wall', '-Wextra', '-Werror', '-pedantic',
            '-DB24_G75_SOURCE_CAPSULE=1',
            '-DB24_G108_SOURCE_VISUAL_WALLS=1', '-DB24_G159_ROAD_FLOOR_CANDIDATE=1',
            '-DB24_G160_ROAD_SPATIAL_INDEX=1', '-DB24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL=1',
            '-I' + str(work / 'src'), '-I' + str(b24), '-I' + str(deps), '-I' + str(temp)]
        command += (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
                    if args.sanitize else ['-O2'])
        command += [str(work / 'src/b14_world.c'), str(b24 / 'b24_g75_source_capsule.c')]
        command += [str(deps / name) for name in (
            'b24_g108_visible_original_wall_grid.c', 'b24_g159_real_source_road.c',
            'b24_g160_original_road_spatial.c', 'b24_gpu_g68_collision.c', 'b24_c1_original_collision.c')]
        command += [str(HERE / 'test_world_height.c'), '-lm', '-o', str(temp / 'test')]
        subprocess.run(command, check=True)
        assets = temp / 'app0:assets'
        assets.mkdir()
        (assets / 'G66_city.g66m').symlink_to((current / 'assets/G66_city.g66m').resolve())
        collider = str((current / 'assets/G66_original_collision.g66c').resolve())
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
        mode = 'baseline-landing' if args.baseline_case == 'landing' else 'real'
        result = subprocess.run([str(temp / 'test'), collider, mode], cwd=temp,
                                text=True, capture_output=True, env=env)
        print(result.stdout, end='')
        if args.expect_baseline_failure:
            assertion = 'world.z>before' if args.baseline_case == 'takeoff' else 'fabsf(world.z-floor)'
            assert result.returncode < 0 and assertion in result.stderr, result.stderr
            print('PASS baseline reproduction: ' + args.baseline_case + ' fails on the real source road')
            return
        if result.returncode:
            raise RuntimeError(f'World-height test exit {result.returncode}: {result.stderr}')
        # Fresh process, no optional real-height visual/road assets: translated
        # native geometry is ONLY a synthetic reference-frame regression.
        (assets / 'G66_city.g66m').unlink()
        subprocess.run([str(temp / 'test'), collider, 'translated'], cwd=temp, check=True, env=env)
        legacy = shlex.split(os.environ.get('CC', 'cc')) + [
            '-std=c11', '-Wall', '-Wextra', '-Werror', '-pedantic', '-O2',
            '-I' + str(work / 'src'), str(work / 'src/b14_world.c'),
            str(HERE / 'test_b14_legacy.c'), '-lm', '-o', str(temp / 'legacy')]
        subprocess.run(legacy, check=True)
        subprocess.run([str(temp / 'legacy')], check=True)
        # Duplicate patch application must fail closed on a disposable copy.
        if not args.expect_baseline_failure:
            spec = importlib.util.spec_from_file_location('height_patch', HERE / 'patch_world_height.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            copy = temp / 'duplicate-work'
            names = ('src/main.c', 'src/b14_world.c', 'src/b14_world.h',
                     'b24/b24_unified/b24_g75_source_capsule.c',
                     'b24/b24_unified/b24_g75_source_capsule.h')
            for name in names:
                dest = copy / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(work / name, dest)
            before = {name: (copy / name).read_bytes() for name in names}
            try:
                module.patch(copy)
            except ValueError as error:
                assert 'already present' in str(error)
            else:
                raise AssertionError('Duplicate height patch was accepted')
            assert all((copy / name).read_bytes() == data for name, data in before.items())
        print('PASS actual Circle + B14/G75 source integration, strict host checks')


if __name__ == '__main__':
    main()
