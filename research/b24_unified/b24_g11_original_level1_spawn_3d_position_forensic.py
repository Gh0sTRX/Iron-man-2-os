#!/usr/bin/env python3
"""Real 2010 level1.bclara original first-mission SpawnPoint and Position bytes.

Exact owner CLEV level1 source. BCLARA format not independently specified;
this is constrained forensic research, NOT claiming a guessed float triple is
the original authored starting coordinate or writing it to the runtime.
"""
import argparse,collections,hashlib,json,math,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
def f32(raw,off):
 try:return struct.unpack_from('<f',raw,off)[0]
 except struct.error:return float('nan')
def legit(a):
 return all(math.isfinite(f) and abs(f)<2000 for f in a) and (
      sum(abs(f)>=.1 for f in a)>=2 and sum(abs(f)>=5 for f in a)>=1)
def context(raw,off,radius=192):
 start=max(0,off-radius);end=min(len(raw),off+radius)
 snippet=raw[start:end]
 ascii=''.join(chr(c) if 32<=c<127 else '.' for c in snippet)
 return {"offset":off,"span_start":start,"span_end":end,
          "author_bytes_hex":snippet.hex(),
          "ascii_with_nonprintables_as_period":ascii}
def float_near(raw,off,radius=192):
 c=[]
 for k in range(max(0,off-radius),min(len(raw)-12,off+radius),4):
  xyz=struct.unpack_from('<fff',raw,k)
  if legit(xyz):
   c.append({"offset":k,"offset_delta_from_name":k-off,
             "potential_xyz":list(round(v,5) for v in xyz),
             "semantics_verified":False})
 return c[:90]
def parse(raw):
 found=[]
 for match in re.finditer(rb'SpawnPoint(?:[0-9_]{0,14})|Position\x00|UseDefaultGPMaterials\x00|NodeMaterials\x00',raw):
  if len(found)>200:break
  s=match.group(0).decode('latin1')
  loc=match.start()
  nearfloat=float_near(raw,loc,128) if 'SpawnPoint' in s else []
  found.append({"name":s,"byte_offset":loc,
                "context":context(raw,loc,120) if 'SpawnPoint' in s else None,
                "float3_near_event":nearfloat})
 byname=collections.Counter(x["name"] for x in found)
 return {"original_size":len(raw),"source_sha256":hashlib.sha256(raw).hexdigest(),
         "field_name_frequency":dict(byname),
         "spawnpoint_and_position_source_records":found,
         "spawnpoint_count":sum('SpawnPoint' in x["name"] for x in found),
         "startup_position_confirmed":False,
         "notes":"BCLARA field names and nearby floats are not a decoded coordinate/property link."}
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  clev=z.read('Payload/IronMan2.app/clev')
  level=get_exact(clev,decode(clev,'.bclara'),'level1.bclara')
 r=parse(level)
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(r,indent=2)+'\n')
 print("G11_AUTHENTIC_2010_LEVEL1_SPAWN_FIELDS",r["field_name_frequency"])
 for x in r['spawnpoint_and_position_source_records']:
  if 'SpawnPoint' in x['name']:
   print('G11_2010_REAL_MISSION_SPAWN_NAME',x['name'],'fileoff',x['byte_offset'],
         'nearby_plausible_triples',x['float3_near_event'][:40])
 print("PASS G11 original level1 scene exact SpawnPoint and authored property search; no forged enemy coordinates")
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 main(a.ipa,a.out)
