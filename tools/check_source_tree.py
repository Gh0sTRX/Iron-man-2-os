#!/usr/bin/env python3
"""Check that the canonical tree is source-only and cannot package a VPK."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
files=list((root/'src').rglob('*'))
assert files
for path in files:
    assert not path.is_symlink(),path
    if path.is_file():
        assert path.suffix in ('.c','.h'),path
        assert path.name not in (
            'b24_g217_AUTHENTIC_original_2010_iOS_source_states_ONLY_NO_VPK.h',
            'b24_g137_mission000_owner_original_generated.c'),path
        data=path.read_bytes()
        assert b'\0' not in data,path
        assert b'drive.google.com/' not in data,path
cmake=(root/'CMakeLists.txt').read_text()
assert 'vita_create_vpk' not in cmake and 'vita_create_self' not in cmake
assert 'work/' not in cmake
for name in re.findall(r'\b(src/[^\s)]+\.c)',(root/'cmake/VitaSources.cmake').read_text()):
    assert (root/name).is_file(),name
print('PASS canonical source-only tree, external original tables, no package target')
