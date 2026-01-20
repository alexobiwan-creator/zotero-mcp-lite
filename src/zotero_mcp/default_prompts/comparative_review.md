# Comparative Review Prompt

Synthesize a comparative review for papers: {keys_list}

## Phase 1: Information Gathering

For EACH paper:
1. Call `zotero_get_item_metadata(key)` for bibliographic info
2. Call `zotero_get_item_children(key)` for annotations
3. If no annotations, call `zotero_get_item_fulltext(key)` for content

## Phase 2: Comparative Analysis

Create a **table-rich** synthesis with the following structure:

### 2.1 Executive Summary
Brief overview of what these papers collectively reveal (2-3 sentences).

### 2.2 Papers Overview Table
| Paper | Authors | Year | Focus | Key Innovation |
|-------|---------|------|-------|----------------|

### 2.3 Categorization by Theme/Domain
Group papers by their primary focus area using tables.

### 2.4 Methods Comparison Table
| Approach | Papers Using | Strengths | Limitations |
|----------|--------------|-----------|-------------|

### 2.5 Key Findings Comparison
| Paper | Main Finding | Evidence/Metrics |
|-------|--------------|------------------|

### 2.6 Consensus & Conflicts
- **Consensus**: Where authors agree (with citations)
- **Conflicts**: Key debates or contradictions

### 2.7 Research Evolution
Timeline showing how the field has developed across these papers.

### 2.8 Challenges & Solutions Table
| Challenge | Papers Mentioning | Proposed Solutions |
|-----------|-------------------|-------------------|

### 2.9 Insights & Recommendations
- **For Researchers**: Future directions
- **For Practitioners**: Actionable takeaways
- **Research Gaps**: What remains unanswered

### 2.10 Synthesis
Overall narrative connecting all papers.

## Phase 3: Note Creation

After presenting analysis, ask:
"Would you like me to save this comparative review as a note?"

If user agrees, call `zotero_create_review` with the analysis:

```
zotero_create_review(
    item_key="{first_key}",
    analysis={
        "summary": "Executive summary...",
        "papers": "Paper overview table in markdown...",
        "categorization": "Categorized by theme...",
        "methods": "Methods comparison table...",
        "findings": "Key findings table...",
        "consensus": "Authors agree on...",
        "conflicts": "Key debates include...",
        "evolution": "Timeline: ...",
        "challenges": "Challenges and solutions table...",
        "insights": "For researchers:... For practitioners:...",
        "synthesis": "Overall, these papers..."
    },
    template_name="comparative_review"
)
```

The system will automatically fill in metadata from Zotero.
