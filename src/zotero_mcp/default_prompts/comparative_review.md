# Comparative Review Prompt

Synthesize a comparative review for papers: {keys_list}

## Optimal Workflow (Recommended)

For best results, use this **closed-loop workflow**:

1. **First**: Run `literature_review` on each paper individually
2. **Save**: Let the reviews be stored as Zotero notes
3. **Then**: Run this `comparative_review` - it will read your saved reviews

This approach yields higher quality synthesis because:
- Your structured reviews provide consistent data points
- Token cost is dramatically reduced (reading notes vs. full PDFs)
- Your personal insights are preserved and compared

## Phase 1: Hierarchical Information Gathering

For EACH paper, retrieve information in this **priority order**:

### Step 1: Check for Existing Review Notes
```
Call zotero_get_item_children(key)
```
- Look for notes with titles containing "Review:", "Analysis:", or structured review content
- If found: Use these as the **primary data source** (skip fulltext)

### Step 2: Check for Annotations
- If no review notes exist, use highlights and comments from annotations
- Annotations represent the user's reading insights - prioritize them

### Step 3: Fulltext (Last Resort)
```
Call zotero_get_item_fulltext(key)
```
- Only if Steps 1-2 yield insufficient content
- Extract only: Abstract, Key Findings, Methods summary

**Goal:** Minimize token usage while maximizing insight quality.

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

### 2.6 Consensus & Conflicts (CRITICAL SECTION)

#### Consensus
Where authors agree - cite specific claims with paper references.

#### Conflicts (Use Debate Model)
For each conflict, you MUST specify:

1. **Dimension of Disagreement**: What exactly differs? (methodology, sample, assumptions, metrics, conclusions)
2. **Position A**: "[Author A] claims X, based on evidence Y"
3. **Position B**: "[Author B] claims Z, based on evidence W"
4. **Root Cause**: Why do they differ? (e.g., different sample sizes, time periods, theoretical frameworks)

**Bad example:** "Authors disagree on the effectiveness."
**Good example:** "Smith (2023) reports 85% accuracy using CNN on 10K images, while Chen (2024) finds only 62% accuracy using the same architecture on real-world construction sites (N=500). The gap likely stems from domain shift between lab and field conditions."

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
        "conflicts": "Debate analysis: A claims X because Y, B claims Z because W...",
        "evolution": "Timeline: ...",
        "challenges": "Challenges and solutions table...",
        "insights": "For researchers:... For practitioners:...",
        "synthesis": "Overall, these papers..."
    },
    template_name="comparative_review"
)
```

The system will automatically fill in metadata from Zotero.
