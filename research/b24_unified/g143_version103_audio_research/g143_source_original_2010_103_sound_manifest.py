#!/usr/bin/env python3
"""G143 inspect ACTUAL owner Iron Man 2 iOS v1.0.3 independently of
Google Drive connected 256 MiB raw streaming limit. Callable in a GH
runner if Drive public gdown works. Original 1.0.0 optional audio SHA
baseline can be provided separately; NEVER assert same versions without it.
NO ROM/IPA/WWW binary copied to GitHub artifacts. NO VPK.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from collections import Counter
def scan(ipa):
 if ipa.stat().st_size not in (248613763,275580565):
  raise ValueError("Unknown original iOS IPA size; refuse mislabeled version")
 with zipfile.ZipFile(ipa) as z:
  rows=[]
  for zi in z.infolist():
   if not zi.filename.startswith('Payload/IronMan2.app/') or not zi.filename.endswith('.www'):
    continue
   name=zi.filename.split('/')[-1]
   raw=z.read(zi)
   if len(raw)<44 or raw[:4]!=b'RIFF' or raw[8:12]!=b'WAVE':
    raise ValueError(f'original WAV not RIFF {name}')
   pos=12;fmt=None;data=None
   while pos+8<=len(raw):
    key=raw[pos:pos+4];n=struct.unpack_from('<I',raw,pos+4)[0];pos+=8
    if pos+n>len(raw):raise ValueError(f'wave overflow {name}')
    if key==b'fmt ':
     if n<16:raise ValueError('short fmt')
     fmt=struct.unpack_from('<HHIIHH',raw,pos)
    if key==b'data':data=n
    pos+=n+(n&1)
   if fmt is None or data is None:raise ValueError('missing real WAV fmt/data '+name)
   tag,ch,hz,rate,align,bits=fmt
   rows.append({'filename':name,'sha256':hashlib.sha256(raw).hexdigest(),
    'bytes':len(raw),'codec':tag,'channels':ch,'hz':hz,'bits':bits,
    'compressed_in_ipa':zi.compress_size})
 return rows
def run(args):
 out=args.out;out.parent.mkdir(parents=True,exist_ok=True)
 newer=scan(args.v103)
 if len(newer)<800:raise ValueError('Original 1.0.3 file not expected complete audio')
 category=Counter(n.split('_',1)[0] for n in (z['filename'] for z in newer))
 report={
 'original_owner_iOS_version_1_0_3_size':args.v103.stat().st_size,
 'full_1_0_3_WWW_RIFF_count':len(newer),
 'categories_1_0_3':dict(category),
 'version_1_0_3_raw_audio_sha256_filename_manifest':newer,
 'v1_0_0_full_audio_comparison_status':'not attempted (optional authentic baseline missing)',
 'full_v1_0_3_IPA_distributed':False,'raw_audio_1_0_3_distributed':False,
 'VPK_created':False}
 if args.v100:
  prior=scan(args.v100)
  a={r['filename']:r['sha256'] for r in prior}
  bb={r['filename']:r['sha256'] for r in newer}
  both=a.keys()&bb.keys()
  report['v1_0_0_full_audio_comparison_status']='true original owner two-IPAs compared WAV by filename and SHA256'
  report['v1_0_0_vs_1_0_3_original_WAV_differences']={
   'base_count':len(a),'new_count':len(bb),
   'unchanged_count':sum(a[n]==bb[n] for n in both),
   'modified_count':sum(a[n]!=bb[n] for n in both),
   'added_names':sorted(bb.keys()-a.keys()),
   'removed_names':sorted(a.keys()-bb.keys()),
   'modified_names':sorted(n for n in both if a[n]!=bb[n])}
 print('G143 source 1.0.3 genuine RIFF 803+ WAVE',len(newer),dict(category))
 print('G143 version comparison:',report['v1_0_0_full_audio_comparison_status'])
 if 'v1_0_0_vs_1_0_3_original_WAV_differences' in report:
  print(json.dumps(report['v1_0_0_vs_1_0_3_original_WAV_differences'],indent=2))
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--v103',type=Path,required=True)
 p.add_argument('--v100',type=Path);p.add_argument('--out',type=Path,required=True)
 run(p.parse_args())
