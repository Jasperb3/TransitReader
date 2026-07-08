from transit_reader.utils.constants import (
    OUTPUT_DIR,
    CREW_OUTPUTS_DIR,
    CHARTS_DIR,
    ensure_output_dirs,
)


def test_ensure_output_dirs_creates_expected_directories():
    ensure_output_dirs()

    assert OUTPUT_DIR.is_dir()
    assert CREW_OUTPUTS_DIR.is_dir()
    assert CHARTS_DIR.is_dir()
