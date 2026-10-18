#!/usr/bin/env python3
"""Host-only fixture validates G229's real-G227 anchor patch and fail-closed rules."""
import tempfile
from pathlib import Path
from g229_install_window_into_real_vita_main import run

def mock_main():
    return '''#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"
B24G227GroundProbe b24_g227_probe={0}; /* one read-only snapshot per game frame */
b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx);
b24_g227_probe.frame_num=(uint32_t)frame;
b24_g227_qa_classify(&b24_g227_probe);
#endif
'''

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        path = root / 'work/src/main.c'
        cm = root / 'work/CMakeLists.txt'
        path.parent.mkdir(parents=True)
        cm.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(mock_main())
        cm.write_text('option(B24_G227_WALK_ROOT_DIAGNOSTIC "QA" OFF)\n')
        run(root)
        revised=path.read_text()
        assert revised.count('b24_g229_window_push(')==1
        assert revised.count('b14_world_tick(')==1
        assert revised.count('b24_gpu_runtime_draw(')==1
        assert 'B24G229WalkWindow b24_g229_window' in revised
        assert (root / 'work/b24/b24_unified/b24_g229_ground_trajectory_window.h').exists()
        try:
            run(root)
            assert False, 'double-install should fail'
        except ValueError as e:
            assert 'already installed' in str(e)
        assert revised == path.read_text(), 'fail-closed mutated file'
        # Test missing GPU owner never mutates file or creates source.
        path.write_text(mock_main().replace('b24_gpu_runtime_draw(', 'unknown_gpu('))
        try:
            run(root)
            assert False, 'missing source anchor should fail'
        except ValueError as e:
            assert 'single-owner' in str(e)
        assert path.read_text() == mock_main().replace('b24_gpu_runtime_draw(', 'unknown_gpu(')
    print('G229 PY HOST PASS: true G227 fixture patched, world/GPU single owner, duplicate/missing anchors fail-closed. NO VPK.')

if __name__=='__main__':
    main()
