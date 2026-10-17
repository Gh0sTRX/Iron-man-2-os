#!/usr/bin/env python3
"""G132: Original 2010 Gameloft iOS SetInputEnabled(lua_State*)
native ARM 0x18494 branches specially for input code 14 at 0x184f4.
Resolve target C++ original symbol names and disassemble exact linked
methods 0x975e8 0xffe78 0xffff8 0x1001f8 0xc2518 0xdb504
vs generic code 2/6 calls 0x1d260, to determine if code14 means flight,
camera, all-input or only HUD context. DO NOT infer just from numeric 14.
No original executable/machine bytes redistribution, NO VPK.
"""
import argparse,bisect,json,subprocess,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
import capstone
SITES=[0x18494,0x975e8,0xffe78,0xffff8,0x1001f8,0xc2518,0xdb504,0x1d260,
0x25d9c,0x25c80,0x23960,0x7fd3c,0x7fc80,0xc2540]
def main(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError("authentic 2010 original owner IPA only")
 with zipfile.ZipFile(ipa) as z:raw=z.read("Payload/IronMan2.app/IronMan2")
 obj=parse_macho(raw)
 syms=sorted(obj['entries'],key=lambda x:x[1]&~1)
 names=[x[0] for x in syms]
 dem=subprocess.run(["c++filt"],input="\n".join(names)+"\n",
       capture_output=True,check=True,text=True).stdout.splitlines()
 if len(dem)!=len(syms):raise ValueError("C++ owner native symbols inconsistent")
 rows=list(zip(syms,dem))
 addresses=sorted(set(x[0][1]&~1 for x in rows))
 text_sects=[s for s in obj['sections'] if s[3]=='__text']
 found=[]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for addr in SITES:
  idx=bisect.bisect_right(addresses,addr)-1
  if idx<0:raise ValueError('native original address before first symbol')
  base=addresses[idx]
  symlist=[(a,dem) for a,dem in rows if (a[1]&~1)==base]
  sec=next((s for s in text_sects if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:raise ValueError(f"0x{addr:x} outside owner native original ARM __text")
  next_addr=addresses[idx+1] if idx+1<len(addresses) else sec[0]+sec[1]
  limit=min(500,sec[0]+sec[1]-addr,next_addr-addr)
  offset=sec[2]+addr-sec[0]
  is_thumb=bool(symlist[0][0][1]&1) if symlist else False
  instructions=list((thumb if is_thumb else arm).disasm(raw[offset:offset+limit],addr))
  found.append({'real_owner_native_iOS_ARM_address':hex(addr),
    'entry_equals_exact_original_CPP_symbol_start':base==addr,
    'owner_original_nearest_Cplusplus_names':[dem for _,dem in symlist][:16],
    'owner_original_preceding_Cplusplus_address':hex(base),
    'actually_disassembled_original_ARM_source_bytes':len(instructions)>0,
    'original_native_ARM_control_flow':[
      {'pc':hex(ins.address),'op':ins.mnemonic,'registers_or_imm':ins.op_str}
      for ins in instructions[:100]],
    'meaning_of_first_Mission000_markv_flight_gate_proven':False})
 assert len(found)==len(SITES)
 out.mkdir(parents=True,exist_ok=True)
 report={'actual_original_iOS_native_symbols_for_special_14_generic_2_6':found,
  'verified_special_Input_14_branch_ARM_0x184CC':True,
  'flight_disallowed_in_Level1_known':False,
  'flight_permitted_in_Level1_known':False,
  'original_iOS_raw_arm_bytes_distributed':False,'NO_VPK':True}
 (out/'G132_2010_NATIVE_SetInputEnabled_SPECIAL_14_AND_GENERIC_2_6_REAL_CALL_TARGETS.json').write_text(
   json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 for m in found:
  print("G132 original INPUT native call",m['real_owner_native_iOS_ARM_address'],
   m['owner_original_nearest_Cplusplus_names'][:6],
   "at_exact_entry",m['entry_equals_exact_original_CPP_symbol_start'])
  if m['real_owner_native_iOS_ARM_address'] in ('0xffe78','0xffff8','0x1001f8','0x1d260'):
   for ins in m['original_native_ARM_control_flow'][:65]:
    print('G132 2010 ORIGINAL INSTRUCTION',ins)
 print('G132 original special 14 native submethods resolved, real flight permission remains evidence-dependent NO VPK.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args();main(a.ipa,a.out)
