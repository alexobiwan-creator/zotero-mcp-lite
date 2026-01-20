"""
Tests for zotero_mcp.utils module.

Tests cover:
- format_creators: Creator name formatting
- clean_html: HTML tag removal
- text_to_html: Markdown/text to HTML conversion
"""

import unittest

from zotero_mcp.utils import clean_html, format_creators, text_to_html


class TestFormatCreators(unittest.TestCase):
    """Tests for format_creators function."""

    def test_with_first_last_name(self):
        """Standard format with firstName and lastName."""
        creators = [
            {"firstName": "John", "lastName": "Smith"},
            {"firstName": "Jane", "lastName": "Doe"},
        ]
        result = format_creators(creators)
        self.assertEqual(result, "Smith, John; Doe, Jane")

    def test_with_single_name(self):
        """Institutional or single name format."""
        creators = [{"name": "World Health Organization"}]
        result = format_creators(creators)
        self.assertEqual(result, "World Health Organization")

    def test_mixed_formats(self):
        """Mix of individual and institutional names."""
        creators = [
            {"firstName": "John", "lastName": "Smith"},
            {"name": "Research Institute"},
        ]
        result = format_creators(creators)
        self.assertEqual(result, "Smith, John; Research Institute")

    def test_empty_list(self):
        """Empty creator list returns default message."""
        result = format_creators([])
        self.assertEqual(result, "No authors listed")

    def test_ignores_unknown_fields(self):
        """Entries without recognized fields are skipped."""
        creators = [
            {"firstName": "John", "lastName": "Smith"},
            {"unknown": "value"},  # Should be ignored
        ]
        result = format_creators(creators)
        self.assertEqual(result, "Smith, John")


class TestCleanHtml(unittest.TestCase):
    """Tests for clean_html function."""

    def test_removes_simple_tags(self):
        """Removes basic HTML tags."""
        result = clean_html("<p>Hello</p>")
        self.assertEqual(result, "Hello")

    def test_removes_nested_tags(self):
        """Removes nested HTML tags."""
        result = clean_html("<div><p>Hello <strong>world</strong>!</p></div>")
        self.assertEqual(result, "Hello world!")

    def test_preserves_plain_text(self):
        """Plain text without tags remains unchanged."""
        result = clean_html("Hello world")
        self.assertEqual(result, "Hello world")

    def test_empty_string(self):
        """Empty string returns empty string."""
        result = clean_html("")
        self.assertEqual(result, "")

    def test_removes_self_closing_tags(self):
        """Removes self-closing tags like <br/>."""
        result = clean_html("Line1<br/>Line2")
        self.assertEqual(result, "Line1Line2")


class TestTextToHtml(unittest.TestCase):
    """Tests for text_to_html function - markdown to HTML conversion."""

    def test_simple_text_wrapped_in_p(self):
        """Simple text gets wrapped in paragraph tags."""
        result = text_to_html("Hello world")
        self.assertIn("<p>", result)
        self.assertIn("Hello world", result)

    def test_markdown_bold(self):
        """Markdown bold converts to strong/b tags."""
        result = text_to_html("This is **bold** text")
        self.assertTrue("<strong>" in result or "<b>" in result)

    def test_markdown_italic(self):
        """Markdown italic converts to em/i tags."""
        result = text_to_html("This is *italic* text")
        self.assertTrue("<em>" in result or "<i>" in result)

    def test_markdown_table(self):
        """Markdown tables convert to HTML tables."""
        markdown = "| Header 1 | Header 2 |\n|---|---|\n| Cell 1 | Cell 2 |"
        result = text_to_html(markdown)
        self.assertIn("<table>", result)
        self.assertIn("<th>", result)
        self.assertIn("<td>", result)

    def test_markdown_list(self):
        """Markdown lists convert to HTML lists."""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        result = text_to_html(markdown)
        self.assertIn("<ul>", result)
        self.assertIn("<li>", result)

    def test_markdown_headers(self):
        """Markdown headers convert to HTML headers."""
        result = text_to_html("## Section Title")
        self.assertIn("<h2>", result)

    def test_markdown_blockquote(self):
        """Markdown blockquotes convert to HTML blockquotes."""
        result = text_to_html("> This is a quote")
        self.assertIn("<blockquote>", result)

    def test_passthrough_existing_html_p(self):
        """Content with <p>...</p> structure passes through unchanged."""
        html = "<p>Already HTML</p>"
        result = text_to_html(html)
        self.assertEqual(result, html)

    def test_passthrough_existing_html_div(self):
        """Content with <div>...</div> structure passes through unchanged."""
        html = "<div>Content</div>"
        result = text_to_html(html)
        self.assertEqual(result, html)

    def test_passthrough_existing_html_table(self):
        """Content with <table>...</table> structure passes through unchanged."""
        html = "<table><tr><td>Cell</td></tr></table>"
        result = text_to_html(html)
        self.assertEqual(result, html)

    def test_passthrough_br_tag(self):
        """Content with <br/> passes through unchanged."""
        html = "Line 1<br/>Line 2"
        result = text_to_html(html)
        self.assertEqual(result, html)

    def test_empty_string(self):
        """Empty string returns empty string."""
        result = text_to_html("")
        self.assertEqual(result, "")

    def test_whitespace_only(self):
        """Whitespace-only string returns empty string."""
        result = text_to_html("   \n\n  ")
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
