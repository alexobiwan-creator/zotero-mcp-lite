# Literature Review Prompt

User request: {paper}

## Step 1: Find the Paper

- If user mentions a title/topic → Use `zotero_search_items(query)`
- If user says "recent paper" → Use `zotero_get_recent(limit=1)`
- If user provides an item key → Use that key
- If unclear → Ask which paper to review

## Step 2: Gather Information

1. Call `zotero_get_item_metadata(item_key)`
2. Call `zotero_get_item_children(item_key)` for annotations
3. If annotations are sparse, call `zotero_get_item_fulltext(item_key)`

## Step 3: In-Depth Analysis

Analyze the paper thoroughly under these sections. **Be comprehensive** - include specific details, examples, and evidence from the paper.

**Format guidelines:**
- Use **tables** for comparisons (methods, results, datasets)
- Use **bullet points** for lists of findings, contributions, or limitations
- Use **sub-sections** to organize complex topics
- Include **specific numbers and metrics** when available
- Quote **key definitions and formulas** directly

### Required Sections:

**Research Objective** - What problem? Why important? What gap does it fill?

**Research Background** - Prior work with specific contributions. Show the research timeline/evolution if relevant.

**Research Methods** - Detailed methodology. Consider using a table for:
| Aspect | Details |
|--------|---------|
| Dataset | Name, size, characteristics |
| Model/Approach | Architecture, key components |
| Evaluation | Metrics, baselines, protocols |

**Contribution** - Key findings with specific metrics. Use comparisons where applicable.

**Research Gaps** - What limitations do authors acknowledge? What's missing?

**Discussion** - Future directions, implications for the field.

**Key Quotes** - Important statements that define the work.

**To-Read** - Related papers and why they're relevant.

### Quality Rules

- Go deep, not shallow - explain the "why" and "how", not just "what"
- Never fabricate data or citations
- If information not found, write "Not discussed in paper"

## Step 4: Save to Zotero

Ask: "Save this review to Zotero?"

If yes, call `zotero_create_review` with the analysis content.
