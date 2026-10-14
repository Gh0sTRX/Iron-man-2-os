#!/usr/bin/env python3
"""Source-authentic Underwater dual-mesh skin QA using existing B13 methods.
Expected FIRST mesh 811 source verts and SECOND 29, unlike the previous 5
one-skin models. Never infer matching topology or rig: validate each palette.
Original B13 skin parser's arbitrary 128 weight-value ceiling is too low:
the genuine 811v Underwater source skin descriptor has 192 weights.
"""
from __future__ import annotations
import argparse,math,struct,sys,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact

def rig_from_authentic_source(raw):
    """B13 identical scene-node walk but root lookup must avoid '#Bip01-node'
       marker strings that preceded actual null-delimited 'Bip01-node'."""
    at=raw.find(b'\x00Bip01-node\x00')
    if at<0:raise ValueError('authentic null-delimited Bip01 root not found')
    t=at+1
    needle=struct.pack('<I',t)
    roots=[]
    for o in range(32,len(raw)-72,4):
        if raw[o:o+4]==needle:
            n,child=struct.unpack_from('<II',raw,o+52)
            if 0<n<32 and child+n*72<=len(raw):roots.append(o)
    if len(roots)!=1:raise ValueError(f'underwater ambiguous real scene root {roots}')
    nodes=[];seen=set()
    def walk(o,parent):
        if o in seen:raise ValueError('duplicate original skeletal node')
        seen.add(o)
        p=struct.unpack_from('<I',raw,o)[0]
        if p>=len(raw):raise ValueError('name pointer outside source')
        end=raw.find(b'\0',p)
        if end<0:raise ValueError('missing name terminator')
        name=raw[p:end].decode('latin1')
        pos=struct.unpack_from('<3f',raw,o+12)
        quat=struct.unpack_from('<4f',raw,o+24)
        scale=struct.unpack_from('<3f',raw,o+40)
        count,ch=struct.unpack_from('<II',raw,o+52)
        if count>32 or count and ch+count*72>len(raw):
            raise ValueError('invalid source rig children')
        nodes.append(dict(name=name,offset=o,parent=parent,pos=pos,quat=quat,scale=scale))
        for i in range(count):walk(ch+i*72,name)
    walk(roots[0],None)
    return nodes

def dual_skin(ipa:Path,im2t:Path,mod):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read('Payload/IronMan2.app/models')
    raw=get_exact(packed,decode(packed,'.bdae'),'LC_MC_UnderWater.bdae')
    nodes=rig_from_authentic_source(raw)
    model=im2t.read_bytes()
    magic,nv,nt,tw,th=struct.unpack_from('<4sIIII',model)
    if (magic,nv,nt,tw,th)!=(b'IM2T',840,1078,512,512):
        raise ValueError('original Underwater source IM2T topology drift')
    if len(model)!=20+nv*20+nt*6+tw*th*4:raise ValueError('truncated underwater model')
    verts=np.frombuffer(model,dtype='<f4',count=840*5,offset=20).reshape(840,5)
    mapnodes={}
    for node in nodes:
        ptr=struct.unpack_from('<I',raw,node['offset']+8)[0]
        if 0<=ptr<len(raw):
            end=raw.find(b'\x00',ptr)
            if end>=ptr:
                label=raw[ptr:end].decode('latin1')
                if label in mapnodes and mapnodes[label]!=node['name']:
                    raise ValueError('nonunique original bone label '+label)
                mapnodes[label]=node['name']
    groups=[];errors=[]
    for count,start in ((811,0),(29,811)):
        skin=mod.parse_skin(raw,count)
        _,names,inv,idx,weights=skin
        if not all(n in mapnodes for n in names):
            missing=[n for n in names if n not in mapnodes]
            raise ValueError('original joint names missing in rig '+str(missing))
        joints=[mapnodes[n] for n in names]
        rest=mod.worlds(nodes)
        delta=max(float(np.max(np.abs(rest[j]@inv[i]-np.eye(4)))) for i,j in enumerate(joints))
        if delta>2e-4:raise ValueError(f'original bind matrices invalid for {count} verts, residual {delta}')
        obj={'nodes':nodes,'joints':joints,'inv':inv,'indexes':idx,'weights':weights,
             'verts':verts[start:start+count]}
        rest_positions=mod.bake_pose(obj,None,0)
        maxpos=float(np.max(np.abs(rest_positions-verts[start:start+count,:3])))
        errors.append(maxpos)
        print('AUTHENTIC_UNDERWATER_SKIN',count,'bones',len(names),'unique_weights',int((weights>0).sum()),
              'bind_matrix_maxerr',delta,'bind_pose_source_vertex_maxerr',maxpos)
        groups.append(obj)
    return groups,errors,raw

def main(ipa:Path,im2t:Path,b13_dir:Path):
    sys.path.insert(0,str(b13_dir))
    import b13_bake as mod
    groups,errors,raw=dual_skin(ipa,im2t,mod)
    if max(errors)>0.005:raise ValueError('Original Underwater skinned rest pose mismatch. Wrong geometry source/order.')
    with zipfile.ZipFile(ipa) as z:
        packed=z.read('Payload/IronMan2.app/anims')
    entries=decode(packed,'.anim')
    for animname in ('Underwater_Float_idle.anim','Underwater_Swim_F.anim',
                     'Underwater_Swim_Att_Aim.anim'):
        clip=mod.decode_anim(get_exact(packed,entries,animname))
        changes=[]
        for skin in groups:
            pose0=mod.bake_pose(skin,clip,0)
            pose1=mod.bake_pose(skin,clip,max(1,clip.duration_ms//2))
            if not np.isfinite(pose0).all() or not np.isfinite(pose1).all():raise ValueError('bad original clip')
            changes.append(float(np.max(np.abs(pose1-pose0))))
        print('AUTHENTIC_UNDERWATER_PLAYER_ANIMATION',animname,'duration',clip.duration_ms,
              'max_vertex_motion_each_submesh',changes)
        if max(changes)<1e-4:raise ValueError('Original source animation did not move the original armor')
    print('PASS source-authentic underwater TWO real skin descriptors, root scene hierarchy, source rest binding and 3 native animations; not in Vita game yet')
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--ipa',type=Path,required=True)
    p.add_argument('--im2t',type=Path,required=True)
    p.add_argument('--b13-dir',type=Path,required=True)
    a=p.parse_args();main(a.ipa,a.im2t,a.b13_dir)
