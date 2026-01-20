# Literature Review Prompt

Perform comprehensive academic analysis of paper {item_key}.

## Phase 1: Information Gathering

1. Call `zotero_get_item_metadata("{item_key}")`
2. Call `zotero_get_item_children("{item_key}")` for annotations
3. If annotations are sparse, call `zotero_get_item_fulltext("{item_key}")`

## Phase 2: Analysis

Analyze the paper under these sections. Use tables, bullet points, or prose as appropriate for each section:

- **Research Objective** - What problem does this paper solve?
- **Research Background** - Key prior work and research gap
- **Research Methods** - How did they do it?
- **Contribution** - What did they find/achieve?
- **Research Gaps** - Limitations acknowledged by authors
- **Discussion** - Future directions and implications
- **Key Quotes** - Important statements from the paper
- **To-Read** - Related papers worth reading and why

### Rules

- Extract only explicit content from the paper
- If information not found, write "Not discussed"
- Never fabricate data or citations

## Phase 3: Save to Zotero

Ask: "Save this review to Zotero?"

If yes, call `zotero_create_review` with the analysis content:

```
zotero_create_review(
    item_key="{item_key}",
    analysis={
        "objective": "Your Research Objective content",
        "background": "Your Research Background content",
        "methods": "Your Research Methods content",
        "contribution": "Your Contribution content",
        "gaps": "Your Research Gaps content",
        "discussion": "Your Discussion content",
        "quotes": "Your Key Quotes content",
        "to_read": "Your To-Read content"
    }
)
```
