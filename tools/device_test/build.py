#!/usr/bin/env python3
"""Build, verify and locally package the explicitly authorized source diagnostic.

No network downloads, historical source generators, VPK uploads or installation.
Owner data and the package must remain outside the checkout. This manual helper
never changes the seven full-port acceptance gates or adds a CMake VPK target.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[2]
IMAGE='vitasdk/vitasdk@sha256:8227da1b596d981f4513cd9b36bda1e43857f6dae5bcf4312c1cd40167f7d9bb'
TITLE_ID='IM2DG0001'
VERSION='00.03'
RESOURCES=('models','animations','maps','assets')
TABLE_SHA='e68d328a31636aeac5fc6347a69cda4f15a2a7fc20ac7094b35f90e9c48ea42a'


def digest(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):result.update(data)
    return result.hexdigest()


def require(condition,message):
    if not condition:raise ValueError(message)


def sfo_strings(data):
    require(len(data)>=20,'Truncated SFO')
    magic,version,keys,values,count=struct.unpack_from('<5I',data)
    require(magic==0x46535000 and count<=100 and 20+count*16<=keys<=values<=len(data),'Invalid SFO header')
    result={}
    for i in range(count):
        key,fmt,size,capacity,offset=struct.unpack_from('<HHIII',data,20+i*16)
        end=data.find(b'\0',keys+key,values)
        require(keys+key<end<values and size<=capacity and values+offset+capacity<=len(data),'Invalid SFO entry')
        name=data[keys+key:end].decode('ascii')
        require(name not in result,'Duplicate SFO key')
        if fmt==0x204:
            result[name]=data[values+offset:values+offset+size].rstrip(b'\0').decode('utf-8')
    return result


def collect_assets(asset_root,baseline):
    files={}
    for directory in RESOURCES:
        base=asset_root/directory
        require(base.is_dir() and not base.is_symlink(),'Missing or linked resource directory')
        for path in sorted(base.rglob('*')):
            require(not path.is_symlink(),'Linked resource is not accepted')
            if path.is_file():files[path.relative_to(asset_root).as_posix()]=digest(path)
    require(set(files)==set(baseline['resources_sha256']),'Owner resource inventory differs from verified baseline')
    for name,sha in baseline['resources_sha256'].items():
        require(files[name]==sha,'Owner resource differs from verified baseline: '+name)
    require(sum(name.startswith('models/') for name in files)==5,'Expected five verified suit models')
    table=asset_root/'data/source_tables.im2d'
    require(table.is_file() and not table.is_symlink() and digest(table)==TABLE_SHA,'Missing/changed verified original source tables')
    files['data/source_tables.im2d']=TABLE_SHA
    return files


def run_check(name,command,out,environment=None):
    print('RUN '+name,flush=True)
    log=out/(name+'.log')
    with log.open('w') as handle:
        result=subprocess.run(command,cwd=ROOT,env=environment,stdout=handle,stderr=subprocess.STDOUT)
    require(result.returncode==0,'Check failed; inspect '+str(log))
    return dict(status='passed',log=log.name,log_sha256=digest(log))


def verify_vpk(path,files,eboot_sha):
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None,'Package CRC failure')
        names=archive.namelist()
        require(len(names)==len(set(names)),'Duplicate ZIP entries')
        require(all(not n.startswith('/') and '..' not in n.split('/') and '\\' not in n for n in names),'Unsafe ZIP path')
        require({n for n in names if not n.endswith('/')}==set(files)|{'sce_sys/param.sfo','eboot.bin'},'Package inventory mismatch')
        for name,sha in files.items():
            with archive.open(name) as f:
                h=hashlib.sha256()
                for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
            require(h.hexdigest()==sha,'Packaged resource hash mismatch: '+name)
        eboot=archive.read('eboot.bin')
        require(eboot[:4]==b'SCE\0' and hashlib.sha256(eboot).hexdigest()==eboot_sha,'Invalid or stale SELF')
        sfo=sfo_strings(archive.read('sce_sys/param.sfo'))
        require(sfo.get('TITLE_ID')==TITLE_ID and sfo.get('APP_VER')==VERSION,'Incorrect diagnostic title/version')
    return sfo


def main(args):
    asset_root=args.asset_root.resolve();out=args.output.resolve()
    require(not asset_root.is_relative_to(ROOT) and not out.is_relative_to(ROOT),'Keep assets and package outside checkout')
    require(not out.exists(),'Preserve existing output; choose an unused output directory')
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(),'Commit reviewed source changes before packaging')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    baseline=json.loads(args.baseline_manifest.read_text())
    files=collect_assets(asset_root,baseline)
    gates_path=ROOT/'research/b24_unified/g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json'
    gates_sha=digest(gates_path)
    out.mkdir(parents=True,mode=0o700)
    environment=os.environ.copy();environment['IM2_ASSET_ROOT']=str(asset_root)
    checks={}
    checks['host']=run_check('host',['bash','tools/test_host.sh'],out,environment)
    sanitized=environment.copy();sanitized.update(IM2_HOST_BUILD='build-sanitized',IM2_SANITIZERS='ON')
    checks['sanitizers']=run_check('sanitizers',['bash','tools/test_host.sh'],out,sanitized)
    checks['vita_arm']=run_check('vita-arm',['bash','tools/build_vita.sh'],out)
    elf=ROOT/'build-vita/im2_beta'
    header=elf.read_bytes()[:52]
    require(len(header)==52 and header[:7]==b'\x7fELF\x01\x01\x01' and struct.unpack_from('<H',header,18)[0]==40,'Not a little-endian ARM ELF32')
    commands=f'''set -eu
vita-elf-create /workspace/build-vita/im2_beta /diagnostic/im2_beta.velf
vita-make-fself -c -s /diagnostic/im2_beta.velf /diagnostic/eboot.bin
vita-mksfoex -s TITLE_ID=IM2DG0001 -s APP_VER={VERSION} -d ATTRIBUTE2=12 "Iron Man 2 - Combat Test" /diagnostic/param.sfo
'''
    checks['self']=run_check('self',['docker','run','--rm','--network','none','--user',f'{os.getuid()}:{os.getgid()}',
        '-v',f'{ROOT}:/workspace:ro','-v',f'{out}:/diagnostic','-w','/workspace',IMAGE,'sh','-c',commands],out)
    # A VPK is a standard ZIP; preserve every SDK-produced metadata/SELF byte.
    # Assemble directly to avoid staging or linking proprietary asset directories.
    vpk=out/f'IronMan2_Combat_Test_{VERSION}.vpk';pending=vpk.with_suffix('.vpk.part')
    with zipfile.ZipFile(pending,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        archive.write(out/'param.sfo','sce_sys/param.sfo');archive.write(out/'eboot.bin','eboot.bin')
        for name in sorted(files):archive.write(asset_root/name,name)
    sfo=verify_vpk(pending,files,digest(out/'eboot.bin'))
    require(digest(gates_path)==gates_sha,'Readiness gates changed during packaging')
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==commit and
        not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(),'Source changed during packaging')
    pending.replace(vpk)
    manifest=dict(scope='Explicitly authorized current-source diagnostic; not a finished port',
        source_commit=commit,sdk_image=IMAGE,title_id=TITLE_ID,sfo=sfo,checks=checks,
        elf_sha256=digest(elf),self_sha256=digest(out/'eboot.bin'),vpk_sha256=digest(vpk),
        vpk_bytes=vpk.stat().st_size,resource_count=len(files),resources_sha256=files,
        uploaded_ipa_read=False,original_audio_included=False,native_lighting_verified=False,
        test_opponent={'model':'original Mark IV','original_enemy_ai':False,'prototype_health_and_stationary_sparring':True},
        lighting_mode='experimental current-pose geometric normals using existing G75 policy',
        readiness_gates=json.loads(gates_path.read_text()),device_tested=False)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(digest(vpk)+'  '+vpk.name+'\n')
    print(json.dumps({k:manifest[k] for k in ('source_commit','title_id','vpk_sha256','vpk_bytes','resource_count')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--diagnostic-current-state',action='store_true',required=True,
                   help='Explicit manual scope; never used by automatic CI')
    p.add_argument('--asset-root',type=Path,required=True)
    p.add_argument('--baseline-manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    main(p.parse_args())
