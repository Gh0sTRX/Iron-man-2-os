import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from original_ui_asset_probe import plausible_swf, probe, report
class GuiProbeTests(unittest.TestCase):
    def test_valid_and_invalid_swf_headers(self):
        swf=b'FWS'+bytes((9,))+(32).to_bytes(4,'little')+b'\x58'
        self.assertEqual(plausible_swf(swf,0)['format'],'SWF uncompressed')
        self.assertIsNone(plausible_swf(b'FWS'+b'\xff'+(32).to_bytes(4,'little'),0))
        self.assertIsNone(plausible_swf(b'FWS'+bytes((9,))+(999999999).to_bytes(4,'little'),0))
    def test_zip_candidates_and_overlap(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'synthetic.ipa'
            swf=b'FWS'+bytes((9,))+(120).to_bytes(4,'little')+b'\x58'+bytes(31)
            with ZipFile(file,'w',ZIP_DEFLATED) as z:
                z.writestr('Payload/IronMan2.app/menus/game_main.swf',swf)
                z.writestr('Payload/IronMan2.app/gui.pvr',b'PVR\x03'+bytes(16))
                z.writestr('Payload/IronMan2.app/something.bin',b'x'*(1024*1024-4)+swf)
                z.writestr('Payload/IronMan2.app/noise.bin',b'FWS'+bytes((4,))+bytes(15))
            rows=probe(file)
            self.assertEqual(len([x for x in rows if x['category']=='top-level SWF']),1)
            self.assertEqual(len([x for x in rows if x['category']=='embedded SWF header']),1)
            self.assertTrue(any(x['category']=='named candidate' and x['path'].endswith('.pvr') for x in rows))
            self.assertFalse(any(x['path'].endswith('noise.bin') for x in rows))
            stats=report(file,Path(directory)/'out')
            self.assertEqual(stats['top_level_swf'],1)
            self.assertTrue((Path(directory)/'out'/'UI_ASSET_CANDIDATES.csv').is_file())
if __name__=='__main__':unittest.main()
