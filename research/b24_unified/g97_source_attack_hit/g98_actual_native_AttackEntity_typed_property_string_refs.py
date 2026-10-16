#!/usr/bin/env python3
"""G98 real 2010 ARM AttackEntity::LoadFromFile loads exactly 14 source
EntityData::GetParamValue(char*,int*/bool*) calls; reconstruct literal
cstring/struct address context for each original attack-data key without
inventing numeric values or claiming a property binary schema decoded.
No game binary redistribution. Source metadata only, NO VPK.
"""
import argparse,bisect,collections,json,struct,subprocess,zipfile,re,sys
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_REG,ARM_OP_IMM,ARM_REG_PC
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho

METHOD='AttackEntity::LoadFromFile(EntityData*)'
ADDR=0xa934c
GET_INT=0xd7548
GET_BOOL=0xd76bc
def inspect(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('Need private owner exact 2010 IPA')
 with zipfile.ZipFile(ipa) as z:exe=z.read('Payload/IronMan2.app/IronMan2')
 m=parse_macho(exe)
 sections=m['sections']
 sec=next((s for s in sections if s[3]=='__text' and s[0]<=ADDR<s[0]+s[1]),None)
 if not sec:raise ValueError('original ARM AttackEntity method absent')
 def vbytes(addr,count):
  sec=next((s for s in sections if s[0]<=addr and addr+count<=s[0]+s[1]),None)
  if sec is None:return None
  offset=sec[2]+addr-sec[0]
  if offset<0 or offset+count>len(exe):return None
  return exe[offset:offset+count]
 def pointer(addr):
  raw=vbytes(addr,4)
  if raw is None:return None
  return struct.unpack('<I',raw)[0]
 def cstring(addr):
  chunk=vbytes(addr,1)
  if not chunk:return None
  vals=[]
  for i in range(144):
   ch=vbytes(addr+i,1)
   if not ch:return None
   v=ch[0]
   if v==0:
    if not 2<=len(vals)<=100:return None
    s=bytes(vals).decode('ascii',errors='ignore')
    if len(s)!=len(vals):return None
    if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_. \-]{1,99}',s):return None
    return s
   if not 32<=v<=126:return None
   vals.append(v)
  return None
 # End at subsequent real symbol; 105 original 32-bit instructions = 420 bytes.
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 raw=vbytes(ADDR,420)
 if raw is None:raise ValueError('Missing authentic original AttackEntity native bytes')
 instructions=list(arm.disasm(raw,ADDR))
 if len(instructions)!=105:raise ValueError('original AttackEntity source disassembly changed')
 methods=[]
 for k,ins in enumerate(instructions):
  if not ins.mnemonic.startswith(('bl','blx')) or not ins.operands:continue
  target=ins.operands[0].imm&~1 if ins.operands[0].type==ARM_OP_IMM else 0
  if target not in (GET_INT,GET_BOOL):continue
  start=max(0,k-12)
  near=instructions[start:k]
  consts=[]
  for j in near:
   if j.mnemonic not in ('ldr','ldrb') or len(j.operands)<2:continue
   op=j.operands[1]
   if op.type!=ARM_OP_MEM or op.mem.base!=ARM_REG_PC:continue
   literal=(j.address+8+op.mem.disp)&~3
   value=pointer(literal)
   if value is None:continue
   name=cstring(value)
   direct=cstring(literal)
   consts.append({'original_ARM_instruction_relative_pc_hex':hex(j.address-ADDR),
    'operand_register':j.reg_name(j.operands[0].reg) if j.operands[0].type==ARM_OP_REG else None,
    'literal_pool_address_hex':hex(literal),
    'original_pointer_value_hex':hex(value),
    'points_to_2010_native_cstring':name,
    'literal_pool_itself_string':direct})
  instructions_before=[{'relative_pc_hex':hex(j.address-ADDR),
     'opcode':j.mnemonic,'operand_registers_and_immediates':j.op_str}
     for j in near]
  # No guess about "last literal" being r1 string; require direct
  # same register r1 and no subsequently written r1 between loading and call.
  probable=[]
  for index,j in enumerate(near):
   if j.mnemonic!='ldr' or not j.operands or j.operands[0].type!=ARM_OP_REG:continue
   if j.reg_name(j.operands[0].reg)!='r1':continue
   if j.operands[1].type!=ARM_OP_MEM or j.operands[1].mem.base!=ARM_REG_PC:continue
   lit=(j.address+8+j.operands[1].mem.disp)&~3
   ptr=pointer(lit)
   key=cstring(ptr) if ptr is not None else None
   if not key:continue
   # A later instruction writing argument r1 makes this speculative.
   later_r1_write=any(l.operands and l.operands[0].type==ARM_OP_REG and
          l.reg_name(l.operands[0].reg)=='r1' and l.mnemonic.startswith((
          'ldr','mov','add','sub','adr','eor','orr','and','mul'))
          for l in near[index+1:])
   if not later_r1_write:
    probable.append({'original_key_name':key,'source_key_pointer_hex':hex(ptr),
         'native_load_address_hex':hex(j.address)})
  methods.append({'native_GetParamValue_call_address_hex':hex(ins.address),
   'native_GetParamValue_call_relative_pc_hex':hex(ins.address-ADDR),
   'actual_original_cpp_GetParamValue_expected_type':'bool*' if target==GET_BOOL else 'int*',
   'native_target_function_address_hex':hex(target),
   'proven_r1_argument_original_cstring':probable[-1] if probable else None,
   'source_literal_pool_cstring_candidates':consts,
   'bounded_native_ARM_context_before_call':instructions_before,
   'original_destination_struct_field_offset_confirmed':False,
   'exact_level1_serialized_property_data_confirmed':False})
 if len(methods)!=14:raise ValueError('2010 original AttackEntity::LoadFromFile GetParamValue calls count no longer 14: '+str(len(methods)))
 count=sum(bool(v['proven_r1_argument_original_cstring']) for v in methods)
 report={'source_original_2010_AttackEntity_LoadFromFile_native_method':hex(ADDR),
 'source_original_2010_int_and_bool_GetParamValue_call_total':14,
 'native_typed_GetParamValue_call_sites':methods,
 'exact_source_r1_argument_cstrings_proven_count':count,
 'exact_original_per_attack_Damage_values_and_serialized_tlv_NOT_DECODDED':True,
 'AttackEntity_GetParamValue_NATIVE_INT_BOOL_2010_SOURCE_TYPES':True,
 'No_fake_original_weapon_damage':True,
 'NO_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G98_ORIGINAL_2010_ATTACKENTITY_GETPARAMVALUE_14_TYPED_FIELD_NAMES.json').write_text(
  json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G98 14 original 2010 AttackEntity::LoadFromFile typed native loads, r1 source string proven',count)
 for m in methods:
  print('ORIGINAL ATTACK PROPERTY',m['native_GetParamValue_call_relative_pc_hex'],
     m['actual_original_cpp_GetParamValue_expected_type'],
     m['proven_r1_argument_original_cstring'] or
      [x for x in m['source_literal_pool_cstring_candidates'] if x['points_to_2010_native_cstring']])
  if not m['proven_r1_argument_original_cstring']:
   for q in m['bounded_native_ARM_context_before_call']:
    print('  SOURCE',q['relative_pc_hex'],q['opcode'],q['operand_registers_and_immediates'])
 print('NEVER imply raw Damage numeric int typed serialized until actual source CLARA instance field connected.')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();inspect(a.ipa,a.out)
