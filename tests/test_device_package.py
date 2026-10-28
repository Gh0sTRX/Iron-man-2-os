"""Source-only negative package checks with synthetic metadata and payloads."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import warnings
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('diagnostic_package',ROOT/'tools/device_test/build.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def sfo(version=module.VERSION,title='IM2DG0001'):
    keys=b'TITLE_ID\0APP_VER\0';start=52;values=(start+len(keys)+3)&~3
    a=title.encode()+b'\0';b=version.encode()+b'\0'
    data=struct.pack('<5I',0x46535000,0x101,start,values,2)
    data+=struct.pack('<HHIII',0,0x204,len(a),16,0)
    data+=struct.pack('<HHIII',9,0x204,len(b),8,16)
    return data+keys+b'\0'*(values-start-len(keys))+a.ljust(16,b'\0')+b.ljust(8,b'\0')


class PackageBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='im2-package-test-')
        self.path=Path(self.temp.name)/'synthetic.vpk'
        self.self_bytes=b'SCE\0synthetic-not-a-real-vita-self'
        self.self_sha=hashlib.sha256(self.self_bytes).hexdigest()
        self.resource=b'explicit synthetic resource'
        self.files={'data/source_tables.im2d':hashlib.sha256(self.resource).hexdigest()}

    def tearDown(self):self.temp.cleanup()

    def write_package(self,metadata=None,resource=None,extra=None):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            with zipfile.ZipFile(self.path,'w') as archive:
                archive.writestr('eboot.bin',self.self_bytes)
                archive.writestr('sce_sys/param.sfo',metadata if metadata is not None else sfo())
                archive.writestr('data/source_tables.im2d',resource if resource is not None else self.resource)
                if extra:archive.writestr(extra,b'synthetic')

    def verify(self):return module.verify_vpk(self.path,self.files,self.self_sha)

    def test_exact_inventory_and_metadata(self):
        self.write_package();self.assertEqual(self.verify()['APP_VER'],module.VERSION)

    def test_stale_version_or_wrong_installed_title(self):
        for metadata in (sfo(version='00.01'),sfo(version='00.02'),sfo(title='IM2DIFF01')):
            self.write_package(metadata=metadata)
            with self.assertRaises(ValueError):self.verify()

    def test_hash_mismatch_is_not_accepted_as_current_data(self):
        self.write_package(resource=b'changed original input')
        with self.assertRaises(ValueError):self.verify()
        self.write_package();self.self_sha='0'*64
        with self.assertRaises(ValueError):self.verify()

    def test_duplicate_unexpected_and_traversing_paths(self):
        for extra in ('eboot.bin','unexpected.bin','../outside.bin','/absolute.bin','data\\unsafe.bin'):
            self.write_package(extra=extra)
            with self.assertRaises(ValueError):self.verify()

    def test_bounded_sfo_rejects_truncated_tables(self):
        raw=sfo()
        for bad in (b'',b'\0'*20,raw[:51],raw[:-1]):
            with self.assertRaises(ValueError):module.sfo_strings(bad)


if __name__=='__main__':unittest.main(verbosity=2)
