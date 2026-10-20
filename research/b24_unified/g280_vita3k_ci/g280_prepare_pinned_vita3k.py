#!/usr/bin/env python3
"""G280 offline-safe reproducible Vita3K CI bootstrap (not game proof).
Only downloads the official upstream 4206 Linux AppImage to a temp location,
verifies the upstream-published immutable SHA256 before ever executing it,
extracts it without FUSE, and leaves full gameplay disabled by default.
Does NOT download firmware, original iOS IPA, or build any VPK.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

TAG="4206"
UPSTREAM="Vita3K/Vita3K-builds"
ASSET="Vita3K-x86_64.AppImage"
DIGEST="f3e5e93c074237b83f12a1dbd2bd728bf0616cb349a640409ea11499e3e3b001"
API=f"https://api.github.com/repos/{UPSTREAM}/releases/tags/{TAG}"
MAX_BYTES=110*1024*1024

def safe_asset_url(url:str)->bool:
    return (url.startswith(f"https://github.com/{UPSTREAM}/releases/download/{TAG}/")
            and url.endswith("/"+ASSET) and url.count("?")==0)

def choose_release_asset(release:dict)->str:
    if str(release.get("tag_name"))!=TAG:
        raise ValueError("G280 upstream release tag changed; refusing rolling latest")
    hits=[a for a in release.get("assets",[]) if a.get("name")==ASSET]
    if len(hits)!=1 or not safe_asset_url(str(hits[0].get("browser_download_url",""))):
        raise ValueError("G280 exact immutable Vita3K release asset missing/unsafe")
    size=int(hits[0].get("size") or 0)
    if size<8*1024*1024 or size>MAX_BYTES:
        raise ValueError("G280 unexpected upstream AppImage size")
    return hits[0]["browser_download_url"]

def request(url:str)->urllib.request.Request:
    headers={"User-Agent":"IronMan2-Vita-private-G280-CI","Accept":"application/vnd.github+json"}
    token=os.environ.get("GITHUB_TOKEN","")
    if token and url==API: headers["Authorization"]="Bearer "+token
    return urllib.request.Request(url,headers=headers)

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def prepare(dest:Path)->Path:
    dest.mkdir(parents=True,exist_ok=True)
    meta=json.loads(urllib.request.urlopen(request(API),timeout=30).read())
    url=choose_release_asset(meta)
    target=dest/ASSET
    tmp=dest/(ASSET+".partial")
    downloaded=0
    try:
        with urllib.request.urlopen(request(url),timeout=75) as response, tmp.open("wb") as out:
            while block:=response.read(1024*1024):
                downloaded+=len(block)
                if downloaded>MAX_BYTES:
                    raise ValueError("G280 upstream exceeded byte cap")
                out.write(block)
        actual=sha256(tmp)
        if actual!=DIGEST:
            raise ValueError(f"G280 security: pinned official SHA256 mismatch expected={DIGEST} actual={actual}")
        tmp.rename(target)
        target.chmod(0o755)
    finally:
        if tmp.exists():tmp.unlink()
    print(f"G280 verified official Vita3K {TAG} AppImage {downloaded} bytes sha256={DIGEST}",flush=True)
    result=subprocess.run([str(target),"--appimage-extract"],cwd=dest,
        stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=120,check=False)
    app=dest/"squashfs-root"/"AppRun"
    if result.returncode or not app.is_file():
        raise RuntimeError("G280 AppImage extraction failed: "+result.stderr[-1500:])
    app.chmod(app.stat().st_mode|0o111)
    print("G280 extracted AppRun without FUSE. Next: actual CLI smoke, NOT game boot.",flush=True)
    return app

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    app=prepare(args.out.resolve())
    print("G280_EXECUTABLE="+str(app))
    (args.out/"g280_metadata.json").write_text(json.dumps({
        "upstream":UPSTREAM,"release_tag":TAG,"asset_name":ASSET,"expected_sha256":DIGEST,
        "stage":"official binary extracted; firmware/VPK/gameplay untested"
    },indent=2)+"\n")

if __name__=="__main__":
    main()
