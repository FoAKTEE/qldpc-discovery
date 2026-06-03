"""Make `import qcode_discovery` resolve to ./src for in-tree test runs (no install needed).

The package lives directly in `src/` (one source folder, mirroring `julia/src/`) and is mapped to
the name `qcode_discovery` by pyproject's `package_dir`; this conftest mirrors that mapping for pytest.
"""
import importlib.util
import sys
from pathlib import Path

_src = Path(__file__).parent / "src"
if "qcode_discovery" not in sys.modules:
    _spec = importlib.util.spec_from_file_location(
        "qcode_discovery", _src / "__init__.py", submodule_search_locations=[str(_src)]
    )
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["qcode_discovery"] = _mod
    _spec.loader.exec_module(_mod)
