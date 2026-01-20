# Literature Review Prompt

Perform comprehensive academic analysis of paper {item_key}.

## Phase 1: Information Gathering

1. Call `zotero_get_item_metadata("{item_key}")` for bibliographic details and abstract.
2. Call `zotero_get_item_children("{item_key}")` to retrieve annotations and notes.
3. If no annotations found, call `zotero_get_item_fulltext("{item_key}")` to get the full paper text.

## Phase 2: Analysis

Based on the available content, analyze:

1. **Research Objective** - What is the main research question?
2. **Research Background** - What context/prior work is mentioned?
3. **Research Methods** - What methodology is used?
4. **Contribution** - What are the novel contributions?
5. **Gaps** - What limitations are identified?
6. **Discussion** - What are the implications?
7. **Quotes** - Key findings worth citing
8. **To-Read** - Related papers mentioned

**Analysis Mode:**
- If annotations exist: Prioritize the user's highlights and comments
- If no annotations: Analyze from full text (or abstract if full text unavailable)

## Phase 3: Note Creation

After presenting the analysis, ask:
"Would you like me to save this review as a note in Zotero?"

If user agrees, call `zotero_create_review` with the analysis:

```
zotero_create_review(
    item_key="{item_key}",
    analysis={
        "objective": "The main research question is...",
        "background": "This paper builds on...",
        "methods": "The methodology involves...",
        "contribution": "The key contributions are...",
        "gaps": "Limitations include...",
        "discussion": "The implications are...",
        "quotes": "Key findings: ...",
        "to_read": "Related papers: ..."
    }
)
```

The system will automatically fill in metadata (title, authors, year, DOI, abstract) from Zotero.
