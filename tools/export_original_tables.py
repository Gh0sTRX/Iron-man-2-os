#!/usr/bin/env python3
"""Convert locally authorized generated tables into an EXTERNAL runtime asset.

Reads data initializers, never executes an input C/Python file. No download.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct


def array(text, name):
    tail = text.split(name, 1)[1].split('=', 1)[1].split('};', 1)[0]
    return [next(csv.reader([s], skipinitialspace=True)) for s in re.findall(r'\{([^{}]+)\}', tail)]


def number(value):
    value = value.strip()
    if value == 'B24G217_UNKNOWN_U32':
        return 0xffffffff
    if not re.fullmatch(r'-?(?:0x[0-9a-fA-F]+|[0-9]+)[uUlL]*', value):
        raise ValueError('Unsupported numeric initializer')
    return int(re.sub(r'[uUlL]+$', '', value), 0) if not re.fullmatch(r'-?0[0-9]+', value) else int(value)


def convert(states_text, mission_text, enum_header):
    pool = bytearray()
    offsets = {}

    def string(value):
        value = value.strip()
        if value not in offsets:
            data = value.encode('ascii')
            if not data or len(data)>127 or any(c<32 or c>126 for c in data):
                raise ValueError('Unsupported table string')
            offsets[value] = len(pool)
            pool.extend(data + b'\0')
        return offsets[value]

    names = re.findall(r'"([^"\n]+)"', states_text.split('b24g217_original_suit_source_names', 1)[1].split('};', 1)[0])
    states = array(states_text, 'b24g217_true_2010_owner_states')
    events = array(states_text, 'b24g217_source_attack_trail_events')
    mission = array(mission_text, 'b24_g137_source_lua_events')
    if len(names)!=4 or len(states)!=776 or len(events)!=224 or not 0<len(mission)<=72:
        raise ValueError('Unexpected original table shape')
    enums = {name: int(n) for name, n in re.findall(r'(B24_G137_CALL_\w+)\s*=\s*(\d+)', enum_header)}
    rows = bytearray()
    for name in names:
        rows.extend(struct.pack('<I', string(name)))
    for row in states:
        if len(row)!=7:raise ValueError('Invalid state row')
        rows.extend(struct.pack('<5I2H', string(row[0]), *map(number, row[1:])))
    for row in events:
        if len(row)!=6:raise ValueError('Invalid track row')
        rows.extend(struct.pack('<4I2H', string(row[0]), *map(number, row[1:])))
    for row in mission:
        if len(row)!=8:raise ValueError('Invalid mission row')
        offset=0xffffffff if row[5].strip()=='0' else string(row[5])
        rows.extend(struct.pack('<HHiiiIBBH',number(row[0]),enums[row[1].strip()],
                               *map(number,row[2:5]),offset,number(row[6]),number(row[7]),0))
    header = struct.pack('<4s7I', b'IM2D',1,4,194,224,len(mission),len(pool),0)
    return header+rows+pool


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--states-header', required=True, type=Path)
    parser.add_argument('--mission-c', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.is_relative_to(root / 'src') or output.is_relative_to(root / 'tests'):
        raise ValueError('Original data must remain outside source/test trees')
    data=convert(args.states_header.read_text(),args.mission_c.read_text(),
                 (root/'src/b24/b24_unified/b24_g137_source_mission000_intro.h').read_text())
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists() and output.read_bytes()!=data:
        raise ValueError('Refusing to replace a different external data asset')
    output.write_bytes(data)
    print(json.dumps({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}))
