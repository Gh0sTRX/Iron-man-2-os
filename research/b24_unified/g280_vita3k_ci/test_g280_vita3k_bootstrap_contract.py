#!/usr/bin/env python3
"""Dependency-free deterministic tests of G280 pin, URL and integrity gate."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
spec=importlib.util.spec_from_file_location("g280",
    Path(__file__).with_name("g280_prepare_pinned_vita3k.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
GOOD=f"https://github.com/{m.UPSTREAM}/releases/download/{m.TAG}/{m.ASSET}"
payload={"tag_name":m.TAG,"assets":[
    {"name":m.ASSET,"size":75*1024*1024,"browser_download_url":GOOD}
]}
assert m.choose_release_asset(payload)==GOOD
assert m.safe_asset_url(GOOD)
bad_links=[
    GOOD+"?token=bad",
    GOOD+".exe",
    GOOD.replace("github.com","evilgithub.com"),
    GOOD.replace("/4206/","/continuous/"),
    GOOD.replace("/Vita3K/Vita3K-builds/","/Other/Other/"),
    "file:///etc/passwd"
]
for url in bad_links:
    assert not m.safe_asset_url(url),url
for broken in [
    {**payload,"tag_name":"newer"},
    {**payload,"assets":[]},
    {**payload,"assets":[payload["assets"][0],payload["assets"][0]]},
    {**payload,"assets":[{**payload["assets"][0],"size":1}]},
    {**payload,"assets":[{**payload["assets"][0],"size":m.MAX_BYTES+1}]}
]:
    try:m.choose_release_asset(broken)
    except ValueError:pass
    else:raise AssertionError("G280 accepted drifted release metadata")
with TemporaryDirectory() as t:
    p=Path(t)/"fake-not-an-executable"
    p.write_bytes(b"do-not-run-anything")
    assert len(m.sha256(p))==64 and m.sha256(p)!=m.DIGEST
print("G280 PASS pinned upstream release metadata/URL/name/size/hash smoke guards; no firmware, no VPK")
