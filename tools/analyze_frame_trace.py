#!/usr/bin/env python3
"""Summarize sampled CPU/frame telemetry; never infer GPU busy or device FPS."""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics


def analyze(path):
    samples=[]
    with Path(path).open(newline='') as source:
        for row in csv.DictReader(source):
            if len(samples)>=4096:raise ValueError('Trace exceeds writer row limit')
            if row.get('schema')!='1' or row.get('gpu_busy_available')!='0':
                raise ValueError('Unsupported schema or GPU busy claim')
            for key in ('frame','ms','paused','cpu_mhz','gpu_mhz','bus_mhz','xbar_mhz'):
                row[key]=int(row[key])
            if row['frame']<0 or row['ms']<0 or row['paused'] not in (0,1):
                raise ValueError('Invalid frame, timestamp or pause state')
            for key in ('raw_dt_ms','simulation_dt_ms','controls_dt_ms','animation_blend_dt_ms',
                        'cpu_frame_wall_ms','stream_ms','camera_ms','scene_submit_ms','suit_submit_ms',
                        'hud_submit_ms','swap_wall_ms','world_x','world_y','world_z','gpu_x','gpu_y','gpu_z'):
                row[key]=float(row[key])
                if not math.isfinite(row[key]) or (key.endswith('_ms') and row[key]<0):
                    raise ValueError('Invalid numeric sample')
            if samples and (row['frame']<=samples[-1]['frame'] or row['ms']<samples[-1]['ms']):
                raise ValueError('Out-of-order frame/timestamp')
            samples.append(row)
    if not samples:raise ValueError('No samples')
    raw=sorted(r['raw_dt_ms'] for r in samples)
    return {
        'sampled_rows':len(samples),'first_frame':samples[0]['frame'],'last_frame':samples[-1]['frame'],
        'mean_sampled_interval_ms':statistics.fmean(raw),
        'p95_sampled_interval_ms':raw[math.ceil(.95*len(raw))-1],
        'unpaused_world_dt_reduced_rows':sum(not r['paused'] and r['raw_dt_ms']>r['simulation_dt_ms']+.01 for r in samples),
        'world_controls_dt_difference_rows':sum(abs(r['simulation_dt_ms']-r['controls_dt_ms'])>.01 for r in samples),
        'max_world_gpu_root_distance':max(math.dist([r['world_x'],r['world_y'],r['world_z']],
                                                               [r['gpu_x'],r['gpu_y'],r['gpu_z']]) for r in samples),
        'mean_cpu_phase_ms':{key:statistics.fmean(r[key] for r in samples) for key in
           ('stream_ms','camera_ms','scene_submit_ms','suit_submit_ms','hud_submit_ms','swap_wall_ms')},
        'observed_clocks_mhz':{key:sorted({r[key] for r in samples}) for key in
                             ('cpu_mhz','gpu_mhz','bus_mhz','xbar_mhz')},
        'gpu_busy_available':False,
        'scope':'Sampled CPU wall/frame intervals; not continuous FPS or GPU occupancy',
    }


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',type=Path)
    print(json.dumps(analyze(parser.parse_args().csv),indent=2))
