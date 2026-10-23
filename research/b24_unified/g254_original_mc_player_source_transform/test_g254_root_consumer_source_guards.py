#!/usr/bin/env python3
"""Synthetic reader regressions only; no IPA, native source or runtime proof.

Original-method identities come from earlier authenticated G254/G260
metadata. Fixture byte strings, method spans and opcode rows below are
deliberately synthetic and are never written as original-source artifacts.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("g254",HERE/"g254_original_2010_MC_LoadFromFile_Init_and_true_GamePlay_constructor_ARM.py")
reader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def synthetic_calls():
 return {
  "0xc2e8c":{"original_full_method_direct_call_metadata":[{
   "native_callsite_VM":"0xc36fc","real_callee_VM":"0xec108",
   "real_cpp_callee":["MainCharacter::MainCharacter()"]}]},
  "0xdbbe0":{"original_full_method_direct_call_metadata":[
   {"native_callsite_VM":"0xdbbf4","real_callee_VM":"0x139f0",
    "real_cpp_callee":["Entity3D::Init()"]},
   {"native_callsite_VM":"0xdbcbc","real_callee_VM":"0xa54fc",
    "real_cpp_callee":["WCollision::Init(Actor*, PositionData*)"]}]}}


class SyntheticRootReaderTests(unittest.TestCase):
 def test_production_fingerprint_is_exact_prior_source(self):
  self.assertEqual(reader.ORIGINAL_EXE_BYTES,7480208)
  self.assertEqual(reader.ORIGINAL_EXE_SHA256,
    "3ba6337a23ab7e08f2e025ec9731c53a7990e8d611b59eac07ba00cb63acc629")

 def test_same_size_changed_binary_is_rejected(self):
  synthetic=b"synthetic executable fixture"
  with mock.patch.object(reader,"ORIGINAL_EXE_BYTES",len(synthetic)), \
       mock.patch.object(reader,"ORIGINAL_EXE_SHA256",hashlib.sha256(synthetic).hexdigest()):
   self.assertEqual(reader.verify_executable(synthetic),hashlib.sha256(synthetic).hexdigest())
   with self.assertRaisesRegex(ValueError,"SHA256"):
    reader.verify_executable(synthetic[:-1]+b"!")
   with self.assertRaisesRegex(ValueError,"size"):
    reader.verify_executable(synthetic+b"!")

 def test_root_symbols_keep_existing_eight_methods(self):
  self.assertEqual(len(reader.METHODS),11)
  self.assertEqual(reader.ROOT_METHODS,{
   0x139f0:"Entity3D::Init()",0xa54fc:"WCollision::Init(Actor*, PositionData*)",
   0x12ea4:"Entity3D::GetPosition()"})
  self.assertEqual(reader.METHODS[0xc2e8c],"GS_GamePlay::LoadEntities()")
  self.assertEqual(reader.METHODS[0xdbbe0],"Actor::Init()")

 def test_method_identity_and_text_bounds_fail_closed(self):
  vm=0x139f0;name=reader.ROOT_METHODS[vm]
  section=(vm-16,128,0x200,"__text")
  names={vm:{name},vm+24:{"synthetic_next_symbol"}}
  self.assertEqual(reader.method_span(vm,name,names,[section]),(0x210,24))
  with self.assertRaisesRegex(ValueError,"address drift"):
   reader.method_span(vm,name,{vm:{"wrong synthetic identity"}},[section])
  with self.assertRaisesRegex(ValueError,"text section"):
   reader.method_span(vm,name,names,[(0,128,0,"__text")])
  with self.assertRaisesRegex(ValueError,"unexpectedly sized"):
   reader.method_span(vm,name,{vm:{name},vm+3:{"synthetic_short"}},[section])
  with self.assertRaisesRegex(ValueError,"unexpectedly sized"):
   reader.method_span(vm,name,{vm:{name}},[(vm,reader.MAX_METHOD_BYTES+4,0,"__text")])

 def test_new_body_window_is_bounded_and_legacy_selection_remains(self):
  rows=[SimpleNamespace(address=0xc3600+i*4) for i in range(700)]
  for vm in reader.ROOT_METHODS:
   self.assertEqual(len(reader.select_window(vm,rows)),512)
  self.assertEqual(len(reader.select_window(0xdbbe0,rows)),260)
  self.assertIs(reader.select_window(0xec2cc,rows),rows)
  window=reader.select_window(0xc2e8c,rows)
  self.assertEqual(window[0].address,0xc36b0)
  self.assertEqual(window[-1].address,0xc3850)

 def test_absolute_getter_discovery_is_exact_and_bounded(self):
  symbols={1:{"Entity3D::GetAbsolutePosition()"},
           2:{"Actor::GetAbsolutePosition() const"},
           3:{"MainCharacter::GetPosition()"},
           4:{"PositionDummyEntity::GetAbsolutePosition()"}}
  found,total=reader.absolute_position_candidates(symbols)
  self.assertEqual(total,2)
  self.assertEqual([x["original_VM"] for x in found],["0x1","0x2"])
  self.assertEqual(reader.absolute_position_candidates({}),([],0))
  many={i:{f"Entity3D::GetAbsolutePosition(synthetic_{i})"}
        for i in range(reader.ABSOLUTE_SYMBOL_LIMIT+2)}
  found,total=reader.absolute_position_candidates(many)
  self.assertEqual(total,reader.ABSOLUTE_SYMBOL_LIMIT+2)
  self.assertEqual(len(found),reader.ABSOLUTE_SYMBOL_LIMIT)

 def test_required_call_chain_rejects_wrong_target_and_missing_call(self):
  calls=synthetic_calls()
  reader.verify_call_chain(calls)
  wrong=copy.deepcopy(calls)
  wrong["0xdbbe0"]["original_full_method_direct_call_metadata"][1]["real_callee_VM"]="0xa54f8"
  with self.assertRaisesRegex(ValueError,"call chain missing"):
   reader.verify_call_chain(wrong)
  missing=copy.deepcopy(calls)
  missing["0xdbbe0"]["original_full_method_direct_call_metadata"].pop()
  with self.assertRaisesRegex(ValueError,"call chain missing"):
   reader.verify_call_chain(missing)

 def test_private_log_records_have_bounded_parseable_source_fields(self):
  methods={}
  for vm in reader.ROOT_METHODS:
   methods[hex(vm)]={"source_actual_ARM_instruction_count":700,
    "source_window_emitted_instructions":reader.ROOT_BODY_LIMIT,
    "source_window_truncated":True,
    "native_original_source_active_constructor_or_data_window":[
     {"original_VM":hex(vm+i*4),"op":"nop","args":""}
     for i in range(reader.ROOT_BODY_LIMIT)]}
  output=io.StringIO()
  with contextlib.redirect_stdout(output):reader.emit_root_bodies(methods)
  lines=output.getvalue().splitlines()
  self.assertEqual(len(lines),3*(reader.ROOT_BODY_LIMIT+1))
  summaries=[]
  for line in lines:
   marker,payload=line.split(" ",1)
   row=json.loads(payload)
   self.assertIn(marker,("G254_ROOT_METHOD","G254_ROOT_INSTRUCTION"))
   if marker=="G254_ROOT_METHOD":summaries.append(row)
  self.assertTrue(all(x["window_truncated"] for x in summaries))
  methods[hex(next(iter(reader.ROOT_METHODS)))]["native_original_source_active_constructor_or_data_window"].append({})
  with self.assertRaisesRegex(ValueError,"exceeds source bound"):
   reader.emit_root_bodies(methods)


if __name__=="__main__":
 unittest.main(verbosity=2)
