import re

import mistune

_HTML_TAG_RE = re.compile(r"<.*?>")
# Pattern to detect actual HTML structure - requires closing tag or self-closing
# Matches: <p>, <p class="x">, <br/>, <br /> but NOT: <p> as plain text mention
_HTML_STRUCTURE_RE = re.compile(
    r"<(p|div|span|br|h[1-6]|ul|ol|li|a|strong|em|b|i|table|tr|td|th)(?:\s[^>]*)?>.*?</\1>|<br\s*/?>",
    re.IGNORECASE | re.DOTALL
)

# Markdown renderer with table and strikethrough support
_markdown = mistune.create_markdown(plugins=['table', 'strikethrough'])


def extract_year(date_str: str) -> str:
    """
    Extract 4-digit year from various date formats.
    
    Handles formats like:
    - "2024-08-01"
    - "2024/03/01"
    - "10 月 22, 2021" (Chinese format)
    - "2021"
    - "March 2024"
    
    Args:
        date_str: Date string in any format.
    
    Returns:
        4-digit year string, or "nodate" if not found.
    """
    if not date_str:
        return "nodate"
    
    # Find a 4-digit year (1900-2099) anywhere in the string
    match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if match:
        return match.group(0)
    
    return "nodate"


def format_creators(creators: list[dict[str, str]]) -> str:
    """
    Format creator names into a string.

    Args:
        creators: List of creator objects from Zotero.

    Returns:
        Formatted string with creator names.
    """
    names = []
    for creator in creators:
        if "firstName" in creator and "lastName" in creator:
            names.append(f"{creator['lastName']}, {creator['firstName']}")
        elif "name" in creator:
            names.append(creator["name"])
    return "; ".join(names) if names else "No authors listed"


def clean_html(raw_html: str) -> str:
    """
    Remove HTML tags from a string.

    Args:
        raw_html: String containing HTML content.

    Returns:
        Cleaned string without HTML tags.
    """
    return re.sub(_HTML_TAG_RE, "", raw_html)


def text_to_html(content: str) -> str:
    """
    Convert text/markdown to HTML for Zotero notes.

    Handles:
    - Markdown tables, lists, bold, italic, headers, blockquotes
    - Plain text with line breaks
    - Already-formatted HTML (passed through unchanged)

    Args:
        content: Plain text, markdown, or HTML content.

    Returns:
        HTML-formatted string suitable for Zotero notes.
    """
    if not content or not content.strip():
        return ""
    
    # Check for actual HTML structure - pass through unchanged
    if _HTML_STRUCTURE_RE.search(content):
        return content
    
    # Convert markdown to HTML using mistune
    return _markdown(content)
