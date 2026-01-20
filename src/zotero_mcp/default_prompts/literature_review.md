# Literature Review Prompt

User request: {paper}

## Step 1: Find the Paper

- Title/topic mentioned → `zotero_search_items(query)`
- "Recent paper" → `zotero_get_recent(limit=1)`
- Item key provided → Use directly
- Unclear → Ask user

## Step 2: Gather Information

1. `zotero_get_item_metadata(item_key)`
2. `zotero_get_item_children(item_key)` for annotations
3. If sparse, `zotero_get_item_fulltext(item_key)`

## Step 3: Analyze

Write a comprehensive review covering these sections:

- **Research Objective**
- **Research Background**
- **Research Methods**
- **Contribution**
- **Research Gaps**
- **Discussion**
- **Key Quotes**
- **To-Read**

Go deep - explain the "why" and "how", not just "what". Use tables, bullet points, or prose as you see fit. Include specific metrics and evidence.

Don't fabricate data or citations.

## Step 4: Save

Ask: "Save to Zotero?" → Use `zotero_create_review`
