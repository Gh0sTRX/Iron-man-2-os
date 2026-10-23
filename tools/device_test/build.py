#!/usr/bin/env python3
"""Package the user-authorized current-state device diagnostic, never a release."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work'
OUT = WORK / 'device-test'
IMAGE = 'vitasdk/vitasdk@sha256:8227da1b596d981f4513cd9b36bda1e43857f6dae5bcf4312c1cd40167f7d9bb'
TITLE_ID = 'IM2DG0001'
VPK = OUT / 'IronMan2_Current_Device_Test.vpk'
RESOURCES = ('models', 'animations', 'maps', 'assets')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sfo_strings(data):
    magic, version, keys, values, count = struct.unpack_from('<5I', data)
    assert magic == 0x46535000, 'Invalid SFO'
    result = {}
    for i in range(count):
        key, fmt, size, capacity, offset = struct.unpack_from('<HHIII', data, 20 + i * 16)
        name = data[keys + key:].split(b'\0', 1)[0].decode()
        if fmt == 0x204:
            result[name] = data[values + offset:values + offset + size].rstrip(b'\0').decode()
    return result


def main():
    OUT.mkdir(exist_ok=True)
    elf = WORK / 'build-G171-ELF-ONLY/im2_beta'
    assert elf.read_bytes()[:4] == b'\x7fELF'
    files = {}
    for directory in RESOURCES:
        paths = sorted((WORK / directory).rglob('*'))
        assert paths, directory
        for path in paths:
            assert not path.is_symlink(), path
            if path.is_file():
                files[path.relative_to(WORK).as_posix()] = digest(path.read_bytes())
    for required in ('assets/G66_city.g66m', 'assets/G66_original_collision.g66c',
                     'assets/G73_original_sky_mesh.g73m', 'maps/C1L1_Vehicles.c1tx'):
        assert required in files, required
    assert sum(name.startswith('models/') for name in files) == 5
    commands = '''set -eu
vita-elf-create work/build-G171-ELF-ONLY/im2_beta work/device-test/im2_beta.velf
vita-make-fself -c -s work/device-test/im2_beta.velf work/device-test/eboot.bin
vita-mksfoex -s TITLE_ID=IM2DG0001 -s APP_VER=00.01 -d ATTRIBUTE2=12 "Iron Man 2 - Device Test" work/device-test/param.sfo
vita-pack-vpk -s work/device-test/param.sfo -b work/device-test/eboot.bin -a work/models=models -a work/animations=animations -a work/maps=maps -a work/assets=assets work/device-test/IronMan2_Current_Device_Test.vpk
'''
    subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--user',
                    f'{__import__("os").getuid()}:{__import__("os").getgid()}',
                    '-v', f'{ROOT}:/workspace', '-w', '/workspace', IMAGE,
                    'sh', '-c', commands], check=True)
    with zipfile.ZipFile(VPK) as archive:
        assert archive.testzip() is None, 'CRC failure'
        names = archive.namelist()
        assert len(names) == len(set(names)), 'Duplicate entries'
        actual_files = {n for n in names if not n.endswith('/')}
        assert actual_files == set(files) | {'sce_sys/param.sfo', 'eboot.bin'}, 'Unexpected/missing payload'
        for name in names:
            assert not name.startswith('/') and '..' not in Path(name).parts, name
        for name, expected in files.items():
            assert digest(archive.read(name)) == expected, name
        assert archive.read('eboot.bin')[:4] == b'SCE\0', 'Invalid SELF'
        sfo = sfo_strings(archive.read('sce_sys/param.sfo'))
        assert sfo['TITLE_ID'] == TITLE_ID and sfo['APP_VER'] == '00.01', sfo
    manifest = {
        'scope': 'User-authorized current-state device diagnostic; not full port acceptance',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'sdk_image': IMAGE, 'title_id': TITLE_ID, 'sfo': sfo,
        'elf_sha256': digest(elf.read_bytes()), 'vpk_sha256': digest(VPK.read_bytes()),
        'vpk_bytes': VPK.stat().st_size, 'resource_count': len(files),
        'resources_sha256': files,
        'readiness_gates': json.loads((ROOT / 'research/b24_unified/g255_single_integrated_VPK_acceptance_gate/SOURCE_PRE_VPK_READINESS.json').read_text()),
        'device_tested': False,
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: manifest[k] for k in ('title_id', 'vpk_sha256', 'vpk_bytes', 'resource_count')}, indent=2))


if __name__ == '__main__':
    main()
