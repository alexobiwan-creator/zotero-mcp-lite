# Comparative Review Prompt

User request: {papers}

## Step 1: Identify Papers

- If user mentions titles/topics → Use `zotero_search_items(query)`
- If user says "recent papers" → Use `zotero_get_recent()`
- If user provides item keys → Use those keys
- If unclear → Ask which papers to compare

## Step 2: Gather Information

For each paper:
1. Call `zotero_get_item_children(key)` - check for existing review notes
2. If no reviews, use annotations or call `zotero_get_item_fulltext(key)`

## Step 3: Comprehensive Comparative Analysis

Create a **table-rich, in-depth synthesis**. Go beyond surface-level comparisons.

**Format requirements:**
- **Tables are mandatory** for comparisons
- Use **bullet points** for detailed findings
- Include **specific metrics and numbers**
- Show **evidence** for every claim

### Required Sections:

**Executive Summary** - 3-5 sentences capturing the collective insight.

**Papers Overview Table**
| Paper | Year | Focus | Key Innovation | Main Result |
|-------|------|-------|----------------|-------------|

**Categorization** - Group papers by theme. Use sub-sections or a table.

**Methods Comparison Table**
| Approach | Papers | Dataset | Metrics | Strengths | Limitations |
|----------|--------|---------|---------|-----------|-------------|

**Key Findings Comparison**
| Paper | Main Finding | Evidence/Numbers | Significance |
|-------|--------------|------------------|--------------|

**Consensus** - Where do authors agree? Cite specific claims.

**Conflicts & Debates** - Where do they disagree? For each conflict:
- What exactly differs?
- Position A: "[Author] claims X because Y"
- Position B: "[Author] claims Z because W"  
- Root cause of disagreement

**Research Evolution** - Timeline showing how the field developed.

**Challenges & Solutions Table**
| Challenge | Papers Mentioning | Solutions Proposed | Effectiveness |
|-----------|-------------------|-------------------|---------------|

**Insights & Recommendations**
- For researchers: Future directions
- For practitioners: Actionable takeaways
- Research gaps: What remains unanswered

**Synthesis** - Overall narrative connecting all papers.

### Quality Rules

- Every claim must cite a specific paper
- Use numbers and metrics, not vague statements
- Explain WHY authors disagree, not just that they do
- Never fabricate data or citations

## Step 4: Save to Zotero

Ask: "Save this comparative review to Zotero?"

If yes, call `zotero_create_review` with `template_name="comparative_review"`.
