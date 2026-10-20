#!/usr/bin/env python3
"""G280 validates VPK contract against fabricated ZIP only (NO game/VPK file).
Test the legacy source archive admission without a VitaSDK build.
"""
import importlib.util
from pathlib import Path
import tempfile
import zipfile

spec=importlib.util.spec_from_file_location("g280_vpk",
    Path(__file__).with_name("g280_existing_vpk_optional_probe.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fake_zip(path:Path,entries):
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_STORED) as z:
        for name,contents in entries:
            z.writestr(name,contents)

with tempfile.TemporaryDirectory() as t:
    p=Path(t)/"fake-test-only.zip"
    e=[("eboot.bin",b"NOT A REAL EBOOT"),("sce_sys/param.sfo",b"FAKE IM2G16101 SFO")]
    fake_zip(p,e)
    out=m.validate_old_vpk(p)
    assert out["title_id"]=="IM2G16101" and out["files"]==2
    for evil in (
        [("eboot.bin",b"a"),("sce_sys/param.sfo",b"Wrong title!")],
        [("sce_sys/param.sfo",b"IM2G16101")],
        e+[("../escape.txt",b"do not extract")],
        e+[("a\\b",b"windows path")],
        e+[("/absolute",b"out of bounds")],
        e+[("eboot.bin",b"duplication")]
    ):
        fake_zip(p,evil)
        try:m.validate_old_vpk(p)
        except ValueError:pass
        else:raise AssertionError("G280 accepted unsafe/non-G161 historic archive")
print("G280 PASS synthetic-only 2010 owner archived-VPK validation (paths/title/CRC/member constraints); NO NEW VPK")
