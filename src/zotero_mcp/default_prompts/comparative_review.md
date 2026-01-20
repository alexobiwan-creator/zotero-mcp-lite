# Comparative Review Prompt

Synthesize a comparative review for papers: {keys_list}

## Recommended Workflow

For best results:
1. Run `/literature_review` on each paper first
2. Then run this comparative review - it will read your saved reviews

## Phase 1: Information Gathering

For each paper:
1. Call `zotero_get_item_children(key)` - check for existing review notes
2. If no reviews, use annotations or call `zotero_get_item_fulltext(key)`

## Phase 2: Comparative Analysis

Create a synthesis covering these sections. Use tables, bullet points, or prose as appropriate:

- **Executive Summary** - What do these papers collectively reveal?
- **Papers Overview** - Table with authors, year, focus, key innovation
- **Categorization** - Group papers by theme/domain
- **Methods Comparison** - Compare approaches, strengths, limitations
- **Key Findings** - Main results from each paper
- **Consensus** - Where authors agree
- **Conflicts** - Where authors disagree and why
- **Research Evolution** - How the field developed across these papers
- **Challenges & Solutions** - Common problems and proposed solutions
- **Insights** - Recommendations for researchers and practitioners
- **Synthesis** - Overall narrative connecting all papers

### Rules

- Cite specific papers when making claims
- For conflicts, explain WHY authors disagree (methodology, sample, assumptions)
- Never fabricate data or citations

## Phase 3: Save to Zotero

Ask: "Save this comparative review to Zotero?"

If yes, call `zotero_create_review` with the analysis:

```
zotero_create_review(
    item_key="{first_key}",
    analysis={
        "summary": "Your Executive Summary",
        "papers": "Your Papers Overview table",
        "categorization": "Your Categorization content",
        "methods": "Your Methods Comparison",
        "findings": "Your Key Findings",
        "consensus": "Your Consensus content",
        "conflicts": "Your Conflicts content",
        "evolution": "Your Research Evolution",
        "challenges": "Your Challenges & Solutions",
        "insights": "Your Insights content",
        "synthesis": "Your Synthesis content"
    },
    template_name="comparative_review"
)
```
