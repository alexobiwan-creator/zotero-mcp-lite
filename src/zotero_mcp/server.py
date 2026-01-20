"""
Zotero MCP Lite server implementation.

A lightweight Model Context Protocol (MCP) server for Zotero reference management.
Provides 10 atomic tools and 4 research prompts for academic literature workflows.

Architecture:
    - Read Operations: Via Zotero Local HTTP API (/api/)
    - Write Operations: Via Zotero Connector API (/connector/)
    - Annotation Queries: Direct SQLite access for performance

Tools (11):
    Workflow: suggest_workflow
    Search & Navigation: search_items, get_recent, get_collections, 
                        get_collection_items, search_annotations
    Content Reading: get_item_metadata, get_item_children, get_item_fulltext
    Writing: create_note, create_review

Prompts (4):
    - knowledge_discovery: Cross-library topic exploration
    - literature_review: Deep single-paper academic analysis
    - comparative_review: Multi-paper synthesis and comparison
    - bibliography_export: Citation and BibTeX generation
"""

from typing import Any, Literal, Optional
import os

from fastmcp import Context, FastMCP

from zotero_mcp.client import (
    get_zotero_client,
    format_item_metadata,
    get_attachment_details,
    create_item_local,
)
from zotero_mcp.config import load_prompt, load_template
from zotero_mcp.template_engine import render_review, build_metadata_dict
from zotero_mcp.utils import format_creators, clean_html, text_to_html


mcp = FastMCP("Zotero")


# -----------------------------------------------------------------------------
# Workflow Discovery Tool
# -----------------------------------------------------------------------------

@mcp.tool(
    name="zotero_suggest_workflow",
    description=(
        "Get the recommended prompt for a research task. "
        "Returns which slash command the user should invoke."
    )
)
def suggest_workflow(
    task: str,
    *,
    ctx: Context
) -> str:
    """Suggest which prompt to use for a research task."""
    task_lower = task.lower()
    
    workflows = {
        "literature_review": {
            "triggers": ["literature review", "review paper", "analyze paper", "paper analysis", "single paper", "review"],
            "command": "/literature_review",
            "description": "Deep academic analysis of a single paper",
            "usage": "/literature_review <item_key>",
        },
        "comparative_review": {
            "triggers": ["comparative", "compare papers", "multiple papers", "synthesis", "comparison"],
            "command": "/comparative_review",
            "description": "Synthesize and compare multiple papers",
            "usage": "/comparative_review <item_key1> <item_key2> ...",
        },
        "bibliography": {
            "triggers": ["bibliography", "citation", "bibtex", "reference list", "cite"],
            "command": "/bibliography_export",
            "description": "Export formatted citations and BibTeX",
            "usage": "/bibliography_export <item_key1> <item_key2> ...",
        },
        "discovery": {
            "triggers": ["explore", "discover", "find related", "knowledge", "topic"],
            "command": "/knowledge_discovery",
            "description": "Explore your knowledge base on a topic",
            "usage": "/knowledge_discovery <query>",
        }
    }
    
    # Find matching workflow
    for name, workflow in workflows.items():
        if any(trigger in task_lower for trigger in workflow["triggers"]):
            return f"""# Recommended: {workflow['description']}

Please ask the user to invoke:

**{workflow['usage']}**

This prompt provides structured guidance for the task."""
    
    # No specific match - list all available
    return """# Available Research Prompts

Ask the user to invoke one of these:

- `/literature_review <item_key>` - Deep analysis of a single paper
- `/comparative_review <item_keys>` - Compare multiple papers
- `/bibliography_export <item_keys>` - Export citations and BibTeX
- `/knowledge_discovery <query>` - Explore knowledge base"""


# -----------------------------------------------------------------------------
# Search & Navigation Tools (6)
# -----------------------------------------------------------------------------

@mcp.tool(
    name="zotero_search_items",
    description=(
        "Search your reference library for papers, articles, books, or notes by keyword. "
        "Default searches title/author/year; use qmode='everything' to search full text and note contents. "
        "Returns item keys for get_item_metadata (details) or get_item_children (highlights/notes). "
        "TIP: For literature review or comparative analysis, call zotero_suggest_workflow first."
    )
)
def search_items(
    query: str,
    qmode: Literal["titleCreatorYear", "everything"] = "titleCreatorYear",
    item_type: str = "-attachment",
    limit: int = 10,
    tag: Optional[list[str]] = None,
    *,
    ctx: Context
) -> str:
    """Search for items in Zotero library."""
    try:
        if not query.strip():
            return "Error: Search query cannot be empty"
        
        ctx.info(f"Searching Zotero for '{query}'")
        zot = get_zotero_client()
        
        tag = tag or []
        zot.add_parameters(q=query, qmode=qmode, itemType=item_type, limit=limit, tag=tag)
        results = zot.items()
        
        if not results:
            return f"No items found matching query: '{query}'"
        
        output = [f"# Search Results for '{query}'", ""]
        
        for i, item in enumerate(results, 1):
            data = item.get("data", {})
            output.append(f"## {i}. {data.get('title', 'Untitled')}")
            output.append(f"**Key:** {item.get('key', '')}")
            output.append(f"**Type:** {data.get('itemType', 'unknown')}")
            output.append(f"**Date:** {data.get('date', 'No date')}")
            output.append(f"**Authors:** {format_creators(data.get('creators', []))}")
            
            if tags := data.get("tags"):
                tag_list = [f"`{t['tag']}`" for t in tags]
                output.append(f"**Tags:** {' '.join(tag_list)}")
            
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        ctx.error(f"Error searching Zotero: {e}")
        return f"Error searching Zotero: {e}"


@mcp.tool(
    name="zotero_get_recent",
    description=(
        "Get recently read, modified, or imported papers from your library. "
        "Default shows papers only; use item_type='' to include standalone notes. "
        "Use sort_by='dateAdded' for new imports, 'dateModified' for recent reading activity."
    )
)
def get_recent(
    limit: int = 10,
    sort_by: Literal["dateModified", "dateAdded"] = "dateModified",
    item_type: str = "-attachment -note",
    *,
    ctx: Context
) -> str:
    """Get recently added/modified items."""
    try:
        sort_label = "Modified" if sort_by == "dateModified" else "Added"
        ctx.info(f"Fetching {limit} recent items by {sort_by}")
        zot = get_zotero_client()
        
        limit = max(1, min(limit, 100))
        items = zot.items(limit=limit, sort=sort_by, direction="desc", itemType=item_type or None)
        
        if not items:
            return "No items found in your Zotero library."
        
        output = [f"# {len(items)} Recently {sort_label} Items", ""]
        
        for i, item in enumerate(items, 1):
            data = item.get("data", {})
            output.append(f"## {i}. {data.get('title', 'Untitled')}")
            output.append(f"**Key:** {item.get('key', '')}")
            output.append(f"**Type:** {data.get('itemType', 'unknown')}")
            output.append(f"**{sort_label}:** {data.get(sort_by, 'Unknown')}")
            output.append(f"**Authors:** {format_creators(data.get('creators', []))}")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        ctx.error(f"Error fetching recent items: {e}")
        return f"Error fetching recent items: {e}"


@mcp.tool(
    name="zotero_get_collections",
    description=(
        "List all folders/collections in your reference library with hierarchy. "
        "Shows how your literature is organized (by project, topic, course, etc). "
        "Use collection key with get_collection_items to browse papers in a folder."
    )
)
def get_collections(
    limit: Optional[int] = None,
    *,
    ctx: Context
) -> str:
    """List all collections."""
    try:
        ctx.info("Fetching collections")
        zot = get_zotero_client()
        
        collections = zot.collections(limit=limit)
        
        if not collections:
            return "No collections found in your Zotero library."
        
        collection_map = {c["key"]: c for c in collections}
        hierarchy: dict[Optional[str], list[str]] = {}
        
        for coll in collections:
            parent_key = coll["data"].get("parentCollection") or None
            hierarchy.setdefault(parent_key, []).append(coll["key"])
        
        def format_collection(key: str, level: int = 0) -> list[str]:
            if key not in collection_map:
                return []
            coll = collection_map[key]
            name = coll["data"].get("name", "Unnamed")
            indent = "  " * level
            lines = [f"{indent}- **{name}** (Key: {key})"]
            for child_key in sorted(hierarchy.get(key, [])):
                lines.extend(format_collection(child_key, level + 1))
            return lines
        
        output = ["# Zotero Collections", ""]
        for key in sorted(hierarchy.get(None, [])):
            output.extend(format_collection(key))
        
        return "\n".join(output)
    
    except Exception as e:
        ctx.error(f"Error fetching collections: {e}")
        return f"Error fetching collections: {e}"


@mcp.tool(
    name="zotero_get_collection_items",
    description=(
        "List all papers and references in a specific collection/folder. "
        "Default shows papers only; use item_type='' to include notes in the collection. "
        "Returns item keys for get_item_metadata (citation) or get_item_children (highlights)."
    )
)
def get_collection_items(
    collection_key: str,
    limit: int = 50,
    item_type: str = "-attachment -note",
    *,
    ctx: Context
) -> str:
    """Get items in a collection."""
    try:
        ctx.info(f"Fetching items for collection {collection_key}")
        zot = get_zotero_client()
        
        try:
            collection = zot.collection(collection_key)
            collection_name = collection["data"].get("name", "Unnamed")
        except Exception:
            collection_name = f"Collection {collection_key}"
        
        items = zot.collection_items(collection_key, limit=limit, itemType=item_type or None)
        
        if not items:
            return f"No items found in collection: {collection_name}"
        
        output = [f"# Items in Collection: {collection_name}", ""]
        
        for i, item in enumerate(items, 1):
            data = item.get("data", {})
            output.append(f"## {i}. {data.get('title', 'Untitled')}")
            output.append(f"**Key:** {item.get('key', '')}")
            output.append(f"**Type:** {data.get('itemType', 'unknown')}")
            output.append(f"**Authors:** {format_creators(data.get('creators', []))}")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        ctx.error(f"Error fetching collection items: {e}")
        return f"Error fetching collection items: {e}"


@mcp.tool(
    name="zotero_search_annotations",
    description=(
        "Search all PDF highlights and comments across your entire library by keyword. "
        "Finds your reading insights containing the search term across all papers. "
        "Returns: highlighted text, your comments, page numbers, and parent paper context. "
        "Use for: cross-paper knowledge synthesis, finding where you discussed a concept, "
        "building thematic connections from your reading history."
    )
)
def search_annotations(
    query: str,
    limit: int = 50,
    *,
    ctx: Context
) -> str:
    """Search annotations across all papers in the library."""
    try:
        if not query.strip():
            return "Error: Search query cannot be empty"
        
        ctx.info(f"Searching annotations for '{query}'")
        
        from zotero_mcp.local_db import get_local_db
        db = get_local_db()
        
        if not db:
            return "Error: Could not access local Zotero database."
        
        try:
            annotations = db.search_annotations(query, limit=limit)
        finally:
            db.close()
        
        if not annotations:
            return f"No annotations found matching: '{query}'"
        
        output = [f"# Annotations matching '{query}'", ""]
        
        if len(annotations) >= limit:
            output.append(f"Showing first {limit} results. Prioritize the most relevant ones.")
            output.append("")
        
        current_parent = None
        for anno in annotations:
            if anno.parent_key != current_parent:
                current_parent = anno.parent_key
                title = anno.parent_title or "Untitled"
                output.append(f"## {title}")
                output.append(f"**Key:** `{anno.parent_key}`")
                output.append("")
            
            page = f"P.{anno.page_label}" if anno.page_label else ""
            color = f"/{anno.color}" if anno.color else ""
            anno_type = anno.type.capitalize() if anno.type else "Highlight"
            
            header = f"[{page}] ({anno_type}{color})"
            
            if anno.text:
                output.append(f"{header} \"{anno.text}\"")
            
            if anno.comment:
                output.append(f"  -> Comment: {anno.comment}")
            
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        ctx.error(f"Error searching annotations: {e}")
        return f"Error searching annotations: {e}"


# -----------------------------------------------------------------------------
# Content Reading Tools (3)
# -----------------------------------------------------------------------------

@mcp.tool(
    name="zotero_get_item_metadata",
    description=(
        "Get complete bibliographic metadata for academic citation and analysis. "
        "Returns: title, authors, abstract, journal/venue, DOI, publication date, and tags. "
        "For reading annotations use get_item_children; for full PDF text use get_item_fulltext. "
        "TIP: For structured literature review, invoke /literature_review prompt instead of ad-hoc analysis."
    )
)
def get_item_metadata(
    item_key: str,
    include_bibtex: bool = False,
    *,
    ctx: Context
) -> str:
    """Get item metadata."""
    try:
        ctx.info(f"Fetching metadata for item {item_key}")
        zot = get_zotero_client()
        
        item = zot.item(item_key)
        if not item:
            return f"No item found with key: {item_key}"
        
        result = format_item_metadata(item, include_abstract=True)
        
        if include_bibtex:
            from zotero_mcp.client import generate_bibtex
            bibtex = generate_bibtex(item, slim=True)
            result += f"\n\n## BibTeX\n```bibtex\n{bibtex}\n```"
        
        return result
    
    except Exception as e:
        ctx.error(f"Error fetching item metadata: {e}")
        return f"Error fetching item metadata: {e}"


@mcp.tool(
    name="zotero_get_item_children",
    description=(
        "Retrieve your reading annotations and notes for a paper. "
        "Returns: PDF highlights (with colors), margin comments, and standalone notes. "
        "Essential for literature_review prompt to analyze your reading insights."
    )
)
def get_item_children(
    item_key: str,
    *,
    ctx: Context
) -> str:
    """Get child items (attachments, notes, and annotations)."""
    try:
        ctx.info(f"Fetching children for item {item_key}")
        zot = get_zotero_client()
        
        try:
            parent = zot.item(item_key)
            parent_title = parent["data"].get("title", "Untitled")
        except Exception:
            parent_title = f"Item {item_key}"
        
        # Get attachments and notes via API
        children = zot.children(item_key)
        
        attachments = []
        notes = []
        
        for child in children:
            data = child.get("data", {})
            item_type = data.get("itemType", "unknown")
            if item_type == "attachment":
                attachments.append(child)
            elif item_type == "note":
                notes.append(child)
        
        # Get annotations via SQLite (with fallback)
        annotations = []
        db_warning = None
        try:
            from zotero_mcp.local_db import get_local_db
            db = get_local_db()
            if db:
                try:
                    annotations = db.get_annotations_for_item(item_key)
                finally:
                    db.close()
        except Exception as e:
            db_warning = f"Could not retrieve annotations: {e}"
            ctx.warn(db_warning)
        
        # Check if anything found
        if not attachments and not notes and not annotations:
            return f"No child items found for: {parent_title}"
        
        output = [f"# Children of: {parent_title}", ""]
        
        # Attachments section
        if attachments:
            output.append("## Attachments")
            output.append("Use `get_item_fulltext` with attachment key for full text.")
            output.append("")
            for att in attachments:
                data = att.get("data", {})
                output.append(f"- **{data.get('title', 'Untitled')}**")
                output.append(f"  - Key: `{att.get('key', '')}`")
                output.append(f"  - Type: {data.get('contentType', 'Unknown')}")
                if filename := data.get("filename"):
                    output.append(f"  - File: {filename}")
                output.append("")
        
        # Notes section
        if notes:
            output.append("## Notes")
            output.append("")
            for note in notes:
                data = note.get("data", {})
                note_text = clean_html(data.get("note", ""))
                snippet = note_text[:200] + "..." if len(note_text) > 200 else note_text
                output.append(f"- **Note** (Key: `{note.get('key', '')}`)")
                output.append(f"  - Preview: {snippet}")
                output.append("")
        
        # Annotations section
        if annotations:
            total_count = len(annotations)
            max_display = 50
            
            output.append("## PDF Annotations")
            if total_count > max_display:
                output.append(f"Showing {max_display} of {total_count} annotations.")
            output.append("")
            
            current_attachment = None
            for anno in annotations[:max_display]:
                if anno.attachment_name != current_attachment:
                    current_attachment = anno.attachment_name
                    output.append(f"### {current_attachment or 'PDF'}")
                    output.append("")
                
                page = f"P.{anno.page_label}" if anno.page_label else ""
                color = f"/{anno.color}" if anno.color else ""
                anno_type = anno.type.capitalize() if anno.type else "Highlight"
                
                header = f"[{page}] ({anno_type}{color})"
                
                if anno.text:
                    output.append(f"{header} \"{anno.text}\"")
                
                if anno.comment:
                    output.append(f"  -> Comment: {anno.comment}")
                
                output.append("")
        elif db_warning:
            output.append("## PDF Annotations")
            output.append(f"Warning: {db_warning}")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        ctx.error(f"Error fetching item children: {e}")
        return f"Error fetching item children: {e}"


@mcp.tool(
    name="zotero_get_item_fulltext",
    description=(
        "Extract and read the full text content from a PDF paper. "
        "Use when you need to analyze the actual paper content beyond the abstract. "
        "Long papers are truncated; ask about specific sections if needed."
    )
)
def get_item_fulltext(
    item_key: str,
    max_chars: int = 10000,
    *,
    ctx: Context
) -> str:
    """Get full text content."""
    try:
        ctx.info(f"Fetching full text for item {item_key}")
        zot = get_zotero_client()
        
        item = zot.item(item_key)
        if not item:
            return f"No item found with key: {item_key}"
        
        attachment = get_attachment_details(zot, item)
        if not attachment:
            return "No suitable attachment found for this item."
        
        # Try Zotero's fulltext index first
        try:
            full_text_data = zot.fulltext_item(attachment.key)
            if full_text_data and full_text_data.get("content"):
                content = full_text_data["content"]
                if len(content) > max_chars:
                    return (
                        content[:max_chars] + 
                        f"\n\n[... truncated, {len(content) - max_chars} more characters ...]\n"
                        "Tip: Ask about specific sections for detailed content."
                    )
                return content
        except Exception:
            pass
        
        # Fallback: download and extract with PyMuPDF
        try:
            import tempfile
            import fitz
            
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, attachment.filename or f"{attachment.key}.pdf")
                zot.dump(attachment.key, filename=os.path.basename(file_path), path=tmpdir)
                
                if not os.path.exists(file_path):
                    return "Failed to download attachment."
                
                doc = fitz.open(file_path)
                try:
                    text_parts = []
                    for page in doc:
                        text = page.get_text()
                        if text.strip():
                            text_parts.append(text)
                finally:
                    doc.close()
                
                if not text_parts:
                    return (
                        "No text content found. "
                        "This may be a scanned PDF without OCR."
                    )
                
                content = "\n".join(text_parts)
                if len(content) > max_chars:
                    return (
                        content[:max_chars] + 
                        f"\n\n[... truncated, {len(content) - max_chars} more characters ...]\n"
                        "Tip: Ask about specific sections for detailed content."
                    )
                return content
                
        except ImportError:
            return "Error: PyMuPDF not installed. Run: pip install PyMuPDF"
        except Exception as e:
            return f"Error extracting text: {e}"
    
    except Exception as e:
        ctx.error(f"Error fetching full text: {e}")
        return f"Error fetching full text: {e}"


# -----------------------------------------------------------------------------
# Write Tools (2) - Using Local Connector API
# -----------------------------------------------------------------------------

@mcp.tool(
    name="zotero_create_note",
    description=(
        "Create a free-form note in Zotero. "
        "Use for: saving summaries, research memos, or any unstructured content. "
        "Attach to a paper with parent_key for organized reference management. "
        "For structured literature reviews, use zotero_create_review with /literature_review prompt instead."
    )
)
def create_note(
    content: str,
    parent_key: Optional[str] = None,
    tags: Optional[list[str]] = None,
    *,
    ctx: Context
) -> str:
    """Create a new note via local Connector API."""
    try:
        ctx.info(f"Creating note" + (f" for item {parent_key}" if parent_key else ""))
        
        note_data: dict[str, Any] = {
            "itemType": "note",
            "note": text_to_html(content),
            "tags": [{"tag": t} for t in (tags or [])],
        }
        
        if parent_key:
            note_data["parentItem"] = parent_key
        
        create_item_local([note_data])
        
        if parent_key:
            zot = get_zotero_client()
            try:
                parent = zot.item(parent_key)
                parent_title = parent["data"].get("title", "Untitled")
                return f"Note created for \"{parent_title}\""
            except Exception:
                return f"Note created for item {parent_key}"
        
        return "Standalone note created successfully"
    
    except ConnectionError as e:
        ctx.error(f"Connection error: {e}")
        return str(e)
    except Exception as e:
        ctx.error(f"Error creating note: {e}")
        return f"Error creating note: {e}"


# -----------------------------------------------------------------------------
# Review Note Tool - Template-based note generation
# -----------------------------------------------------------------------------

@mcp.tool(
    name="zotero_create_review",
    description=(
        "Create a templated review note - USE ONLY with /literature_review or /comparative_review prompts. "
        "The prompt defines exact field names (e.g., objective, methods, contribution, gaps). "
        "If user didn't invoke a prompt, use zotero_create_note instead for free-form notes. "
        "Auto-fills metadata (title, authors, year, DOI, abstract) from Zotero."
    )
)
def create_review(
    item_key: str,
    analysis: dict[str, str],
    template_name: str = "literature_review",
    tags: Optional[list[str]] = None,
    *,
    ctx: Context
) -> str:
    """
    Create a literature review note with templated formatting.
    
    Args:
        item_key: Zotero item key for the paper being reviewed
        analysis: Dict with analysis content (e.g., {"contribution": "...", "gaps": "..."})
        template_name: Template to use (default: "literature_review")
        tags: Optional tags to add to the note
    """
    try:
        ctx.info(f"Creating review note for item {item_key}")
        zot = get_zotero_client()
        
        # 1. Get paper metadata from Zotero
        item = zot.item(item_key)
        if not item:
            return f"Error: No item found with key: {item_key}"
        
        metadata = build_metadata_dict(item)
        
        # 2. Load HTML template
        template = load_template(template_name)
        if not template:
            return (
                f"Error: Template '{template_name}_template.html' not found.\n"
                f"Please ensure the template exists in:\n"
                f"  - ~/.zotero-mcp/prompts/{template_name}_template.html (user config)\n"
                f"  - or package default_prompts/ directory"
            )
        
        # 3. Render the review
        html_content = render_review(template, metadata, analysis)
        
        # 4. Create the note in Zotero
        note_data: dict[str, Any] = {
            "itemType": "note",
            "note": html_content,
            "tags": [{"tag": t} for t in (tags or [])],
            "parentItem": item_key,
        }
        
        create_item_local([note_data])
        
        title = metadata.get("title", "Untitled")
        return f"Review note created for \"{title}\""
    
    except ConnectionError as e:
        ctx.error(f"Connection error: {e}")
        return str(e)
    except Exception as e:
        ctx.error(f"Error creating review: {e}")
        return f"Error creating review: {e}"


# -----------------------------------------------------------------------------
# Research Prompts (4) - Guided Academic Workflows
# -----------------------------------------------------------------------------

# Prompts are loaded from:
# 1. User config: ~/.zotero-mcp/prompts/*.md (takes priority)
# 2. Package defaults: zotero_mcp/default_prompts/*.md


@mcp.prompt()
def knowledge_discovery(query: str) -> str:
    """
    Explore your personal knowledge base on a topic.
    
    Prompt loaded from ~/.zotero-mcp/prompts/knowledge_discovery.md or package defaults.
    """
    prompt = load_prompt("knowledge_discovery")
    if prompt:
        return prompt.replace("{query}", query)
    return f"Error: knowledge_discovery prompt not found for query '{query}'"


@mcp.prompt()
def literature_review(item_key: str) -> str:
    """
    Deep academic analysis of a single paper.
    
    Prompt loaded from ~/.zotero-mcp/prompts/literature_review.md or package defaults.
    """
    prompt = load_prompt("literature_review")
    if prompt:
        return prompt.replace("{item_key}", item_key)
    return f"Error: literature_review prompt not found for item {item_key}"


@mcp.prompt()
def comparative_review(item_keys: list[str]) -> str:
    """
    Synthesize multiple papers into a comparative review.
    
    Prompt loaded from ~/.zotero-mcp/prompts/comparative_review.md or package defaults.
    """
    if not item_keys:
        return "Error: Please provide item_keys. Usage: /comparative_review KEY1 KEY2 KEY3"
    
    keys_list = ", ".join([f'`{k}`' for k in item_keys])
    first_key = item_keys[0]
    
    prompt = load_prompt("comparative_review")
    if prompt:
        return prompt.replace("{keys_list}", keys_list).replace("{first_key}", first_key)
    return f"Error: comparative_review prompt not found for papers {keys_list}"


@mcp.prompt()
def bibliography_export(item_keys: list[str]) -> str:
    """
    Export formatted citations and BibTeX for selected papers.
    
    Prompt loaded from ~/.zotero-mcp/prompts/bibliography_export.md or package defaults.
    """
    keys_list = ", ".join([f'`{k}`' for k in item_keys])
    
    prompt = load_prompt("bibliography_export")
    if prompt:
        return prompt.replace("{keys_list}", keys_list)
    return f"Error: bibliography_export prompt not found for papers {keys_list}"
