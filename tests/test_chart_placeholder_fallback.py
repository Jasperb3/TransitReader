from transit_reader.main import _insert_chart_if_missing


def test_placeholder_present_is_unchanged():
    report = "# Report\n\n[transit_chart]\n\nBody text"
    result = _insert_chart_if_missing(report, "![Transit Chart](chart.png)")

    assert result == report


def test_placeholder_missing_inserted_after_h1():
    report = "# Report\n\nBody text with no placeholder"
    result = _insert_chart_if_missing(report, "![Transit Chart](chart.png)")

    assert result.startswith("# Report\n\n![Transit Chart](chart.png)")
    assert "Body text with no placeholder" in result


def test_placeholder_missing_no_h1_prepends():
    report = "Just some body text"
    result = _insert_chart_if_missing(report, "![Transit Chart](chart.png)")

    assert result.startswith("![Transit Chart](chart.png)")
    assert "Just some body text" in result
