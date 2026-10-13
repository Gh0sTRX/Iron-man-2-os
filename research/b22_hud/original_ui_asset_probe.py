#!/usr/bin/env python3
"""Read-only iOS IPA GUI/SWF candidates. Never exports any copyrighted asset data."""
import argparse
import csv
import json
import re
from pathlib import Path
from zipfile import ZipFile
TOKENS=re.compile(r'(^|[/_.-])(ui|hud|menu|sprite|atlas|font|option|button|flash|swf|upgrade|interface|minimap|icon|pause|tutorial)(?=($|[/_.-]))',re.I)
EXT=('.swf','.gfx','.pvr','.png','.tga','.bmp','.dds','.ktx')
MAGIC={b'FWS':'SWF uncompressed',b'CWS':'SWF zlib',b'ZWS':'SWF LZMA'}
FIELDS=['path','size','category','format','source','offset','confidence']

def plausible_swf(data,i):
    if i+8>len(data) or data[i:i+3] not in MAGIC:return None
    version=data[i+3]
    length=int.from_bytes(data[i+4:i+8],'little')
    if not (4<=version<=40 and 8<=length<=64*1024*1024):return None
    if data[i:i+3]==b'FWS' and i+9<=len(data) and not 1<=data[i+8]>>3<=31:return None
    return dict(format=MAGIC[data[i:i+3]],version=version,length=length)

def probe(ipa):
    result=[]
    with ZipFile(ipa) as z:
        for member in z.infolist():
            if member.is_dir():continue
            path=member.filename
            named=bool(TOKENS.search(path) or path.lower().endswith(EXT))
            with z.open(member) as handle:
                first=handle.read(64)
                if named:
                    result.append(dict(path=path,size=member.file_size,
                         category='named candidate',format='unverified',
                         source='name/extension',offset=0,confidence='low'))
                sig=plausible_swf(first,0)
                if sig:
                    result.append(dict(path=path,size=member.file_size,
                         category='top-level SWF',format=sig['format'],
                         source='SWF header',offset=0,confidence='medium: header only'))
                overlap=b'';absolute=0
                handle.seek(0)
                while True:
                    chunk=handle.read(1024*1024)
                    if not chunk:break
                    sample=overlap+chunk
                    base=absolute-len(overlap)
                    for key in MAGIC:
                        offset=0
                        while True:
                            i=sample.find(key,offset)
                            if i<0:break
                            abs_offset=base+i
                            if abs_offset>0 and plausible_swf(sample,i):
                                result.append(dict(path=path,size=member.file_size,
                                  category='embedded SWF header',format=MAGIC[key],
                                  source='embedded magic/header',offset=abs_offset,
                                  confidence='low: possible nested data/false positive'))
                            offset=i+1
                    absolute+=len(chunk)
                    overlap=sample[-8:]
    return result

def report(ipa,out):
    records=probe(ipa)
    out.mkdir(parents=True,exist_ok=True)
    with (out/'UI_ASSET_CANDIDATES.csv').open('w',newline='',encoding='utf-8-sig') as file:
        writer=csv.DictWriter(file,fieldnames=FIELDS)
        writer.writeheader();writer.writerows(records)
    summary=dict(original_ipa=ipa.name,total_candidates=len(records),
         top_level_swf=sum(x['category']=='top-level SWF' for x in records),
         embedded_swf_headers=sum(x['category']=='embedded SWF header' for x in records),
         warning='Candidates ONLY. Original HUD images/menus are not verified, extracted or decrypted by this tool.')
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ipa',type=Path)
    parser.add_argument('--out',type=Path,default=Path('b22_original_ui_manifest'))
    args=parser.parse_args()
    print(json.dumps(report(args.ipa,args.out),indent=2))
