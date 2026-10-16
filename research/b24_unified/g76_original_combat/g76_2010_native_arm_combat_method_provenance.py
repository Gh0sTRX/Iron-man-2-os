#!/usr/bin/env python3
"""G76 genuine 2010 iOS Mach-O ARM binary native combat symbol/function probe.
Do not confuse Mach-O Itanium C++ symtab with Lua bytecode or homebrew B14.
Never publish proprietary machine code, full executable, IPA or VPK. Native
function body disassembly is for internal structural provenance only; artifact
stores method labels, addresses, instruction frequency/call edges, NOT bytes.
"""
from __future__ import annotations
import argparse,json,struct,zipfile,collections,hashlib,re,subprocess
from pathlib import Path
import capstone
NEEDLE=re.compile(r'(melee|combo|damage|hurt|attack|weapon|projectile|bullet|missile|unibeam|repuls|shield|health|life|hitbox|kill|spawn|enemy|fire|explos|blast|laser|splash|knock|guard|impact|npc|armor|laser|lockon|target)',re.I)
MAGIC=b'\xce\xfa\xed\xfe'
def parse_macho(data:bytes):
 if data[:4]!=MAGIC:raise ValueError('not little-endian 32-bit iOS MachO')
 if len(data)<28:raise ValueError('header truncated')
 magic,cputype,cpusubtype,filetype,ncmds,cmdsize,flags=struct.unpack_from('<IiiIIII',data)
 assert 0<ncmds<300
 pos=28;syms=None;sections=[];enc=[]
 for i in range(ncmds):
  if pos+8>len(data):raise ValueError('load command truncated')
  cmd,size=struct.unpack_from('<II',data,pos)
  if size<8 or pos+size>len(data):raise ValueError('bad native iOS MachO command')
  if cmd==2:
   syms=struct.unpack_from('<4I',data,pos+8)
  if cmd==1:
   vmaddr,vmsize,fileoff,filesize=struct.unpack_from('<4I',data,pos+24)
   count=struct.unpack_from('<I',data,pos+48)[0]
   for j in range(count):
    at=pos+56+j*68
    if at+68>pos+size:raise ValueError('section OOB')
    name=data[at:at+16].split(b'\0')[0].decode('latin1','replace')
    seg=data[at+16:at+32].split(b'\0')[0].decode('latin1','replace')
    addr,sz,off=struct.unpack_from('<3I',data,at+32)
    sections.append((addr,sz,off,name,seg))
  if cmd==0x21 and size>=20:
   cryptoff,cryptsize,cryptid=struct.unpack_from('<3I',data,pos+8)
   enc.append({'offset':cryptoff,'length':cryptsize,'cryptid':cryptid})
  pos+=size
 if syms is None:raise ValueError('MachO symtab not available')
 symoff,nsyms,stroff,strsize=syms
 if nsyms>300000 or symoff+nsyms*12>len(data) or stroff+strsize>len(data):
  raise ValueError('native iOS bad symbol table')
 strings=data[stroff:stroff+strsize];entries=[]
 for i in range(nsyms):
  st,n_type,n_sect,desc,addr=struct.unpack_from('<IBBHI',data,symoff+i*12)
  if st>=len(strings):continue
  end=strings.find(b'\0',st)
  if end<0:continue
  label=strings[st:end].decode('latin1','replace')
  if not label or addr==0:continue
  if label.startswith('_'):label=label[1:]
  entries.append((label,addr,n_type,n_sect))
 return {'sections':sections,'entries':entries,'nsyms':nsyms,'crypt':enc,
         'cputype':cputype,'filetype':filetype}
def main(ipa:Path,out:Path):
 with zipfile.ZipFile(ipa) as z:
  candidates=[]
  for f in z.infolist():
   if not f.filename.startswith('Payload/IronMan2.app/') or f.is_dir():continue
   if f.file_size<100000 or f.file_size>110000000:continue
   if '/' in f.filename.removeprefix('Payload/IronMan2.app/'):continue
   with z.open(f) as handle:prefix=handle.read(4)
   if prefix==MAGIC:candidates.append(f.filename)
  if len(candidates)!=1:raise ValueError('expected one original 32-bit iOS Mach-O executable: '+str(candidates))
  exe=z.read(candidates[0])
 parsed=parse_macho(exe)
 names=[x[0] for x in parsed['entries']]
 mangled='\n'.join(names)+'\n'
 c=subprocess.run(['c++filt'],input=mangled,text=True,capture_output=True,check=True).stdout.splitlines()
 if len(c)!=len(names):raise ValueError('demangler output does not match genuine symbols')
 native=[]
 address=collections.defaultdict(list)
 for row,dem in zip(parsed['entries'],c):
  label,addr,t,sect=row
  if NEEDLE.search(dem):
   native.append({'real_2010_symbol':label,'demangled_cpp':dem,'virtual_address_hex':f'0x{addr:08x}',
                  'native_thumb_bit':bool(addr&1),'native_symbol_type':t})
 for x in parsed['entries']:address[x[1]&~1].append(x[0])
 sections=parsed['sections']
 cs_arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 cs_thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 cs_arm.detail=False;cs_thumb.detail=False
 windows=[]
 for symbol in native:
  addr=int(symbol['virtual_address_hex'],16);ea=addr&~1
  secs=[sec for sec in sections if sec[0]<=ea<sec[0]+sec[1] and sec[3]=='__text']
  if not secs:continue
  sec=secs[0];where=sec[2]+ea-sec[0]
  if where>=len(exe):continue
  # We report summarized disassembly but never persist verbatim bytes.
  instructions=list((cs_thumb if addr&1 else cs_arm).disasm(exe[where:where+96],ea,count=22))
  opfreq=collections.Counter(i.mnemonic for i in instructions)
  branches=[{'offset_bytes':i.address-ea,'kind':i.mnemonic,
             'target_or_register':i.op_str[:55]} for i in instructions
             if i.mnemonic.startswith(('bl','b.','bx','cb'))][:12]
  windows.append({'demangled_cpp':symbol['demangled_cpp'],
                  'virtual_address_hex':symbol['virtual_address_hex'],
                  'real_thumb':bool(addr&1),'opcodes_decoded_at_entry':len(instructions),
                  'control_flow_calls':branches,
                  'opcode_histogram_first_96_bytes':dict(opfreq),
                  'full_function_control_flow_decompiled':False})
 class_counts=collections.Counter()
 for m in native:
  name=m['demangled_cpp']
  cl=name.split('::',1)[0] if '::' in name else '<global>'
  class_counts[cl]+=1
 out.mkdir(parents=True,exist_ok=True)
 result={
  'origin':'genuine owner 2010 iOS IPA MachO native ARM code and Itanium named symbols',
  'original_executable_path':candidates[0],
  'original_MachO_SHA256':hashlib.sha256(exe).hexdigest(),
  'symbol_table_total_native_symbols':parsed['nsyms'],
  'combat_name_matched_native_methods':len(native),
  'combat_class_symbols_counts':dict(class_counts.most_common()),
  'native_combat_method_addresses':native,
  'native_method_entry_96B_ARM_disassembly_summary':windows,
  'encryption_command_regions':parsed['crypt'],
  'native_full_functions_decompiled':False,
  'source_damage_HP_constants_authoritatively_verified':False,
  'source_attack_hit_frame_timing_verified':False,
  'is_B14_homebrew_physics':False,
  'G76_source_only_NO_VPK':True}
 (out/'G76_TRUE_ORIGINAL_2010_ARM_NATIVE_COMBAT_METHOD_SYMBOLS.json').write_text(
   json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print('PASS G76 authentic original iOS MachO',candidates[0],
       'symbol_table',parsed['nsyms'],'COMBAT_NAMED',len(native),
       'entry_ARM_disassembly',len(windows),'encryption_flags',parsed['crypt'])
 for symbol in native:
  if any(t in symbol['demangled_cpp'] for t in (
    'MainCharacter::StartMeleeAttack','MainCharacter::DoUniBeamAttack',
    'ProjectileEntity::DoSplashDamage','WeaponDB::FindWeaponEntityById',
    'MainCharacter::UpdateComboAttackAction','MainCharacter::ThrowMissile')):
   print('2010_CPP_REAL',symbol['virtual_address_hex'],symbol['demangled_cpp'])
 print('NOTE opcode/control-flow summary only. Native damage values and C++ body semantics NOT proven')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
