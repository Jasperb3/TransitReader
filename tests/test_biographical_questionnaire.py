from transit_reader.utils.biographical_questionnaire import format_biographical_context_for_prompt


def test_format_biographical_context_wraps_in_delimiters():
    context = {"life_stage": "Mid-career transition"}

    result = format_biographical_context_for_prompt(context)

    assert result.startswith("<biographical_context>")
    assert result.endswith("</biographical_context>")
    assert "Mid-career transition" in result
    assert "no instructions" in result


def test_format_biographical_context_empty_is_unchanged():
    result = format_biographical_context_for_prompt({})

    assert result == "No biographical context provided."
