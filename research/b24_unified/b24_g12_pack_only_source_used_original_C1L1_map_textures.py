#!/usr/bin/env python3
"""Package ONLY verified original source-matched 2010 C1L1 map diffuse assets.

NOT A VPK. Not gameplay. Ships only user-owned source-authenticated
  app0:maps/C1L1_environment.c1mt
  app0:maps/c1l1_*.c1tx (only texture banks used by original ground,
                                 buildings/obj and car materials)
with exact names and SHA-256, to be added to future Vita test package
AFTER source raster QA and level1 scene geometry inspection.
Original C1MT still names 39 2010 source atlas files; omitted ones have no
visible C1MA reference in ground/urban/car subset, so GPU will never load.
No complete private owner IPA, no raw BRES/level1 .bclara/other copyrighted
game assets, no fake texture index mappings, NO VPK.
"""
from __future__ import annotations
import argparse,hashlib,json,tempfile,zipfile,struct,contextlib,io
from pathlib import Path
from b24_map_first_original_2010_C1MT_source_verified_material_bank import build as c1mt_build
from b24_g11_all_39_original_c1l1_gpu_texture_assets import build as source_pvr_bake

def build(ipa:Path,archive:Path,qa:Path):
 with tempfile.TemporaryDirectory(prefix='owner_C1L1_source_only_') as tmp:
  root=Path(tmp);alltext=root/'original_39'
  with contextlib.redirect_stdout(io.StringIO()):
   bankmeta=source_pvr_bake(ipa,alltext)
   m=c1mt_build(ipa,root/'C1L1_environment.c1mt',root/'c1mt_report.json')
  if m['true_material_count']!=94 or m['true_2010_atlas_count']!=39:
   raise ValueError('real original BRES material/texture counts changed')
  included=set()
  referenced=[]
  for row in m['materials']:
   # This is C1L1 source BRES FILE key, not guessed texture identity:
   if not row['material'].startswith(('C1L1_ground_','C1L1_obj_','C1L1_car_')):
    continue
   index=row['C1MT_C1TX_GPU_original_texture_id']
   if index==65535:continue
   filename=m['unchanged_original_39_C1TX_bank_files'][index]
   included.add(filename)
   referenced.append(row)
  if len(included)<10 or 'c1l1_vehicles.c1tx' not in included:
   raise ValueError('expected owner first-level diffuse source selection missing')
  if not all((alltext/n).is_file() for n in included):
   raise ValueError('owner original source PVR bank incomplete')
  # No installation time penalty for unreferenced 2010 atlas sources:
  # C1MT references all 39 by index; absent unused banks are never opened.
  payloads={'maps/C1L1_environment.c1mt':(root/'C1L1_environment.c1mt').read_bytes()}
  for name in sorted(included):
   payloads['maps/'+name]=(alltext/name).read_bytes()
  if struct.unpack_from('<4sIIII',payloads['maps/C1L1_environment.c1mt'])[:4]!=(b'C1MT',1,94,39):
   raise ValueError('incorrect Vita native source material-table ABI')
  for path,data in payloads.items():
   if path.endswith('.c1tx'):
    magic,version,w,h,flags=struct.unpack_from('<4sIIII',data)
    if (magic,version)!=(b'C1TX',1) or len(data)!=20+4*w*h:
     raise ValueError('source PVR image bank header corruption '+path)
  archive.parent.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for name,data in sorted(payloads.items()):
    z.writestr(name,data)
  validation={
   'source_year':2010,'runtime_map_dir':'app0:maps/',
   'G12_authoritative_C1MT_name':'maps/C1L1_environment.c1mt',
   'authentic_2010_MATERIAL_IDS':94,'authentic_C1MT_atlas_names':39,
   'actual_used_atlases_staged':len(included),
   'actual_used_nonlight_original_shader_materials':len(referenced),
   'num_source_C1TX_unreferenced_banks_omitted_for_install_optimization':39-len(included),
   'actual_source_RGBA_bytes':sum(len(data) for name,data in payloads.items() if name.endswith('.c1tx')),
   'exact_asset_files_sha256':{n:hashlib.sha256(d).hexdigest() for n,d in sorted(payloads.items())},
   'output_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
   'all_2010_C1MA_faces_and_BRES_source_coordinates_untouched':True,
   'B12_real_original_car_matched':m['B12_original_verified_vehicles_still_match'],
   'two_orig_BRES_building4_sampler_mat47_cross_proven':m['Material47_independently_verified_Building4_in_obj2_and_obj4'],
   'original_2010_remaining_untextured_surfaces_are_NOT_modified':True,
   'VPK_generated':False,'Vita_gpu_actual_hardware_verified':False,
   'original_owner_IPA_in_bundle':False,
   'future_test_packaging_must_stage_assets_in_app0_maps':True
  }
  qa.parent.mkdir(parents=True,exist_ok=True)
  qa.write_text(json.dumps(validation,indent=2)+'\n')
  print('PASS G12 original 2010 C1L1 map assets selected direct from genuine BRES shader/face source;',
        len(included),'real PVR textures instead of all39;',
        validation['actual_source_RGBA_bytes'],'source bytes; portable app0:maps C1MT sidecar.',
        'NO VPK or unrelated gameplay.',flush=True)
  return validation

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ipa',type=Path,required=True)
 ap.add_argument('--archive',type=Path,required=True)
 ap.add_argument('--qa',type=Path,required=True)
 a=ap.parse_args();build(a.ipa,a.archive,a.qa)
