import importlib.util
import io
from pathlib import Path
import struct
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audio_prepare',ROOT/'tools/prepare_audio_assets.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class AudioPreparationTests(unittest.TestCase):
    def test_real_riff_structure_and_bounds(self):
        # Explicit synthetic PCM WAV, not a substitute original effect.
        f=io.BytesIO()
        with wave.open(f,'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(b'\0\0'*2205)
        raw=f.getvalue();info=module.riff_info(raw)
        self.assertEqual((info['codec'],info['channels'],info['hz']),(1,1,22050))
        for bad in (b'',raw[:-1],raw+b'x',raw[:12]+b'data'+b'\xff'*4+raw[20:]):
            with self.assertRaises(ValueError):module.riff_info(bad)

    def test_native_pointer_lane_has_to_match_both_anchors_and_every_file(self):
        # Synthetic Mach-O and native-name lane: structural algorithm proof only.
        names=[f'fixture_{i}.www' for i in range(803)]
        names[87]='m_pre_cutscene_intro.www';names[319]='vfx_intro_level1_jarvis_1.www'
        first=256;pool_at=first+803*40;data=bytearray(pool_at)
        pointers=[]
        for name in names:
            pointers.append(0x1000+len(data));data.extend(name.encode()+b'\0')
        struct.pack_into('<7I',data,0,0xfeedface,12,0,2,1,56,0)
        struct.pack_into('<II16s8I',data,28,1,56,b'__DATA',0x1000,len(data),0,len(data),7,3,0,0)
        for i,pointer in enumerate(pointers):struct.pack_into('<I',data,first+i*40,pointer)
        recovered,at=module.sound_ordinals(data,names)
        self.assertEqual((recovered,at),(names,first))
        struct.pack_into('<I',data,first+319*40,pointers[1])
        with self.assertRaises(ValueError):module.sound_ordinals(data,names)

    def test_catalog_preserves_ordinals_and_rejects_paths(self):
        rows=[f'fixture_{i}.www' for i in range(803)]
        data=module.catalog(rows)
        self.assertEqual(struct.unpack_from('<4sII',data),(b'IM2A',1,803))
        rows[5]='../escape.www'
        with self.assertRaises(ValueError):module.catalog(rows)

if __name__=='__main__':unittest.main(verbosity=2)
