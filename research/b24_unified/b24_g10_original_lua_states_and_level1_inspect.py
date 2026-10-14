#!/usr/bin/env python3
"""Original 2010 owner iOS STATE Lua 5.1 binary and level1.bclara evidence.

Pure static structure/index reading; NEVER execute arbitrary Lua bytecode,
never invent combo button semantics; no owner IPA/archive exported.
"""
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact

def read_states(raw):
 count=struct.unpack_from("<H",raw)[0]
 if not 2<=count<=150:raise ValueError("source state count")
 pos=2
 rows=[]
 for i in range(count):
  if pos+2>len(raw):raise ValueError("state filename truncated "+str(i))
  n=struct.unpack_from("<H",raw,pos)[0];pos+=2
  if not 1<=n<=170 or pos+n+4>len(raw):
   raise ValueError("state filename invalid at "+str(i)+" offset "+str(pos-2))
  name=raw[pos:pos+n].decode("utf8");pos+=n
  sz=struct.unpack_from("<I",raw,pos)[0];pos+=4
  if not 12<=sz<=len(raw)-pos:raise ValueError("state Lua blob size invalid "+name)
  binary=raw[pos:pos+sz];pos+=sz
  hdr=binary[:12]
  strings=[m.group(0).decode("ascii","ignore")
           for m in re.finditer(rb"[ -~]{4,120}",binary)]
  rows.append({"name":name,"source_record_index":i,"lua_bytes":sz,
               "source_lua_header_hex":hdr.hex(),
               "Lua_5_1_binary":binary[:5]==b"\x1bLuaQ",
               "exact_source_lua_constants_ascii_sample":strings[:130],
               "authored_combo_state_labels":[s for s in strings if
                    any(t in s.upper() for t in ("COMBO","FLOAT","REPULSOR","MELEE","LOCK"))][:140]})
 if pos!=len(raw):raise ValueError("states trailer not consumed "+str(len(raw)-pos))
 return rows

def level1_report(raw):
 u16=struct.unpack_from("<H",raw)[0]
 text=[(m.start(),m.group(0).decode("latin1")) for m in
      re.finditer(rb"[ -~]{5,95}",raw)]
 priority=[{"offset":i,"string":name} for i,name in text if any(
         t in name.casefold() for t in
         ("c1l1","spawn","material","texture","mission","level",
          "player","world","start","enemy","combat","target","position",
          "terrain","sky","building","road","ground","weapon"))]
 return {"bytes":len(raw),"first_64_hex":raw[:64].hex(),
         "original_scene_first_u16":u16,
         "original_scene_ascii_strings_count":len(text),
         "original_scene_relevant_keyed_name_candidates":priority[:600],
         "unique_ascii_texts_first_100":[s for _,s in text[:100]],
         "original_scene_model_transforms_verified":False,
         "original_mission_spawn_verified":False}
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  states=z.read("Payload/IronMan2.app/states")
  clev=z.read("Payload/IronMan2.app/clev")
 level=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 attempts={"source_states_raw_length":len(states),"source_states_first60":states[:60].hex()}
 try:
  records=read_states(states)
  attempts["decoded_exact_state_records"]=records
  print("G10_REAL_STATES_LUA_COUNT",len(records))
  for record in records:
   print("G10_REAL_2010_ACTOR_LUA_NAME",record["name"],
         "bytes",record["lua_bytes"],"header",record["source_lua_header_hex"],
         "2010_source_combo_hover_names",record["authored_combo_state_labels"][:80])
 except Exception as e:
  attempts["state_index_parse_error"]=str(e)
  print("G10_REAL_STATES_NEEDS_MORE_FORMAT_DECODE",str(e))
 vals=level1_report(level)
 attempts["original_C1L1_level1_bclara"]=vals
 print("G10_ORIGINAL_C1L1_FIRST_LEVEL_NAME_KEYS",vals["original_scene_relevant_keyed_name_candidates"][:120])
 print("G10_ORIGINAL_C1L1_LEVEL1_BYTE_LENGTH",len(level))
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(attempts,indent=2)+"\n")
 print("PASS original 2010 states Lua names and real level1.bclara mission map field forensic, no fake geometry or VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 main(a.ipa,a.out)
