import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from ui_asset_inventory import inspect, plausible_swf

class TestInventory(unittest.TestCase):
    def test_source_candidates_not_decoded_assets(self):
        with tempfile.TemporaryDirectory() as td:
            ipa=Path(td)/'synthetic.ipa'
            swf=b'FWS\x09' + (100).to_bytes(4,'little') + b'NOT_A_VALID_WHOLE_SWF'
            with ZipFile(ipa, 'w', ZIP_DEFLATED) as z:
                z.writestr('Payload/Game.app/main_menu.swf',swf)
                z.writestr('Payload/Game.app/packs/opaque.dat',b'XXXX'+swf+b'!')
                z.writestr('Payload/Game.app/textures/sprite.png',b'\x89PNG\r\n\x1a\nSAMPLE')
                z.writestr('Payload/Game.app/level1.bclara',b'not ui')
            res=inspect(ipa,1)
            rows={r['entry']:r for r in res['records']}
            self.assertEqual(res['entries'],4)
            self.assertEqual(rows['Payload/Game.app/main_menu.swf']['category'],'ui_extension')
            self.assertEqual(rows['Payload/Game.app/packs/opaque.dat']['magic_swf_offsets'],[4])
            self.assertEqual(rows['Payload/Game.app/packs/opaque.dat']['category'], 'embedded_swf_signature_candidate')
            self.assertEqual(rows['Payload/Game.app/level1.bclara']['category'],'other')
            self.assertTrue(plausible_swf(swf,0))
            self.assertFalse(plausible_swf(b'FWS\xff'+(100).to_bytes(4,'little'),0))

if __name__=='__main__':
    unittest.main()
