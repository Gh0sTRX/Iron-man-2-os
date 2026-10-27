#!/usr/bin/env python3
"""Verify the authorized IPA, recover native sound ordinals, decode external PCM.

No download, source patch, asset upload or game-event guess. Supports resuming
only outputs whose original and PCM hashes still match the saved manifest.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile

EXE_SHA='3ba6337a23ab7e08f2e025ec9731c53a7990e8d611b59eac07ba00cb63acc629'


def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def riff_info(data):
    if len(data)<44 or data[:4]!=b'RIFF' or data[8:12]!=b'WAVE':
        raise ValueError('Source is not RIFF/WAVE')
    end=struct.unpack_from('<I',data,4)[0]+8
    if end!=len(data):raise ValueError('RIFF size mismatch')
    at=12;fmt=None;payload=None
    while at+8<=end:
        tag=data[at:at+4];n=struct.unpack_from('<I',data,at+4)[0];at+=8
        if n>end-at:raise ValueError('Truncated WAVE chunk')
        if tag==b'fmt ':
            if fmt is not None or n<16:raise ValueError('Invalid WAVE format')
            codec,ch,hz,avg,align,bits=struct.unpack_from('<HHIIHH',data,at)
            if ch not in (1,2) or not 8000<=hz<=192000 or not avg or not align:
                raise ValueError('Unsupported WAVE dimensions')
            fmt=dict(codec=codec,channels=ch,hz=hz,avg_bytes=avg,align=align,bits=bits)
        elif tag==b'data':
            if payload is not None or n==0:raise ValueError('Invalid WAVE data')
            payload=n
        at+=n+(n&1)
    if at!=end or fmt is None or payload is None:raise ValueError('Incomplete WAVE')
    return dict(fmt,payload_bytes=payload)


def sound_ordinals(exe,names):
    """Find the 803x40 native NAME-pointer lane using both proven anchors.

    Does not claim the other fields' semantics or that every ID has a bound
    gameplay event. Requires every pointer to resolve to one original WAV.
    """
    if len(exe)<28 or struct.unpack_from('<I',exe)[0]!=0xfeedface:
        raise ValueError('Expected verified 32-bit Mach-O')
    ncmds,command_bytes=struct.unpack_from('<II',exe,16)
    if ncmds>256 or 28+command_bytes>len(exe):raise ValueError('Bad Mach-O load commands')
    segments=[];at=28
    for _ in range(ncmds):
        if at+8>28+command_bytes:raise ValueError('Truncated load command')
        cmd,size=struct.unpack_from('<II',exe,at)
        if size<8 or at+size>28+command_bytes:raise ValueError('Bad command size')
        if cmd==1:
            if size<56:raise ValueError('Bad segment')
            vm,vmsize,offset,filesize=struct.unpack_from('<4I',exe,at+24)
            if offset+filesize>len(exe):raise ValueError('Bad segment bounds')
            if filesize:segments.append((vm,offset,filesize))
        at+=size
    if at!=28+command_bytes:raise ValueError('Load command size mismatch')
    by_pointer={}
    for name in names:
        for spelling in (name,name.removesuffix('.www')):
            needle=spelling.encode('ascii')+b'\0';pos=0
            while True:
                pos=exe.find(needle,pos)
                if pos<0:break
                for vm,offset,filesize in segments:
                    if offset<=pos and pos+len(needle)<=offset+filesize:
                        address=vm+pos-offset
                        if address in by_pointer and by_pointer[address]!=name:
                            raise ValueError('Ambiguous sound string')
                        by_pointer[address]=name
                pos+=1
    candidates={}
    for pointer,name in by_pointer.items():
        if name!='m_pre_cutscene_intro.www':continue
        needle=struct.pack('<I',pointer);pos=0
        while True:
            pos=exe.find(needle,pos)
            if pos<0:break
            first=pos-87*40;pos+=1
            if first<0 or first%4 or first+802*40+4>len(exe):continue
            rows=[by_pointer.get(struct.unpack_from('<I',exe,first+i*40)[0]) for i in range(803)]
            if rows[319]!='vfx_intro_level1_jarvis_1.www' or any(n is None for n in rows):continue
            if len(set(rows))!=803 or set(rows)!=set(names):continue
            if not any(offset<=first and first+802*40+4<=offset+size for _,offset,size in segments):continue
            candidates[first]=rows
    if len(candidates)!=1:raise ValueError('Native 803x40 sound-name lane is absent or ambiguous')
    first,rows=next(iter(candidates.items()))
    return rows,first


def catalog(rows):
    pool=bytearray();offsets=[]
    for name in rows:
        pcm=name.removesuffix('.www')+'.pcm'
        if not re.fullmatch(r'[A-Za-z0-9_\-]{1,119}\.pcm',pcm):
            raise ValueError('Unsafe original sound name')
        offsets.append(len(pool));pool.extend(pcm.encode('ascii')+b'\0')
    return struct.pack('<4s3I',b'IM2A',1,len(rows),len(pool))+struct.pack('<'+'I'*len(rows),*offsets)+pool


def prepare(ipa,asset_root):
    repo=Path(__file__).resolve().parents[1];asset_root=asset_root.resolve()
    if asset_root.is_relative_to(repo):raise ValueError('Keep owner assets outside the checkout')
    if not shutil.which('ffmpeg'):raise ValueError('ffmpeg is required for original audio decoding')
    if ipa.stat().st_size!=248613763:raise ValueError('Unexpected original IPA size/version')
    dest=asset_root/'audio';dest.mkdir(parents=True,exist_ok=True)
    metadata=asset_root/'data';metadata.mkdir(exist_ok=True)
    manifest_file=metadata/'audio_manifest.json'
    previous=json.loads(manifest_file.read_text()).get('sounds',[]) if manifest_file.exists() else []
    previous={r['source_name']:r for r in previous}
    done=[]
    with zipfile.ZipFile(ipa) as archive:
        owner='Payload/IronMan2.app/'
        exe=archive.read(owner+'IronMan2')
        if len(exe)!=7480208 or hashlib.sha256(exe).hexdigest()!=EXE_SHA:
            raise ValueError('Original executable SHA256 mismatch')
        entries=[x for x in archive.infolist() if x.filename.startswith(owner) and
                 '/' not in x.filename[len(owner):] and x.filename.endswith('.www')]
        names=[x.filename[len(owner):] for x in entries]
        if len(names)!=803 or len(set(names))!=803:raise ValueError('Unexpected source audio bank')
        if any(not re.fullmatch(r'[A-Za-z0-9_\-]{1,119}\.www',name) for name in names):
            raise ValueError('Unsafe original audio basename')
        rows,first=sound_ordinals(exe,names)
        by_name={x.filename[len(owner):]:x for x in entries}
        for index,name in enumerate(rows):
            if by_name[name].file_size>64*1024*1024:raise ValueError('Source audio exceeds size bound')
            raw=archive.read(by_name[name]);info=riff_info(raw)
            original_sha=hashlib.sha256(raw).hexdigest()
            target=dest/(name.removesuffix('.www')+'.pcm')
            old=previous.get(name)
            if target.exists():
                if (not old or old['source_sha256']!=original_sha or old['pcm_sha256']!=sha_file(target)
                    or old['lua_id']!=index+1 or old['native_index']!=index or old['pcm_name']!=target.name):
                    raise ValueError('Existing PCM is not the previously verified output')
                done.append(old);continue
            with tempfile.TemporaryDirectory(dir=dest,prefix='.decode-') as temp:
                source=Path(temp)/'source.wav';output=Path(temp)/'decoded.pcm'
                source.write_bytes(raw)
                result=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',
                    '-i',str(source),'-vn','-acodec','pcm_s16le','-ar','48000','-ac','2',
                    '-f','s16le',str(output)],capture_output=True)
                if result.returncode:raise ValueError('Original WAV decoding failed')
                size=output.stat().st_size
                if not size or size>2147483647 or size%4:raise ValueError('Invalid decoded stereo PCM')
                pcm_sha=sha_file(output);output.rename(target)
            done.append(dict(lua_id=index+1,native_index=index,source_name=name,
                source_sha256=original_sha,pcm_name=target.name,pcm_sha256=pcm_sha,
                pcm_bytes=size,source_format=info,gameplay_event_binding_verified=False))
            temp_manifest=manifest_file.with_suffix('.json.part')
            temp_manifest.write_text(json.dumps(dict(original_exe_sha256=EXE_SHA,sounds=done),indent=2)+'\n')
            temp_manifest.replace(manifest_file)
        payload=catalog(rows)
        output=metadata/'audio_catalog.im2a'
        if output.exists() and output.read_bytes()!=payload:
            raise ValueError('Refusing to overwrite a different audio catalog')
        pending=output.with_suffix('.im2a.part');pending.write_bytes(payload);pending.replace(output)
    print(json.dumps({'verified_sounds':len(done),'catalog_sha256':hashlib.sha256(payload).hexdigest(),
                      'native_name_pointer_lane_file_offset':first,'device_playback_verified':False}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ipa',type=Path,required=True)
    parser.add_argument('--asset-root',type=Path,required=True)
    args=parser.parse_args();prepare(args.ipa,args.asset_root)
