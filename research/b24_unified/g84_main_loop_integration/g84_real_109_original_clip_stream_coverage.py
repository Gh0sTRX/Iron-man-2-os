#!/usr/bin/env python3
"""G84 check whether EVERY G83 authored movement/aim/flight clip is
ACTUALLY packaged as an original-source IM2V in reconstructed old G9
work/animations, not merely named in the 2010 anim catalog.
Source-only, no VPK, no packing/distribution of proprietary original files.
"""
import argparse,json,re
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--routing-c',required=True,type=Path)
 p.add_argument('--animation-dir',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 args=p.parse_args()
 if not args.animation_dir.is_dir():raise FileNotFoundError(args.animation_dir)
 stem=set(re.findall(r'"((?:ironman|warmachine)_(?:ironman|warmachine)_[a-z0-9_]+)"',
                      args.routing_c.read_text()))
 assert len(stem)==109,('G83 source clip registry drift',len(stem))
 assets=list(args.animation_dir.glob('*.im2v'))
 available={f.stem.casefold() for f in assets}
 missing=sorted(stem-available)
 present=sorted(stem&available)
 report={'2010_original_B18_verified_explicit_G83_109_source_clip_names':len(stem),
  'all_current_G9_IM2V_file_count':len(assets),
  'actual_original_2010_G83_clip_present_count':len(present),
  'source_assets_missing_from_G9_work_animations':missing,
  'present_original_G83_clip_stems':present,
  'user_gameplay_combat_fully_restored':False,
  'new_VPK_generated':False}
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(report,indent=2)+'\n')
 print('G84 genuine original routed clip coverage',len(present),'of',len(stem),
       'available asset streams',len(assets),'missing',len(missing))
 for v in missing:print('MISSING ORIGINAL IM2V STREAM:',v)
 print('Source audit only, no Vita binary or VPK')
 if missing:raise SystemExit('G84 missing actual stream sources; source-only release gate remains blocked')
if __name__=='__main__':main()
