#!/usr/bin/env python3
"""G184 actual 2010 SceneImpl::CollectDummies native PIC string group metadata.

Static ARM shows substring-based dummy collector, probable original group
table. Decode only source PIC literals and string pointers with range checks;
DO NOT equate a table ordinal to SceneImpl GetDummy(int,unsigned) until
the exact native grouping/registration code proves it.
No modified Vita gameplay or proprietary asset republication, no VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER_SIZE=248613763
ADDR=0x62ea4
METHOD="SceneImpl::CollectDummies(irr::scene::ISceneNode*)"

def main(ipa,out):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("Original owner 2010 IPA required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original 2010 ZIP invalid")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 n=parse_macho(exe)
 m=subprocess.run(["c++filt"],input="\n".join(row[0] for row in n["entries"])+"\n",capture_output=True,text=True,check=True).stdout.splitlines()
 if len(m)!=len(n["entries"]):raise ValueError("original native symbol mismatch")
 syms=collections.defaultdict(set)
 for rec,name in zip(n["entries"],m):syms[rec[1]&~1].add(name)
 if METHOD not in syms[ADDR]:raise ValueError("not real original SceneImpl native method")
 sections=n["sections"]
 def vread(a,length):
  # S_ZEROFILL __common has NO initialized FILE bytes. Earlier G184
  # accidentally read arbitrary executable data using file offset 0.
  sec=next((s for s in sections if s[3] not in ("__common","__bss") and
             s[0]<=a and a+length<=s[0]+s[1]),None)
  if sec is None:return None
  off=sec[2]+a-sec[0]
  if off<0 or off+length>len(exe):return None
  return exe[off:off+length]
 def u32(a):
  d=vread(a,4)
  return struct.unpack("<I",d)[0] if d is not None else None
 def i32(a):
  d=vread(a,4)
  return struct.unpack("<i",d)[0] if d is not None else None
 def cstring(a):
  if not isinstance(a,int) or a==0:return None
  data=bytearray()
  for i in range(96):
   b=vread(a+i,1)
   if b is None:return None
   if b==b"\0":
    try:s=data.decode("ascii")
    except UnicodeDecodeError:return None
    if not (1<=len(s)<=95):return None
    return s
   if not 32<=b[0]<=126:return None
   data.append(b[0])
  return None
 def pic(loadvm,addvm):
  ldr=vread(loadvm,4)
  # Native 2010 ARM register/opcodes verified from G183 strict addresses;
  # don't decode arbitrary bytes or recompile original binary.
  literal=loadvm+8 + (0x788 if loadvm==0x62f8c else 0x778)
  delta=i32(literal)
  if delta is None:raise ValueError("original constant PIC literal not mapped "+hex(literal))
  result=(addvm+8+delta)&0xffffffff
  return {"source_native_ldr_VM":hex(loadvm),
          "source_native_add_VM":hex(addvm),
          "native_literal_pool_VM":hex(literal),
          "original_source_signed_PIC_delta":delta,
          "target_pointer_address_VM":hex(result),
          "target_VM_integer":result}
 dataA=pic(0x62f8c,0x62f90)
 dataB=pic(0x62fa0,0x62fa8)
 # Native collector accesses named global A's +8 for max type count,
 # and global B's +0 for first pattern pointer list.
 atA=dataA["target_VM_integer"];atB=dataB["target_VM_integer"]
 descriptor={"source_vm":hex(atA),"field0_vm_or_int":u32(atA),
             "field4_vm_or_int":u32(atA+4),"field8_vm_or_int":u32(atA+8),
             "source_count_semantics_unproven":True}
 ptr=u32(atB)
 prefixes=[]
 # Table pointer range/labels can be validated only if true C strings
 # are present. Do not invent synthetic "Dummy_Chest" names.
 if ptr and vread(ptr,4):
  count=descriptor["field8_vm_or_int"]
  if count is None or count<=0 or count>2000:limit=65
  else:limit=min(count,100)
  for i in range(limit):
   key=u32(ptr+4*i)
   if key is None:break
   label=cstring(key)
   if label is None:
    prefixes.append({"ordinal":i,"2010_pointer_VM":hex(key),
                     "raw_source_original_string":None,"unresolved":True})
    if i>4:break
   else:
    prefixes.append({"ordinal":i,"2010_pointer_VM":hex(key),
                     "raw_source_original_string":label,"unresolved":False})
 code=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 sec=next(s for s in sections if s[3]=="__text" and s[0]<=ADDR<s[0]+s[1])
 addrs=sorted(syms)
 pos=bisect.bisect_right(addrs,ADDR)
 end=addrs[pos] if pos<len(addrs) else sec[0]+sec[1]
 size=min(12000,end-ADDR,sec[0]+sec[1]-ADDR)
 source=list(code.disasm(exe[sec[2]+ADDR-sec[0]:sec[2]+ADDR-sec[0]+size],ADDR))
 dmap={i.address:i for i in source}
 need={
  0x62f8c:("ldr","fp, [pc, #0x788]"),
  0x62f90:("add","r1, pc, fp"),
  0x62f94:("ldr","fp, [r1, #8]"),
  0x62fa0:("ldr","r8, [pc, #0x778]"),
  0x62fa8:("add","r5, pc, r8"),
  0x62fb0:("ldr","ip, [r5]"),
  0x62fbc:("ldr","r1, [ip]"),
  0x62fc0:("bl","#0x73e84"),
 }
 for vm,(mn,args) in need.items():
  ins=dmap.get(vm)
  if ins is None or ins.mnemonic!=mn or ins.op_str!=args:
   raise ValueError("g184 original native PIC matching source opcode drift "+hex(vm))
 armctx=[{"VM":hex(x.address),"opcode":x.mnemonic,"args":x.op_str}
   for x in source if 0x62f8c<=x.address<=0x63280]
 proof={
   "origin":"Original 2010 iOS SceneImpl::CollectDummies actual ARM PIC and owner source string descriptors",
   "original_native_method":METHOD,"method_VM":hex(ADDR),
   "native_source_original_verified_PIC_pattern_count_descriptor":dataA,
   "native_source_original_verified_PIC_pattern_ptr_descriptor":dataB,
   "pattern_count_source_descriptor_raw_integer_fields":descriptor,
   "original_dynamic_table_symbol":"SceneImpl::s_dummiesTable",
   "source_PIC_points_to_macho_S_ZEROFILL_not_initialized_file_data":True,
   "old_G184_972_5127504_2_file_words_are_INVALID_as_table_contents":True,
   "pattern_list_first_source_virtual_address":hex(ptr) if ptr is not None else None,
   "source_PIC_potential_original_dummy_substring_keys":prefixes,
   "original_native_collect_loop_ARM_context_no_binary_bytes":armctx,
   "original_UniBeam_dummy_group_14_and_33_input_proven":[14,33],
   "original_scene_dummy_registry_plus_0x278_group_index_proven":True,
   "original_PIC_substring_pattern_ordinal_equals_native_scene_index_PROVEN":False,
   "original_scene_dummy_group14_name_PROVEN":False,
   "original_scene_dummy_group33_name_PROVEN":False,
   "source_name_has_real_actual_2010_arm_to_asset_dummy_mapping_PROVEN":False,
   "NO_MODIFIED_VITA_INPUT_VFX_DAMAGE":True,
   "NO_USER_IPA_BINARY_OR_LICENSED_ASSET_EXPORT":True,"NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n")
 print("G184 authentic PIC source A",dataA,"count fields",descriptor)
 print("G184 authentic PIC source B",dataB,"table pointer",hex(ptr) if ptr is not None else None)
 for row in prefixes:print("G184 ORIGINAL PATT",row)
 for row in armctx[:200]:print("G184 ORIGINAL COLLECT ARM",row["VM"],row["opcode"],row["args"])
 print("G184 original dummy group14/33 model names remain UNPROVEN until registration index confirmed; NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 main(a.ipa,a.out)
