"""Tests for Pass 1 LLM JSON parsing."""

from kgraph.pipeline.pass1_llm import _parse_json_from_text


class TestParseJsonFromText:
    """Test _parse_json_from_text handles braces inside strings."""

    def test_simple_object(self):
        """Basic JSON object parses."""
        out = _parse_json_from_text('{"a": 1, "b": 2}')
        assert out == {"a": 1, "b": 2}

    def test_braces_in_string_value(self):
        """Braces inside string values are ignored by depth counter."""
        text = '{"text": "The {gene} increases risk of {disease}"}'
        out = _parse_json_from_text(text)
        assert out == {"text": "The {gene} increases risk of {disease}"}

    def test_closing_brace_in_string(self):
        """Closing brace inside string does not end the object."""
        text = '{"note": "See Figure 1}"}'
        out = _parse_json_from_text(text)
        assert out == {"note": "See Figure 1}"}

    def test_escaped_quote_in_string(self):
        """Escaped quotes inside string do not toggle string state."""
        text = r'{"text": "He said \"hello\""}'
        out = _parse_json_from_text(text)
        assert out == {"text": 'He said "hello"'}

    def test_strips_markdown_code_block(self):
        """Markdown code block wrapper is stripped."""
        text = '```json\n{"x": 1}\n```'
        out = _parse_json_from_text(text)
        assert out == {"x": 1}

    def test_nested_object_with_string_braces(self):
        """Nested objects with braces in inner strings parse correctly."""
        text = '{"entities": [{"name": "BRCA2", "text": "gene {mutation}"}]}'
        out = _parse_json_from_text(text)
        assert out["entities"][0]["text"] == "gene {mutation}"
