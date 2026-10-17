#!/usr/bin/env python3
"""G148: OWN original 2010 iOS IronMan2 v1.0.0 text_english localization.

Reconstruct ALL 1,213 source Lua one-based CLARA IDs into actual native
StringMgr::strIDClara2Real(int*) packed (section << 12)|local indexes.
The 14 source localized sections each consist of little-endian u16
count then count*[u16 byte_length + EXACT UTF-8 original text bytes].
Original source VM 0xCE8CC uses one-based Lua ID then subtracts one
and selects chapter section boundaries. E.g. 339 -> 338 - 255 = 83,
section1 ("chap1.english"), native value 0x1053.
This recovers strings for all future level scripts without inventing
mission progression, flight permission, or artificial HUD layouts.

User-provided IPA is read-only and NEVER copied to public GitHub.
Do not commit generated copyrighted full text or original IPA. No VPK.
"""
import argparse,csv,hashlib,json,struct,zipfile
from pathlib import Path
AUTHENTIC_SECTIONS=(
 ('about.english',255),('chap1.english',90),
 ('chap10.english',73),('chap2.english',92),
 ('chap3.english',118),('chap4.english',79),
 ('chap5.english',17),('chap6.english',108),
 ('chap7.english',1),('chap8.english',48),
 ('chap9.english',8),('global.english',33),
 ('init.english',5),('menu.english',286))
def decode_pack(data):
 if len(data)<80:raise ValueError('2010 source text archive invalid')
 n=struct.unpack_from('<H',data,0)[0]
 if n!=len(AUTHENTIC_SECTIONS)+2:raise ValueError('not the owner original 14-section text pack')
 base=2+4*n
 off=struct.unpack_from('<'+str(n)+'I',data,2)
 if off[0]!=0 or off[-1]!=len(data)-base or any(x>=y for x,y in zip(off,off[1:])):
  raise ValueError('original locale data invalid offsets')
 count=struct.unpack_from('<H',data,base)[0]
 if count!=len(AUTHENTIC_SECTIONS):raise ValueError('original locale naming metadata wrong')
 p=base+2
 rows=[];stats=[]
 for sec,(known,count_expected) in enumerate(AUTHENTIC_SECTIONS):
  length=struct.unpack_from('<H',data,p)[0];p+=2
  if not 1<=length<=255:raise ValueError('filename length invalid')
  name=data[p:p+length].decode('utf-8');p+=length
  if name!=known:raise ValueError('original localized section order changed: '+name)
  b=data[base+off[sec+1]:base+off[sec+2]]
  count=struct.unpack_from('<H',b,0)[0]
  if count!=count_expected:raise ValueError('original text line count changed: '+name)
  k=2
  for item in range(count):
   size=struct.unpack_from('<H',b,k)[0];k+=2
   if k+size>len(b):raise ValueError('localized source text OOB')
   original=b[k:k+size].decode('utf-8');k+=size
   rows.append({
    'Lua_CLARA_ID_1based':len(rows)+1,
    'native_encoded_id':'0x%04X'%((sec<<12)|item),
    'source_section_index':sec,
    'source_file':name,
    'local_index_0based':item,
    'original_english_text':original})
  if k!=len(b):raise ValueError('source locale trailing bytes in '+name)
  stats.append({'source_file':name,'lines':count,
                'source_SHA256':hashlib.sha256(b).hexdigest()})
 if p!=base+off[1]:raise ValueError('2010 original text pack name data offset drift')
 if len(rows)!=1213:raise ValueError('2010 original 1213 source strings missing')
 if rows[338]['native_encoded_id']!='0x1053':
  raise ValueError('2010 original StringMgr translation source ID339 changed')
 if rows[338]['original_english_text']!='Are you ready to face the crowd, sir?':
  raise ValueError('2010 original chapter1 JARVIS QTE text not source-matched')
 return rows,stats
def main(path,out):
 with zipfile.ZipFile(path) as z:
  b=z.read('Payload/IronMan2.app/text_english')
 rows,stats=decode_pack(b)
 out.mkdir(parents=True,exist_ok=True)
 target=out/'G148_original_2010_1213_Lua_ID_to_English_text.csv'
 with target.open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]))
  writer.writeheader();writer.writerows(rows)
 (out/'G148_original_2010_English_text_sections_and_QTE339.json').write_text(
  json.dumps({'owner_source':'original user-provided 2010 IronMan2 iOS text_english archive',
    'total_source_strings':1213,
    'sections':stats,
    'first_mission_ShowTut_339':rows[338],
    'actual_original_QTE_in_Vita_playable':False,
    'VPK_generated':False},indent=2,ensure_ascii=False)+'\n')
 print('G148 VERIFIED original 2010 Game StringMgr 1213 lines, 14 section pack, source Lua ID339 native 0x1053, original REAL JARVIS text. NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
