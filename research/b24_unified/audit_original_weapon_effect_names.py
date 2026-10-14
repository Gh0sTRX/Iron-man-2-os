#!/usr/bin/env python3
"""Grounded source-name inventory for genuine 2010 iOS combat animation / FX.
Reads only owner-supplied IPA, never makes names or textures up.
A matching name is NOT proof of a usable renderer asset/weapon effect rig.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode
WEAPON=re.compile(r"beam|repuls|unibeam|missil|rocket|proj|explos|pulse|blaster|shot|muzzle|effect|spark|shell|tracer|gun|cannon|laser",re.I)
MOTION=re.compile(r"iron.?man.*(aim|ground.?att|fly.?att|beam|fire|combo)|warmachine.*(aim|fly.?att|ground.?att|gun)|underwater.*(att|aim|swim)",re.I)
def run(ipa:Path,out:Path):
 summary={}
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner IPA CRC error")
  for kind,ext in (("models",".bdae"),("textures",".tga"),("anims",".anim")):
   raw=z.read("Payload/IronMan2.app/"+kind)
   records=decode(raw,ext)
   hits=[{"name":e.name,"bytes":e.end-e.start} for e in records
         if WEAPON.search(e.name) or kind=="anims" and MOTION.search(e.name)]
   summary[kind]={"total_records":len(records),"matching_count":len(hits),"matches":hits}
   print("ORIGINAL_2010",kind,"records",len(records),"specific weapon/animation candidates",len(hits))
   for x in hits[:110]:print("ORIGINAL_ASSET_NAME",kind,x["name"],x["bytes"])
  # Non-pattern checks for prohibited fabrication: archive names strictly.
  assert summary["anims"]["total_records"]==972
  assert summary["models"]["total_records"]==207
  assert summary["textures"]["total_records"]==412
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"note":"Names only; no proven particle GPU implementation, source rig sockets or gameplay enemies",
                             "assets":summary},indent=2,ensure_ascii=False)+"\n")
 print("PASS true original owner iOS source combat names recovered; no false animation functionality claim")
 return summary
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--manifest",type=Path,required=True)
 a=p.parse_args();run(a.ipa,a.manifest)
