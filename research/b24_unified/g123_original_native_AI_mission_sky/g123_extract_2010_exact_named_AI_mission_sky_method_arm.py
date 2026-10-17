#!/usr/bin/env python3
"""2010 original iOS user IPA full bounded disassembly for exact genuine
CNPC:: state/target hit (not C++ names alone), MissionConditionKill
and GS_GamePlay::UpdateSkyBox. No assembled code or IPA exported.
Source native instruction-level control flow only, no fake completed AI.
"""
import argparse,bisect,collections,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho
TARGETS={
 'GS_GamePlay::UpdateSkyBox(int)':'0xc2810',
 'CNPC::OnDie()':'0xe1ba8',
 'CNPC::OnSpawn(SpawnPoint*, Entity*)':'0xe1b4c',
 'CNPC::SetState(int, int)':'0xe1694',
 'CNPC::ChooseAttack()':'0xe1888',
 'CNPC::ChooseTarget()':'0xe2d78',
 'CNPC::UpdateStateIdle(int, CNPC::NPCStateNode&)':'0xe408c',
 'CNPC::UpdateStateHurt(int, CNPC::NPCStateNode&)':'0xe7190',
 'CNPC::UpdateStateAttack(int, CNPC::NPCStateNode&, void*)':'0xe5868',
 'CNPC::UpdateStateSpawn(int, CNPC::NPCStateNode&)':'0xe413c',
 'CNPC::UpdateState(int, void*)':'0xe2470',
 'MissionConditionKill::EvaluateComplete(int)':'0xcb5b8',
 'MissionConditionKill::LoadFromFile(EntityData*)':'0xcb4ec',
 'MissionConditionProtect::EvaluateFail(int)':'0xffd3c',
 'BigMachineNPC::ChooseAttack()':'0x104358'
}
def main(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('private owner exact original 2010 IPA expected')
 with zipfile.ZipFile(ipa) as z:exe=z.read('Payload/IronMan2.app/IronMan2')
 native=parse_macho(exe)
 syms=native['entries'];dem=subprocess.run(['c++filt'],
    input='\n'.join(r[0] for r in syms)+'\n',text=True,capture_output=True,check=True).stdout.splitlines()
 assert len(syms)==len(dem)
 names=collections.defaultdict(set)
 for s,n in zip(syms,dem):names[n].add(s[1]&~1)
 addresses=sorted(set(s[1]&~1 for s in syms))
 secs=[s for s in native['sections'] if s[3]=='__text']
 methods=[]
 csA=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 csT=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for c in (csA,csT):c.detail=True
 for name,addr in TARGETS.items():
  source_addr=int(addr,16)
  variants=names.get(name,set())
  if source_addr not in variants:raise ValueError('G123 expected native original 2010 method differs '+name+str(variants))
  sec=next((s for s in secs if s[0]<=source_addr<s[0]+s[1]),None)
  if not sec:raise ValueError('missing original native code section '+name)
  symbol=next((s for s,n in zip(syms,dem) if n==name and s[1]&~1==source_addr),None)
  ix=bisect.bisect_right(addresses,source_addr)
  last=addresses[ix] if ix<len(addresses) else sec[0]+sec[1]
  size=min(last-source_addr,sec[0]+sec[1]-source_addr,5000)
  if size<4:raise ValueError('original owner 2010 tiny function '+name)
  ins=list((csT if symbol[1]&1 else csA).disasm(
    exe[sec[2]+source_addr-sec[0]:sec[2]+source_addr-sec[0]+size],source_addr))
  rows=[]
  for op in ins:
   calltarget=op.operands[0].imm&~1 if op.mnemonic in ('bl','blx') and op.operands and op.operands[0].type==ARM_OP_IMM else None
   known=sorted(n for n,a in names.items() if calltarget in a)[:6] if calltarget is not None else []
   rows.append({'native_original_relative_pc':hex(op.address-source_addr),
    'verified_ARM_opcode':op.mnemonic,'actual_original_registers_literals':op.op_str,
    'resolved_2010_CPP_called_symbols_if_BL':known})
  methods.append({'original_2010_cpp_name':name,'original_arm_address':addr,
   'original_arm_function_bytes':size,'verified_code_instr_count':len(rows),
   'original_native_ARM_control_flow_register_trace_metadata':rows,
   'user_expected_native_AI_or_sky_algorithm_PORTED_to_Vita':False})
 out.mkdir(parents=True,exist_ok=True)
 report={'original_2010_native_CPPP_methods':methods,
   '2010_guest_original_source_methods_verified':len(methods),
   'source_NPC_AI_mission_GLES_runtime_fully_reproduced':False,
   'no_original_game_binary_or_IPA_exported':True,'NO_VPK':True}
 (out/'G123_AUTHENTIC_2010_NATIVE_CNCP_SKYBOX_MISSION_KILL_ARM_OPCODE_CONTEXT.json').write_text(
    json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G123 original source 2010 exact bounded method instruction/branch count',len(methods))
 for m in methods:
  print('G123_ORIGINAL_METHOD',m['original_arm_address'],m['original_2010_cpp_name'],
     'code bytes',m['original_arm_function_bytes'],'instructions',m['verified_code_instr_count'])
  if m['original_2010_cpp_name'] in ('GS_GamePlay::UpdateSkyBox(int)',
    'MissionConditionKill::EvaluateComplete(int)',
    'CNPC::SetState(int, int)','CNPC::OnDie()'):
   for ins in m['original_native_ARM_control_flow_register_trace_metadata']:
    print('G123_PROVEN_ARM',ins['native_original_relative_pc'],
      ins['verified_ARM_opcode'],ins['actual_original_registers_literals'],
      ins['resolved_2010_CPP_called_symbols_if_BL'])
 print('Do not fabricate original 2010 sky shader or NPC waves from method NAMES alone. NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path);a=p.parse_args();main(a.ipa,a.out)
