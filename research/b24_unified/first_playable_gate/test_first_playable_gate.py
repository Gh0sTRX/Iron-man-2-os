#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('first_playable_gate',HERE/'verify_first_playable_gate.py')
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
class GateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.current=json.loads((HERE/'first_playable_status.json').read_text())
 def test_current_blocked(self):
  self.assertFalse(gate.validate(self.current))
  self.assertEqual(self.current['wip_limit'],1)
  self.assertEqual(self.current['active_workstream'],'world_render_collision_hardware_parity')
 def test_refuse_source_only_false_pass(self):
  m=copy.deepcopy(self.current)
  m['criteria'][0]['state']='passed'
  with self.assertRaisesRegex(ValueError,'handheld proof'): gate.validate(m)
 def test_refuse_green_ci_as_device_qa(self):
  m=copy.deepcopy(self.current)
  m['release']['ready']=True
  with self.assertRaisesRegex(ValueError,'Release readiness'): gate.validate(m)
 def test_cannot_skip_fps_hardware(self):
  m=copy.deepcopy(self.current)
  m['criteria']=[x for x in m['criteria'] if x['id']!='device_performance']
  with self.assertRaisesRegex(ValueError,'Missing or extra'): gate.validate(m)
 def test_cannot_expand_wip(self):
  m=copy.deepcopy(self.current)
  m['wip_limit']=2
  with self.assertRaisesRegex(ValueError,'WIP limit'): gate.validate(m)
 def test_cannot_auto_issue_vpk(self):
  m=copy.deepcopy(self.current)
  m['release']['candidate_vpk_auto_allowed']=True
  with self.assertRaisesRegex(ValueError,'Never auto-generate'): gate.validate(m)
 def test_fake_device_record_rejected(self):
  m=copy.deepcopy(self.current)
  m['criteria'][0]['state']='passed'
  m['criteria'][0]['device_proof']={'hardware':'PS Vita'}
  with self.assertRaisesRegex(ValueError,'incomplete Vita device evidence'): gate.validate(m)
if __name__=='__main__': unittest.main()
