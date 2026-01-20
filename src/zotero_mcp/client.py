"""
Zotero client wrapper for MCP server.

Full local mode: Uses Local HTTP API for reads, Connector API for writes.
No cloud dependency required.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from pyzotero import zotero

logger = logging.getLogger(__name__)

from zotero_mcp.utils import format_creators, extract_year


load_dotenv()

# Zotero local endpoints
ZOTERO_LOCAL_API = "http://127.0.0.1:23119/api"
ZOTERO_CONNECTOR_API = "http://127.0.0.1:23119/connector"


@dataclass
class AttachmentDetails:
    """Details about a Zotero attachment."""
    key: str
    title: str
    filename: str
    content_type: str


def get_zotero_client() -> zotero.Zotero:
    """
    Get Zotero client for local operations.
    
    Always uses local API mode - requires Zotero Desktop running.
    
    Environment variables:
        ZOTERO_LIBRARY_ID: Library ID (default '0' for local)
        ZOTERO_LIBRARY_TYPE: 'user' or 'group' (default 'user')
    
    Returns:
        Configured Zotero client instance.
    """
    library_id = os.getenv("ZOTERO_LIBRARY_ID", "0")
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE", "user")
    
    return zotero.Zotero(
        library_id=library_id,
        library_type=library_type,
        api_key=None,
        local=True,
    )


def create_item_local(items: list[dict], timeout: float = 10.0) -> dict:
    """
    Create items via Zotero Connector API (local write).
    
    Uses /connector/saveItems endpoint which supports write operations.
    
    Args:
        items: List of item dictionaries to create.
        timeout: Request timeout in seconds.
    
    Returns:
        Result dictionary with success status.
    
    Raises:
        httpx.HTTPError: If the request fails.
        ConnectionError: If Zotero is not running.
    
    Environment variables:
        ZOTERO_CONNECTOR_LIBRARY_ID: Library ID for Connector API (default 1)
    """
    library_id = int(os.getenv("ZOTERO_CONNECTOR_LIBRARY_ID", "1"))
    payload = {
        "libraryID": library_id,
        "items": items,
    }
    
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                f"{ZOTERO_CONNECTOR_API}/saveItems",
                json=payload,
            )
            resp.raise_for_status()
            return {"success": True}
    except httpx.ConnectError:
        raise ConnectionError(
            "Cannot connect to Zotero. "
            "Ensure Zotero desktop is running with local API enabled."
        )
    except httpx.TimeoutException:
        raise TimeoutError(
            f"Request to Zotero timed out after {timeout} seconds. "
            "Try again or increase timeout."
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Zotero returned an error: {e.response.status_code} - {e.response.text}"
        )


def check_zotero_running() -> bool:
    """Check if Zotero desktop is running."""
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{ZOTERO_CONNECTOR_API}/ping")
            return "Zotero" in resp.text
    except Exception:
        return False


def format_item_metadata(item: dict[str, Any], include_abstract: bool = True) -> str:
    """
    Format a Zotero item's metadata as markdown.
    
    Args:
        item: Zotero item dictionary.
        include_abstract: Whether to include the abstract.
    
    Returns:
        Markdown-formatted metadata.
    """
    data = item.get("data", {})
    item_type = data.get("itemType", "unknown")
    
    lines = [
        f"# {data.get('title', 'Untitled')}",
        f"**Type:** {item_type}",
        f"**Key:** {data.get('key')}",
    ]
    
    if date := data.get("date"):
        lines.append(f"**Date:** {date}")
    
    if creators := data.get("creators", []):
        lines.append(f"**Authors:** {format_creators(creators)}")
    
    # Publication details
    if item_type == "journalArticle":
        if journal := data.get("publicationTitle"):
            info = f"**Journal:** {journal}"
            if volume := data.get("volume"):
                info += f", Vol. {volume}"
            if issue := data.get("issue"):
                info += f", No. {issue}"
            if pages := data.get("pages"):
                info += f", pp. {pages}"
            lines.append(info)
    elif item_type == "book":
        if publisher := data.get("publisher"):
            info = f"**Publisher:** {publisher}"
            if place := data.get("place"):
                info += f", {place}"
            lines.append(info)
    
    if doi := data.get("DOI"):
        lines.append(f"**DOI:** {doi}")
    
    if url := data.get("url"):
        lines.append(f"**URL:** {url}")
    
    if tags := data.get("tags"):
        tag_list = [f"`{t['tag']}`" for t in tags]
        if tag_list:
            lines.append(f"**Tags:** {' '.join(tag_list)}")
    
    if include_abstract and (abstract := data.get("abstractNote")):
        lines.extend(["", "## Abstract", abstract])
    
    if collections := data.get("collections", []):
        lines.append(f"**Collections:** {len(collections)}")
    
    if "meta" in item and item["meta"].get("numChildren", 0) > 0:
        lines.append(f"**Attachments/Notes:** {item['meta']['numChildren']}")
    
    return "\n\n".join(lines)


def generate_bibtex(item: dict[str, Any], slim: bool = True) -> str:
    """
    Generate BibTeX format for a Zotero item.
    
    Args:
        item: Zotero item data.
        slim: If True, exclude large fields (abstract, file, note) to save tokens.
    
    Returns:
        BibTeX formatted string.
    """
    data = item.get("data", {})
    item_type = data.get("itemType", "misc")
    item_key = data.get("key")
    
    if item_type in ("attachment", "note"):
        raise ValueError(f"Cannot export BibTeX for item type '{item_type}'")
    
    # Map Zotero types to BibTeX types
    type_map = {
        "journalArticle": "article",
        "book": "book",
        "bookSection": "incollection",
        "conferencePaper": "inproceedings",
        "thesis": "phdthesis",
        "report": "techreport",
        "webpage": "misc",
        "manuscript": "unpublished",
    }
    
    # Create citation key
    creators = data.get("creators", [])
    author = ""
    if creators:
        first = creators[0]
        name = first.get("name", "")
        last_name = name.split()[-1] if name.strip() else ""
        author = first.get("lastName", last_name).replace(" ", "")
    
    year = extract_year(data.get("date", ""))
    cite_key = f"{author}{year}_{item_key}"
    
    bib_type = type_map.get(item_type, "misc")
    lines = [f"@{bib_type}{{{cite_key},"]
    
    # Fields to include
    field_mappings = [
        ("title", "title"),
        ("publicationTitle", "journal"),
        ("volume", "volume"),
        ("issue", "number"),
        ("pages", "pages"),
        ("publisher", "publisher"),
        ("DOI", "doi"),
        ("url", "url"),
    ]
    
    if not slim:
        field_mappings.append(("abstractNote", "abstract"))
    
    for zotero_field, bibtex_field in field_mappings:
        if value := data.get(zotero_field):
            value = str(value).replace("{", "\\{").replace("}", "\\}")
            lines.append(f"  {bibtex_field} = {{{value}}},")
    
    # Add authors
    if creators:
        authors = []
        for creator in creators:
            if creator.get("creatorType") == "author":
                if "lastName" in creator and "firstName" in creator:
                    authors.append(f"{creator['lastName']}, {creator['firstName']}")
                elif "name" in creator:
                    authors.append(creator["name"])
        if authors:
            lines.append(f"  author = {{{" and ".join(authors)}}},")
    
    if year != "nodate":
        lines.append(f"  year = {{{year}}},")
    
    # Remove trailing comma
    if lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]
    lines.append("}")
    
    return "\n".join(lines)


def get_attachment_details(
    zot: zotero.Zotero,
    item: dict[str, Any]
) -> Optional[AttachmentDetails]:
    """
    Get the best attachment for a Zotero item.
    
    Prioritizes PDF over HTML over other types.
    
    Args:
        zot: Zotero client instance.
        item: Zotero item dictionary.
    
    Returns:
        AttachmentDetails if found, None otherwise.
    """
    data = item.get("data", {})
    item_type = data.get("itemType")
    item_key = data.get("key")
    
    # Direct attachment
    if item_type == "attachment":
        return AttachmentDetails(
            key=item_key,
            title=data.get("title", "Untitled"),
            filename=data.get("filename", ""),
            content_type=data.get("contentType", ""),
        )
    
    # Find child attachments
    try:
        children = zot.children(item_key)
        
        pdfs = []
        htmls = []
        others = []
        
        for child in children:
            child_data = child.get("data", {})
            if child_data.get("itemType") != "attachment":
                continue
            
            content_type = child_data.get("contentType", "")
            attachment = AttachmentDetails(
                key=child.get("key", ""),
                title=child_data.get("title", "Untitled"),
                filename=child_data.get("filename", ""),
                content_type=content_type,
            )
            
            if content_type == "application/pdf":
                pdfs.append(attachment)
            elif content_type.startswith("text/html"):
                htmls.append(attachment)
            else:
                others.append(attachment)
        
        # Return first match in priority order
        for category in [pdfs, htmls, others]:
            if category:
                return category[0]
    
    except Exception as e:
        # Log but don't fail - returning None is acceptable when attachment not found
        logger.debug(f"Failed to fetch children for item {item_key}: {e}")
    
    return None
