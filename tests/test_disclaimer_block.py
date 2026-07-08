import inspect

from transit_reader.main import DISCLAIMER_BLOCK, TransitFlow


def test_disclaimer_block_content():
    assert "not a" in DISCLAIMER_BLOCK
    assert "substitute" in DISCLAIMER_BLOCK
    assert "professional" in DISCLAIMER_BLOCK.lower()


def test_save_transit_analysis_appends_disclaimer():
    source = inspect.getsource(TransitFlow.save_transit_analysis)
    assert "DISCLAIMER_BLOCK" in source
