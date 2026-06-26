import importlib.util
from pathlib import Path


def test_script_entrypoints_import_without_errors():
    scripts_dir = Path("scripts")
    for script_path in sorted(scripts_dir.glob("*.py")):
        module_name = f"_script_smoke_{script_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)
