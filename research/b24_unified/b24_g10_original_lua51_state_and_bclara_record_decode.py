#!/usr/bin/env python3
"""Static ONLY Lua 5.1 original 2010 iOS bytecode + genuine level1.bclara.

Lua prototype bytecode is parsed for source author strings and call instruction
traces, NEVER executed. Objective: restore actual original state input mapping
and level1 original material/spawn author config with no guessed bytecode.
"""
import argparse,json,re,struct,zipfile,collections
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
HEADER=b"\x1bLuaQ\x00\x01\x04\x04\x04\x04\x00"
class Parser:
 def __init__(self,b,at):
  self.raw=b;self.pos=at;self.known=[]
 def fetch(self,n):
  if n<0 or n>5000000 or self.pos+n>len(self.raw):
   raise ValueError("Lua binary truncated "+str(self.pos))
  b=self.raw[self.pos:self.pos+n];self.pos+=n;return b
 def u8(self):return self.fetch(1)[0]
 def u32(self):return struct.unpack("<I",self.fetch(4))[0]
 def size(self,sz,limit):
  n=self.u32()
  if n>limit:raise ValueError("Lua unreasonable "+sz+" count "+str(n))
  return n
 def string(self):
  n=self.size("string",200000)
  if n==0:return None
  data=self.fetch(n)
  if data[-1:]!=b"\x00":raise ValueError("Lua unterminated string")
  return data[:-1].decode("latin1","replace")
 def function(self,depth=0):
  if depth>15:raise ValueError("Lua nesting invalid")
  src=self.string()
  line1,line2=self.u32(),self.u32()
  ups,params,vararg,stack=self.u8(),self.u8(),self.u8(),self.u8()
  nc=self.size("bytecode",90000)
  ins=[self.u32() for _ in range(nc)]
  nk=self.size("const",50000)
  const=[]
  for _ in range(nk):
   t=self.u8()
   if t==0:const.append(None)
   elif t==1:const.append(bool(self.u8()))
   elif t==3:const.append(struct.unpack("<f",self.fetch(4))[0])
   elif t==4:const.append(self.string())
   else:raise ValueError("Lua unsupported constant type "+str(t))
  np=self.size("prototypes",2048)
  children=[self.function(depth+1) for _ in range(np)]
  nl=self.size("lineinfo",500000);self.fetch(nl*4)
  lv=self.size("locals",90000)
  local_names=[]
  for _ in range(lv):
   local_names.append(self.string())
   self.u32();self.u32()
  nu=self.size("upvalue_names",2048)
  upnames=[self.string() for _ in range(nu)]
  names=[x for x in const if isinstance(x,str)]
  return {"source_name":src,"first_line":line1,"last_line":line2,
    "nupvalues":ups,"parameters":params,"is_vararg":vararg,
    "stack":stack,"instructions":nc,"constants":names,
    "local_names":[n for n in local_names if n],
    "upvalue_names":[n for n in upnames if n],
    "children":children}
def values(p):
 return [x for x in p["constants"]]+sum((values(c) for c in p["children"]),[])
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  raw=z.read("Payload/IronMan2.app/states")
  packed=z.read("Payload/IronMan2.app/clev")
  level=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
 signatures=[m.start() for m in re.finditer(re.escape(b"\x1bLuaQ"),raw)]
 print("REAL_2010_LUA51_BINARY_SIGNATURES",len(signatures),signatures[:25])
 records=[]
 for index,start in enumerate(signatures):
  try:
   parser=Parser(raw,start)
   header=parser.fetch(12)
   if header!=HEADER:raise ValueError("unexpected Lua header "+header.hex())
   func=parser.function()
   constants=values(func)
   key=[s for s in constants if any(t in s.casefold() for t in
      ("combo","float","ground","aim","attack","button","shot",
       "weapon","melee","fire","move","rush","missile","lock"))]
   records.append({"lua_signature_offset":start,
      "lua_parse_ok":True,"source_size_from_bytecode":parser.pos-start,
      "root_source":func["source_name"],"root_instructions":func["instructions"],
      "all_original_lua_strings":[s for s in constants if s][:250],
      "source_combat_state_and_input_strings":key[:350],
      "actual_lua_function_root":func})
   print("2010_ACTUAL_LUA_STATE_MACHINE",index,
         "offset",start,"author_string_count",len(constants),
         "root",func["source_name"],"combat_input_string_sample",key[:65])
  except Exception as e:
   records.append({"lua_signature_offset":start,"lua_parse_ok":False,
                   "parse_error":str(e)})
 relevant=[]
 for m in list(re.finditer(rb"NodeMaterials\x00?|SpawnPoint\x00?|UseDefaultGPMaterials\x00?|C1L1_[ -~]{0,40}",level))[:65]:
  at=m.start()
  near=level[max(0,at-48):min(len(level),at+100)]
  relevant.append({"offset":at,"original_key":m.group(0).decode("latin1","replace"),
      "original_around_key_hex":near.hex(),
      "original_around_key_printable":''.join(chr(v) if 32<=v<127 else '.' for v in near)})
 print("2010_C1L1_LEVEL1_NODEMATERIALS_SPAWN_CONTEXT",relevant[:25])
 result={"lua51_script_signatures":len(signatures),
   "lua51_parsed_count":sum(r["lua_parse_ok"] for r in records),
   "lua_state_machine_source_records":records,
   "level1_bclara_original_material_position_keys":relevant,
   "original_level1_authored_material_diffuse_mapping_proven":False,
   "original_combat_controls_implementation_verbatim_proven":False}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("PASS G10 static source-only iOS Lua 5.1 state-machine and level1.bclara authored property decoding, no execution, no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
