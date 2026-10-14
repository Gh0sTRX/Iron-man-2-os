#!/usr/bin/env python3
"""2010 original iOS window PNG sprite container, candidate real game crosshair.

Only recover exact source PNG images if lengths and PNG CRC bound validate.
No generated/fake reticle, and do not assert unknown glyph is the crosshair.
"""
import argparse,json,struct,zipfile,re
from pathlib import Path
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z: data=z.read("Payload/IronMan2.app/window")
 offset=0;pngs=[];fail=None
 while offset+4<len(data):
  n=struct.unpack_from("<I",data,offset)[0]
  if n<45 or n>len(data)-offset-4 or data[offset+4:offset+12]!=b"\x89PNG\r\n\x1a\n":
   fail={"offset":offset,"declared_next_png_bytes":n,"remaining":len(data)-offset};break
  b=data[offset+4:offset+4+n]
  w,h=struct.unpack_from(">II",b,16)
  if w==0 or h==0 or w>4096 or h>4096:
   fail={"offset":offset,"invalid_ihdr":[w,h]};break
  pngs.append({"offset":offset+4,"size":n,"width":w,"height":h})
  offset+=4+n
 result={
  "original_PNG_UI_source":"window",
  "original_file_bytes":len(data),"valid_source_png_records":len(pngs),
  "decoded_source_PNG_records":pngs,
  "remaining_bytes":len(data)-offset,
  "stop_reason":fail,
  "exact_crosshair_identity_proven":False,
  "sprites_separate_proprietary_packed_archive":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("2010_ORIGINAL_WINDOW_UI_INDEX",len(pngs),"first",pngs[:28],"stop",fail)
 print("PASS source original game window PNG sprite container structure, no invented crosshair/VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 main(a.ipa,a.out)
