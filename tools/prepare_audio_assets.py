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

IPA_SHA='4c338c71cdd2817afb10099b90834c911d3c82e94adc477f24a9f9f4e0479c94'
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
    """Recover the native 803x40 inline-name records, never alphabetical IDs.

    G140/G142 native LoadMusic refers to VM 0x473700. Two identical inline
    string tables exist in the verified executable; these are NOT pointers.
    Each candidate must match both proven IDs and every original WAV name.
    """
    if len(exe)<28 or struct.unpack_from('<I',exe)[0]!=0xfeedface:
        raise ValueError('Expected verified 32-bit Mach-O')
    anchor=b'm_pre_cutscene_intro\0';pos=0;candidates={}
    expected=set(names)
    if len(names)!=803 or len(expected)!=803:raise ValueError('Invalid original sound inventory')
    while True:
        pos=exe.find(anchor,pos)
        if pos<0:break
        first=pos-87*40;pos+=1
        if first<0 or first+803*40>len(exe):continue
        rows=[]
        for index in range(803):
            record=exe[first+index*40:first+(index+1)*40]
            end=record.find(b'\0')
            if end<1:break
            try:name=record[:end].decode('ascii')+'.www'
            except UnicodeDecodeError:break
            if name not in expected:break
            rows.append(name)
        if len(rows)!=803 or len(set(rows))!=803:continue
        if rows[319]!='vfx_intro_level1_jarvis_1.www':continue
        candidates[first]=rows
    if not candidates or len({tuple(rows) for rows in candidates.values()})!=1:
        raise ValueError('Native 803x40 inline sound-name tables are absent or disagree')
    first=min(candidates)
    return candidates[first],first


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
    if sha_file(ipa)!=IPA_SHA:raise ValueError('Original IPA SHA256 mismatch')
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
        if first!=4663040 or exe[first:first+803*40]!=exe[4695160:4695160+803*40]:
            raise ValueError('Previously native-referenced duplicate sound table mismatch')
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
                      'native_inline_name_table_file_offset':first,'device_playback_verified':False}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ipa',type=Path,required=True)
    parser.add_argument('--asset-root',type=Path,required=True)
    args=parser.parse_args();prepare(args.ipa,args.asset_root)
