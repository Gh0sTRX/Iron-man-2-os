#!/usr/bin/env python3
"""Read owner-provided iOS 2010 Iron Man 2 Level1 Lua instruction metadata.
This decodes PC70..85 to resolve what PC75-78 actually does and where
PC79 resumes. Never ships IPA, original bytecode or original assets.
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[0]))
from b24_owner_pack_extract import decode,get_exact
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER,report

OPS=['MOVE','LOADK','LOADBOOL','LOADNIL','GETUPVAL','GETGLOBAL',
'GETTABLE','SETGLOBAL','SETUPVAL','SETTABLE','NEWTABLE','SELF',
'ADD','SUB','MUL','DIV','MOD','POW','UNM','NOT','LEN','CONCAT',
'JMP','EQ','LT','LE','TEST','TESTSET','CALL','TAILCALL','RETURN',
'FORLOOP','FORPREP','TFORLOOP','SETLIST','CLOSE','CLOSURE','VARARG']

def parse(word,constants):
    op=word&63
    if op>=len(OPS):
        raise ValueError('unsupported native Lua opcode')
    a=(word>>6)&255
    b=(word>>23)&511
    c=(word>>14)&511
    bx=(word>>14)&262143
    sbx=bx-131071
    p={'op':OPS[op],'a':a,'b':b,'c':c,'bx':bx,'sbx':sbx}
    if op in (5,7): # GETGLOBAL, SETGLOBAL use ABx
        if bx>=len(constants) or not isinstance(constants[bx],str):
            raise ValueError('original Lua global name not string constant')
        name=constants[bx]
        # API function identifiers are not game's dialogue/content.
        p['global_identifier']=name if len(name)<=80 else '(long global)'
    if op==1:
        if bx>=len(constants):
            raise ValueError('source constant index out of range')
        v=constants[bx]
        p['load_constant_type']=(
            'boolean' if isinstance(v,bool) else 'number' if isinstance(v,(float,int))
            else 'nil' if v is None else 'string')
        if isinstance(v,(float,int,bool)):
            p['load_constant_value']=v
    if op==2:
        p['load_boolean_value']=bool(b)
        p['skip_next_instruction']=bool(c)
    if op==23: # Lua 5.1 EQ compares RK(B) and RK(C)
        p['compare_RK_B']=('R'+str(b) if b<256 else 'K'+str(b-256))
        p['compare_RK_C']=('R'+str(c) if c<256 else 'K'+str(c-256))
        if c>=256 and c-256<len(constants) and isinstance(constants[c-256],bool):
            p['compare_bool_value_C']=constants[c-256]
    if op==22:
        p['jump_target_PC']=sbx # caller adds PC+1
    if op==28:
        p['lua_arg_count']=b-1 if b>0 else 'variable'
        p['lua_return_count']=c-1 if c>0 else 'variable'
    # Never output raw word/bytecode or source dialogue.
    return p

def run(ipa,out):
    if ipa.stat().st_size!=248613763:
        raise ValueError('2010 user original iOS IPA length must match')
    with zipfile.ZipFile(ipa) as z:
        data=z.read('Payload/IronMan2.app/clev')
        raw=get_exact(data,decode(data,'.bclara'),'level1.bclara')
    rows=report(raw)['source_lua_static_CALLBACK_instructions_and_id_links']
    intro=next(r for r in rows if r['original_callback']=='Mission000_OnStart')
    n=NativeLua(raw,intro['original_source_callback_offset'])
    assert n.fetch(12)==HEADER
    proto=n.function()['original_child_functions'][0]
    code=proto['native_function_code']
    constants=proto['native_constants']
    assert len(code)==937
    instr={str(pc):parse(code[pc],constants) for pc in range(68,86)}
    assert instr['71']['op']=='GETGLOBAL'
    assert instr['71']['global_identifier']=='IsTutConfirmed'
    assert instr['72']['op']=='CALL' and instr['72']['lua_return_count']==1
    assert instr['73']['op']=='EQ' and instr['73']['a']==0
    assert instr['73']['b']==instr['72']['a']
    assert instr['73']['compare_bool_value_C'] is False
    assert instr['74']['op']=='JMP' and 75+instr['74']['sbx']==79
    assert instr['78']['op']=='JMP' and 79+instr['78']['sbx']==71
    # Verify the 75/76/77 instructions have been exported as metadata,
    # but do NOT assume Wait() or any actor side effect before inspection.
    assert set(['75','76','77']).issubset(instr)
    out.parent.mkdir(parents=True,exist_ok=True)
    result={'source':'original owner 2010 level1 Mission000 Lua metadata',
        'original_total_lua_instructions':len(code),
        'source_instructions_PC68_to_85':instr,
        'source_PC73_false_path_entry':75,
        'source_PC73_true_path_entry':79,
        'source_PC78_jmp_back_to':71,
        'source_complete_runtime_VM_implemented':False,
        'new_VPK':False}
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('G151 authentic original Lua PC68-85:')
    for pc in range(68,86):
        print('PC',pc,instr[str(pc)])
    print('G151 original PC73 EQ false/true branch metadata verified; NO VPK')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--ipa',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    run(a.ipa,a.out)
