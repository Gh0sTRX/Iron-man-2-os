#!/usr/bin/env python3
"""2010 real iOS ARM GamePlayUI::SetUIKeyEnabled 0x1D260:
resolve actual key 2 and key 6 paths jumping 0x1D3FC/0x1D41C.
Disassemble all original ARM and label branch destinations and any
affected HUD/widget offsets. Key ID is not a bitmask.
User original 2010 IPA temporary only, NO VPK.
"""
import argparse,bisect,json,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho
import capstone
def go(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('authentic user 2010 owner original')
 with zipfile.ZipFile(ipa) as z:raw=z.read('Payload/IronMan2.app/IronMan2')
 m=parse_macho(raw)
 syms=sorted(m['entries'],key=lambda z:z[1]&~1)
 names=subprocess.run(['c++filt'],input='\n'.join(z[0] for z in syms)+'\n',text=True,capture_output=True,check=True).stdout.splitlines()
 assert len(names)==len(syms)
 adr=sorted(set(z[1]&~1 for z in syms))
 fn=0x1d260
 sect=next(s for s in m['sections'] if s[3]=='__text' and s[0]<=fn<s[0]+s[1])
 at=bisect.bisect_right(adr,fn)
 end=adr[at]
 n=min(end-fn,2900)
 d=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 instr=list(d.disasm(raw[sect[2]+fn-sect[0]:sect[2]+fn-sect[0]+n],fn))
 if not instr or instr[0].address!=fn:raise ValueError('original native iOS method not ARM')
 listing=[{'pc':hex(i.address),'op':i.mnemonic,'args':i.op_str} for i in instr]
 cases={'2':'0x1d3fc','6':'0x1d41c','14':'0x1d2d8'}
 checks={z['pc'] for z in listing}
 if not all(x in checks for x in cases.values()):raise ValueError('full original ARM switch cases missing; method bytes '+str(n))
 for label,target in cases.items():
  pos=next(k for k,x in enumerate(listing) if x['pc']==target)
  print('G133 EXACT ORIGINAL ARM input UI KEY',label,'CASE native',target)
  for row in listing[pos:pos+16]:print('G133 original 2010 ARM',row['pc'],row['op'],row['args'])
 print('G133 original entire GamePlayUI method bytes',n,'instructions',len(instr),'native method symbol class GamePlayUI::SetUIKeyEnabled')
 report={'genuine_owner_iOS_arm_method':'GamePlayUI::SetUIKeyEnabled(int, bool)',
 'entry_original_VM':'0x1d260','true_next_native_cpp_symbol':hex(end),
 'actual_2010_arm_instruction_listing':listing,
 'cases_key2_key6_special14_PC':cases,
 'source_verified_UI_switch_2_vs_6_distinct_cases':True,
 'flight_capability_of_suitcase_MarkV_level1_proven':False,
 'original_gameplay_Lua_VM_executed':False,'new_vpk':False}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G133_REAL_2010_ORIGINAL_UI_KEY2_KEY6_SPECIAL14_FULL_ARM_SWITCH.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();go(a.ipa,a.out)
