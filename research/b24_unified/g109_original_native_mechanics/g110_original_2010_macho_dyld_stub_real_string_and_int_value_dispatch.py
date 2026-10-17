#!/usr/bin/env python3
"""Resolve imported actual 2010 iOS original ARM libc functions for
EntityData GetParamValue int and bool. The original executable ARM BL
targets 0x47111c strcmp-like and 0x470e88 typed-value conversion.
Resolve LC_DYSYMTAB indirect symbols against MachO __stubs reserved1/2.
No proprietary machine code or entire executable exported. NO VPK.
"""
import argparse,json,struct,subprocess,zipfile
from pathlib import Path
def run(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('Original owner IPA 2010 exact size expected')
 with zipfile.ZipFile(ipa) as z:data=z.read('Payload/IronMan2.app/IronMan2')
 assert data[:4]==b'\xce\xfa\xed\xfe'
 _,cpu,sub,typ,ncmds,_,flags=struct.unpack_from('<IiiIIII',data)
 sym=None;dysym=None;stubs=[];pos=28
 for _ in range(ncmds):
  cmd,sz=struct.unpack_from('<II',data,pos)
  assert 8<=sz<=65536 and pos+sz<=len(data)
  if cmd==2:sym=struct.unpack_from('<4I',data,pos+8)
  if cmd==0xb:dysym=struct.unpack_from('<18I',data,pos+8)
  if cmd==1:
   nsect=struct.unpack_from('<I',data,pos+48)[0]
   for j in range(nsect):
    p=pos+56+68*j
    assert p+68<=pos+sz
    name=data[p:p+16].split(b'\0',1)[0].decode('ascii','replace')
    sec_vm,sec_size,sec_off=struct.unpack_from('<3I',data,p+32)
    sec_flags,reserved1,reserved2=struct.unpack_from('<3I',data,p+56)
    if sec_flags&0xff==0x8 or name in ('__stubs','__symbol_stub','__picsymbolstub4'):
     stubs.append(dict(section=name,vm=sec_vm,sz=sec_size,
        flags=sec_flags,indirect_index=reserved1,stub_bytes=reserved2))
  pos+=sz
 if sym is None or dysym is None:raise ValueError('missing original 2010 MachO dynamic symbols')
 symoff,nsyms,stroff,strsize=sym
 indirectoff,nindirect=dysym[12:14]
 assert 0<nsyms<300000 and 0<nindirect<300000
 assert symoff+12*nsyms<=len(data) and stroff+strsize<=len(data)
 assert indirectoff+4*nindirect<=len(data)
 strings=data[stroff:stroff+strsize]
 imported=[]
 for target in (0x47111c,0x470e88):
  match=[]
  for s in stubs:
   if not(s['vm']<=target<s['vm']+s['sz']) or not s['stub_bytes']:continue
   if (target-s['vm'])%s['stub_bytes']:continue
   which=s['indirect_index']+(target-s['vm'])//s['stub_bytes']
   if which>=nindirect:continue
   i=struct.unpack_from('<I',data,indirectoff+which*4)[0]
   if i & 0xc0000000:
    match.append({'no_external_source_symbol':True,'index_flags':hex(i)})
    continue
   if i>=nsyms:continue
   off,t,sec,desc,addr=struct.unpack_from('<IBBHI',data,symoff+12*i)
   if off>=strsize:continue
   end=strings.find(b'\0',off)
   if end<0:continue
   orig=strings[off:end].decode('latin1','replace')
   demo=subprocess.run(['c++filt',orig.removeprefix('_')],text=True,capture_output=True,check=True).stdout.strip()
   match.append({'original_iOS_dynamic_symbol':orig,'resolved_CPP_or_libc_name':demo,
    'original_stub_section':s['section'],
    'original_stub_entry_size_bytes':s['stub_bytes'],
    'original_dynamic_symbol_index':i})
  imported.append({'original_real_native_ARM_branch_target_vm':hex(target),
    '2010_source_import_dyld_symbol_resolution':match,
    'source_resolution_unique':len(match)==1})
 if not all(x['source_resolution_unique'] for x in imported):
  # Report original 2010 ARM call targets' actual Mach-O section
  # provenance, never assume an imported library call when it may be a
  # statically compiled function.
  probe=[];pos=28
  for _ in range(ncmds):
   cmd,sz=struct.unpack_from('<II',data,pos)
   if cmd==1:
    count=struct.unpack_from('<I',data,pos+48)[0]
    for j in range(count):
     sp=pos+56+68*j
     name=data[sp:sp+16].split(b'\\0',1)[0].decode('ascii','replace')
     vm,ln,off=struct.unpack_from('<3I',data,sp+32)
     fg,r1,r2=struct.unpack_from('<3I',data,sp+56)
     if any(vm<=target<vm+ln for target in (0x47111c,0x470e88)):
      probe.append({'section':name,'vm':hex(vm),'size':ln,
       'flags':hex(fg),'indirect_start':r1,'reserved2_stub_bytes':r2})
   pos+=sz
  print('G110 actual ORIGINAL dynamic-call sections for exact targets:',probe)
  print('Native 2010 IMPORT section candidates:',stubs)
  raise ValueError('native original ARM import stub mapping unresolved; no fake std::string claim')
 report={'original_owner':'2010 iOS IronMan2 user IPA',
  'actual_native_EntityData_GetParamValue_int_src_vm':'0xd7548',
  'actual_native_EntityData_GetParamValue_bool_src_vm':'0xd76bc',
  'real_imported_CPP_libc_lookup_functions':imported,
  'C1L1_26_real_Attack_instance_Damage_values_typed_by_this_stage':False,
  'NO_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G110_ACTUAL_2010_CPLUSPLUS_EntityData_GetParamValue_GetInt_GetBool_SOURCE_IMPORTED_STUBS.json').write_text(json.dumps(
  report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G110 ORIGINAL 2010 native ARM EntityData::GetParamValue called REAL library funcs',imported)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.out)
