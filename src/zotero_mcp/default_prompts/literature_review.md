# Literature Review Prompt

Perform comprehensive academic analysis of paper {item_key}.

## Phase 1: Smart Information Gathering

Execute these steps **in order**:

1. Call `zotero_get_item_metadata("{item_key}")` for bibliographic details.
2. Call `zotero_get_item_children("{item_key}")` to retrieve annotations and notes.
3. **Conditional fulltext retrieval:**
   - If annotations are **rich and cover most analysis fields** → Use annotations as primary source
   - If annotations are **sparse or missing key fields** → Call `zotero_get_item_fulltext("{item_key}")` to supplement

**Prioritize user annotations** - they represent what the user found important. Only fetch fulltext when annotations are insufficient.

## Phase 2: Concise Analysis

Extract information for each field below. **Be concise and direct.**

### Anti-Hallucination Rules

1. **ONLY extract what is explicitly stated** - no fabrication
2. **Quote directly** when possible using "..."
3. **Cite section** - e.g., "[Intro]", "[Methods]", "[Results]"
4. **If not found**: "Not discussed"
5. **If inferred**: Mark with "[Inference]"

### Required Fields

| Field | Extract | Source | Format |
|-------|---------|--------|--------|
| **objective** | Research question/goal | Introduction | Max 50 words |
| **background** | Key prior work cited | Intro/Related Work | Max 50 words |
| **methods** | Methodology + **sample size** + **data source** | Methods | Max 60 words |
| **contribution** | Key findings with **exact metrics** | Results | Max 60 words |
| **gaps** | Limitations stated by authors | Discussion | Max 50 words |
| **discussion** | Future work directions | Conclusion | Max 50 words |
| **quotes** | 2-3 key sentences worth citing | Any | Direct quotes only |
| **to_read** | Gap-filling references | Text | Why worth reading |

### Output Rules

1. **Max 50-60 words per field** (except quotes)
2. **No filler phrases** - avoid "The authors mention...", "This paper discusses..."
3. **Lead with the insight**, not the source
4. **Include numbers** when available (N=, %, accuracy, etc.)

### Format Examples

**Good:**
```
methods: [Methods] Survey of N=500 construction workers; image dataset of 2,847 site photos; YOLOv5 for detection.
```

**Bad (too verbose):**
```
methods: [Methods] The authors describe their methodology in detail. They conducted a survey... (continues for 150 words)
```

### to_read Field: Gap-Filling References

Don't just list papers. Explain **why** each is worth reading:

```
to_read: 
- Wang (2023): Provides safety inspection dataset this paper lacks
- Chen (2022): Alternative approach using transformers, compare accuracy
```

### Handling Missing Information

- Not found: `"Not discussed"`
- Implied only: `"[Inference] ..."`
- **Never fabricate** to fill gaps

## Phase 3: Note Creation

After presenting analysis, ask:
"Would you like me to save this review as a note in Zotero?"

If yes, call `zotero_create_review`:

```
zotero_create_review(
    item_key="{item_key}",
    analysis={
        "objective": "[Intro] Develop automated compliance checking for construction sites.",
        "background": "[Related Work] Builds on YOLO-based detection (Redmon 2016) and safety ontologies (Zhang 2021).",
        "methods": "[Methods] N=500 site images; few-shot learning with 5-shot setup; YOLOv5 backbone.",
        "contribution": "[Results] 88.2% precision, 79.5% recall for object detection; 94.8% for attributes.",
        "gaps": "[Limitations] Limited to fall hazards; no real-time deployment tested.",
        "discussion": "[Conclusion] Extend to other hazard types; integrate with BIM systems.",
        "quotes": "'Few-shot learning reduces annotation burden by 80%' [Results]",
        "to_read": "Li (2024): Multi-agent approach for comparison; OSHA dataset for validation"
    }
)
```

**Reminder:** Metadata (title, authors, DOI, abstract) auto-filled from Zotero. Focus on concise, verifiable insights.
