# Comparative Review Prompt

User request: {papers}

## Step 1: Identify Papers

- Titles/topics → `zotero_search_items(query)`
- "Recent papers" → `zotero_get_recent()`
- Item keys → Use directly
- Unclear → Ask user

## Step 2: Gather Information

For each paper:
1. `zotero_get_item_children(key)` for existing reviews/annotations
2. If needed, `zotero_get_item_fulltext(key)`

## Step 3: Comparative Analysis

Create a synthesis covering:

- **Executive Summary**
- **Papers Overview**
- **Categorization**
- **Methods Comparison**
- **Key Findings**
- **Consensus**
- **Conflicts** (explain why authors disagree)
- **Research Evolution**
- **Challenges & Solutions**
- **Insights**
- **Synthesis**

Go deep - surface-level comparisons are not useful. Use tables where helpful. Cite papers for claims. Include specific metrics.

Don't fabricate data or citations.

## Step 4: Save

Ask: "Save to Zotero?" → Use `zotero_create_review` with `template_name="comparative_review"`
