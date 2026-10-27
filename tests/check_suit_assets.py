"""Verify the actual owner-derived model layouts before sharing pose streams."""
from pathlib import Path
import hashlib
import struct
import sys
root=Path(sys.argv[1])
geometry=[];textures=[]
for name in ('mark6','mark4','stealth'):
    data=(root/'models'/f'{name}.im2t').read_bytes()
    magic,nv,nt,tw,th=struct.unpack_from('<4s4I',data)
    assert (magic,nv,nt,tw,th)==(b'IM2T',802,970,512,512)
    end=20+nv*20+nt*6
    assert len(data)==end+tw*th*4
    geometry.append(data[20:end]);textures.append(hashlib.sha256(data[end:]).hexdigest())
assert geometry[0]==geometry[1]==geometry[2]
assert hashlib.sha256(geometry[0]).hexdigest()=='a8b1bccd72c494797ae5470d6d1bb0a7537c67078cb1f15b75d0bad212071f90'
assert len(set(textures))==3
for name in ('ground_idel','walk_f','walk_b','walk_l','walk_r','run',
             'air_idel','air_move_f','air_move_b','air_move_l','air_move_r',
             'fly_f','fly_b','fly_l','fly_r','fly_f_rush','ground_combo_1',
             'ground_combo_2','ground_combo_3','aim_ground_beam1','aim_ground_beam2',
             'aim_ground_beam3','aim_float_beam1','aim_float_beam2','aim_float_beam3'):
    p=root/'animations'/f'ironman_ironman_{name}.im2v'
    with p.open('rb') as source:
        magic,nv,frames,fps,ms=struct.unpack('<4s4I',source.read(20))
    assert magic==b'IM2V' and nv==802 and fps==20 and frames>0,p
    assert p.stat().st_size==20+frames*nv*12,p
print('PASS genuine VI/IV/Stealth: identical geometry/UV/topology, separate textures, 25 compatible original pose streams')
