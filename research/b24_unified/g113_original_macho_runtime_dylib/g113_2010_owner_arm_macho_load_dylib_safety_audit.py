#!/usr/bin/env python3
"""G113 native 2010 user owner IronMan2.app ARM MachO LC_LOAD_DYLIB
and IPA actual absolute/bundled library path audit. Diagnostic only.
Never patch original decrypted binary or disable original protection.
No original package/executable published; no Vita VPK.
"""
import argparse,json,struct,zipfile
from pathlib import Path
HEADER='<IiiIIII'
DYLIB_CMDS={0xc:'LC_LOAD_DYLIB',0xd:'LC_ID_DYLIB',
 0x18:'LC_LOAD_WEAK_DYLIB',0x1f:'LC_REEXPORT_DYLIB',
 0x23:'LC_LOAD_UPWARD_DYLIB',0x80000018:'LC_LOAD_WEAK_DYLIB_REQUIRED'}
def main(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('requires exact original 2010 owner IPA')
 with zipfile.ZipFile(ipa) as z:
  exe=z.read('Payload/IronMan2.app/IronMan2')
  names=set(z.namelist())
 if exe[:4]!=b'\xce\xfa\xed\xfe':raise ValueError('not 2010 iOS native Mach-O')
 magic,arch,sub,kind,ncmds,total,flags=struct.unpack_from(HEADER,exe)
 pos=28;deps=[];other=[]
 for index in range(ncmds):
  cmd,sz=struct.unpack_from('<II',exe,pos)
  if sz<8 or pos+sz>len(exe):raise ValueError('bad authenticated original Mach-O command')
  if (cmd&0x7fffffff) in (0xc,0xd,0x18,0x1f,0x23):
   off=struct.unpack_from('<I',exe,pos+8)[0]
   if off<24 or off>=sz:raise ValueError('2010 native dylib path is outside load command')
   path=exe[pos+off:pos+sz].split(b'\0',1)[0].decode('utf8','replace')
   probe=path.lstrip('/')
   bundled=[x for x in names if x.endswith('/'+probe) or x.endswith(path)]
   deps.append({'command':hex(cmd),'kind':DYLIB_CMDS.get(cmd&0x7fffffff,'DYLIB_CMD'),
     '2010_native_original_load_path':path,
     'original_ipa_contains_matching_library_path':bool(bundled),
     'matched_archive_names_only':bundled[:5],
     '2010_native_load_command_index':index})
  else:other.append(hex(cmd))
  pos+=sz
 out.mkdir(parents=True,exist_ok=True)
 result={'source_original_game':'owner 2010 iPhone Iron Man 2 v1.0.0',
  'arm_cputype':arch,'native_dylib_dependency_count':len(deps),
  'actual_original_native_dylib_dependencies':deps,
  'touchhle_source_fails_on_non_usr_lib_when_guest_file_exists':True,
  'original_ipa_patched_or_rewritten':False,'VPK_generated':False}
 (out/'G113_REAL_ORIGINAL_2010_GAME_MACHO_LIBRARY_DEPENDENCY_AUDIT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print('G113 original native iOS ARM real MachO dependent dynlibs',json.dumps(deps,ensure_ascii=False))
 print('G113 does NOT imply touchHLE starts, keeps original private binary intact. NO VPK')
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--ipa',type=Path,required=True)
 q.add_argument('--out',type=Path,required=True);a=q.parse_args()
 main(a.ipa,a.out)
