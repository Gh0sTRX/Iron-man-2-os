#!/usr/bin/env python3
"""Ephemeral owner-input inspection; publish only bounded structural evidence.

Never exports original bytes, sound-name banks, complete disassembly, links,
textures, executable, PCM or source state tables. No game rules are inferred.
"""
import collections
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import struct
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from fetch_owner_ipa import fetch
from prepare_audio_assets import prepare


def inspect(ipa):
    path=ROOT/'research/b24_unified/g76_original_combat/g76_2010_native_arm_combat_method_provenance.py'
    spec=importlib.util.spec_from_file_location('native_probe',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    import capstone
    from capstone import arm
    with zipfile.ZipFile(ipa) as archive:
        raw=archive.read('Payload/IronMan2.app/IronMan2')
    parsed=module.parse_macho(raw)
    entries=parsed['entries']
    thumb_addresses=set();command=28
    for _ in range(struct.unpack_from('<I',raw,16)[0]):
        kind,size=struct.unpack_from('<II',raw,command)
        if kind==2:
            offset,count=struct.unpack_from('<II',raw,command+8)
            for i in range(count):
                _,_,_,description,address=struct.unpack_from('<IBBHI',raw,offset+i*12)
                if description&0x0008:thumb_addresses.add(address&~1)
        command+=size
    names=subprocess.run(['c++filt'],input='\n'.join(r[0] for r in entries)+'\n',
                         text=True,capture_output=True,check=True).stdout.splitlines()
    if len(names)!=len(entries):raise ValueError('Symbol count mismatch')
    symbols=collections.defaultdict(list)
    for row,name in zip(entries,names):symbols[row[1]&~1].append(name)
    addresses=sorted(symbols)
    target=re.compile(r'^(MainCharacter::(MainCharacter|Init\()|Object3D::(SetPosition|SetMatrix)|'
        r'Model::(SetPosition|GetPosition|SetMatrix)|CollisionData::|PositionData::|'
        r'StateTrackSound::|SoundManager::|SoundPlayer::|Light::|LightData::|'
        r'Actor3D::.*(Sound|Audio)|.*::(SetLight|SetAmbient|SetDiffuse|SetSpecular|SetShadow))')
    rows=[]
    for entry,name in zip(entries,names):
        if not target.search(name):continue
        ea=entry[1]&~1
        sections=[s for s in parsed['sections'] if s[3]=='__text' and s[0]<=ea<s[0]+s[1]]
        if not sections:continue
        section=sections[0]
        end=min(next((a for a in addresses if a>ea),section[0]+section[1]),section[0]+section[1])
        # n_desc's Thumb definition is authoritative; address low bits alone are insufficient.
        at=section[2]+ea-section[0]
        cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB if ea in thumb_addresses else capstone.CS_MODE_ARM);cs.detail=True
        instructions=list(cs.disasm(raw[at:at+min(end-ea,12000)],ea))
        calls=[];fields=[];constants=[]
        for ins in instructions:
            if ins.mnemonic in ('bl','blx','b') and ins.operands and ins.operands[0].type==arm.ARM_OP_IMM:
                destination=ins.operands[0].imm&~1
                if destination in symbols and destination!=ea:
                    calls.append(dict(offset=ins.address-ea,kind=ins.mnemonic,target=symbols[destination][:3]))
            if ins.mnemonic.startswith(('ldr','str')):
                for operand in ins.operands:
                    if operand.type==arm.ARM_OP_MEM and operand.mem.base and not operand.mem.index:
                        base=ins.reg_name(operand.mem.base)
                        if base not in ('pc','sp'):
                            fields.append((ins.mnemonic,base,operand.mem.disp))
            if ins.mnemonic in ('mov','mvn') and len(ins.operands)==2 and ins.operands[1].type==arm.ARM_OP_IMM:
                constants.append(ins.operands[1].imm)
        rows.append(dict(symbol=name,address=hex(ea),symbol_span_bytes=end-ea,
            instruction_mode='Thumb' if ea in thumb_addresses else 'ARM',instructions_decoded=len(instructions),truncated=end-ea>12000,
            opcode_counts=dict(collections.Counter(i.mnemonic for i in instructions)),
            direct_calls=calls[:120],memory_access_counts=[dict(operation=k[0],base=k[1],offset=k[2],count=v)
                for k,v in collections.Counter(fields).most_common(80)],
            immediate_values=sorted(set(constants))[:80],
            semantics_verified=False))
        if len(rows)>220:raise ValueError('Evidence method bound exceeded')
    related=collections.Counter(name.split('::',1)[0] for name in names
        if '::' in name and re.search(r'(Light|Shadow|Sound|Audio|Vox)',name))
    return dict(inspection_schema=2,related_native_class_counts=dict(related.most_common(160)),
                executable_sha256=module.hashlib.sha256(raw).hexdigest(),
                native_symbol_count=parsed['nsyms'],methods=rows,
                native_lighting_or_event_semantics_verified=False)


def main(output):
    report=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_only=True,owner_assets_published=False,device_tested=False)
    with tempfile.TemporaryDirectory(prefix='im2-owner-') as temporary:
        private=Path(temporary)
        # Reuse owner-provided inputs already present in the archival workflow;
        # never copy their identifiers into a report, command line or job log.
        workflow=(ROOT/'.github/workflows/g254-original-player-entitydata-transform-mc-source-no-vpk.yml').read_text()
        ids=re.findall(r"gdown '([^']+)'",workflow)
        link_file=private/'links';link_file.write_text('\n'.join(ids)+'\n');link_file.chmod(0o600)
        ipa=private/'owner.ipa'
        try:
            report['input']=dict(status='verified',**fetch(link_file,ipa))
        except Exception as error:
            report['input']=dict(status='unavailable',error_class=type(error).__name__)
        if ipa.exists():
            for label,action in (('native_structure',lambda:inspect(ipa)),
                                 ('original_audio_conversion',lambda:prepare(ipa,private/'assets'))):
                try:
                    with contextlib.redirect_stdout(io.StringIO()) as captured:
                        result=action()
                    report[label]=result if result is not None else json.loads(captured.getvalue())
                    report[label]['status']='passed'
                except Exception as error:
                    report[label]=dict(status='failed',error_class=type(error).__name__)
                    known=('Native 803x40 inline sound-name tables are absent or disagree',
                        'Previously native-referenced duplicate sound table mismatch',
                        'Unexpected source audio bank','RIFF size mismatch',
                        'Original WAV decoding failed','Unsafe original audio basename',
                        'Evidence method bound exceeded')
                    if str(error) in known:report[label]['diagnostic']=str(error)
    payload=json.dumps(report,indent=2)+'\n'
    if len(payload)>1500000 or 'https://' in payload or 'http://' in payload:
        raise ValueError('Report output policy exceeded')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(payload)
    print(json.dumps({k:(v.get('status') if isinstance(v,dict) else v)
                      for k,v in report.items() if k!='source_commit'}))


if __name__=='__main__':main(Path(sys.argv[1]))
