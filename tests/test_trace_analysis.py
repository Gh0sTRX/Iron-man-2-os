from pathlib import Path
import csv
import importlib.util
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('analysis',ROOT/'tools/analyze_frame_trace.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class TraceAnalysisTests(unittest.TestCase):
    def test_actual_c_writer_output(self):
        import sys
        result=module.analyze(sys.argv[-1])
        self.assertEqual(result['sampled_rows'],4096)
        self.assertEqual(result['world_controls_dt_difference_rows'],4096)
        self.assertEqual(result['unpaused_world_dt_reduced_rows'],4096)
        self.assertEqual(result['max_world_gpu_root_distance'],0)
        self.assertFalse(result['gpu_busy_available'])

    def test_z_difference_and_bad_time_are_visible(self):
        import sys
        with Path(sys.argv[-1]).open() as source:
            reader=csv.DictReader(source);fieldnames=reader.fieldnames;row=next(reader)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'test.csv'
            row['gpu_z']='8' # writer fixture world Z=-4; XY unchanged
            def write(rows):
                with p.open('w',newline='') as target:
                    w=csv.DictWriter(target,fieldnames=fieldnames);w.writeheader();w.writerows(rows)
            write([row])
            self.assertEqual(module.analyze(p)['max_world_gpu_root_distance'],12)
            bad=dict(row,raw_dt_ms='nan');write([bad])
            with self.assertRaises(ValueError):module.analyze(p)
            write([row,row])
            with self.assertRaises(ValueError):module.analyze(p)

if __name__=='__main__':
    unittest.main(argv=[__file__],verbosity=2)
