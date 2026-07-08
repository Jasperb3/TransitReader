import subprocess
import sys


def test_import_models_does_not_prompt():
    result = subprocess.run(
        [sys.executable, "-c", "import transit_reader.utils.models"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
