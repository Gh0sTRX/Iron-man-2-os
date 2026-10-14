#!/usr/bin/env python3
"""2010 Iron Man 2 iOS original HEIGHTMAPS / CLEV / STATES source inventory.
Investigate ACTUAL C1L1 per-point collision/terrain data, no guessing,
no extracting private package wholesale and no new playable claims.
"""
import argparse,collections,hashlib,json,re,struct,zipfile,zlib
from pathlib import Path
from b24_owner_pack_extract import decode
INPUTS=("heightmaps","clev","states","demodata","window","sprites")
def inspect(data,label):
 result={"owner_pack":label,"bytes":len(data),
         "sha256":hashlib.sha256(data).hexdigest(),
         "magic_hex":data[:48].hex(),
         "first_16_le_u32":[struct.unpack_from("<I",data,i)[0]
                            for i in range(0,min(len(data)-3,64),4)],
         "original_resource_pack_valid":False,
         "named_resources":[]}
 try:
  rows=decode(data)
  result["original_resource_pack_valid"]=True
  for r in rows:
   raw=data[r.start:r.end]
   result["named_resources"].append({
    "source_name":r.name,"length":len(raw),
    "first24":raw[:24].hex(),
    "possible_bres":raw[:4]==b"BRES",
    "candidate_first_u32s":[struct.unpack_from("<I",raw,i)[0]
                  for i in range(0,min(len(raw)-3,16),4)]})
 except Exception as e:
  result["index_error"]=str(e)
  samples=set(m.group(0).decode("ascii","replace")
               for m in re.finditer(rb"[ -~]{6,84}",data))
  result["ascii_label_candidates"]=[
    s for s in sorted(samples)
    if any(t in s.casefold() for t in ("c1l1","height","ground",
       "world","chapter","terrain","expo","city","map"))][:80]
  for name,magic in (("zlib_78_9c",b"\x78\x9c"),("zlib_78_da",b"\x78\xda"),
         ("gzip",b"\x1f\x8b"),("bzip2",b"BZh"),("lz4",b"\x04\x22\x4d\x18")):
   if data[:len(magic)]==magic:result["compression_magic_candidate"]=name
 return result

def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  vals={name:inspect(z.read("Payload/IronMan2.app/"+name),name) for name in INPUTS}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(vals,indent=2)+"\n")
 for name,v in vals.items():
  print("ORIGINAL2010_RAW_SCENE_RESOURCE",name,"bytes",v["bytes"],
        "header",v["magic_hex"][:80],
        "pack_valid",v["original_resource_pack_valid"],
        "entries",len(v["named_resources"]),"decode_error",v.get("index_error"))
  print("ORIGINAL2010_GAME_SCENE_NAMED_RESOURCES",name,v["named_resources"][:100])
  print("ORIGINAL2010_GAME_SCENE_ASCII_LABELS",name,
        v.get("ascii_label_candidates",[])[:30])
 print("PASS original 2010 iOS heightmaps and C1L1 scene config forensic metadata, no VPK/no invented floor")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 main(a.ipa,a.out)
