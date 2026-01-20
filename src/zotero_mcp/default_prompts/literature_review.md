# Literature Review Prompt

Perform comprehensive academic analysis of paper {item_key}.

## Phase 1: Information Gathering (MANDATORY)

Execute these steps **in order**:

1. Call `zotero_get_item_metadata("{item_key}")` for bibliographic details.
2. Call `zotero_get_item_children("{item_key}")` to check for annotations.
3. **ALWAYS** call `zotero_get_item_fulltext("{item_key}")` to get the full paper text.

**You MUST read the full text before analysis.** Do not rely solely on the abstract.

## Phase 2: Deep Analysis

After reading the full text, extract information for each field below.

### Anti-Hallucination Rules (CRITICAL)

1. **ONLY extract what is explicitly stated** in the paper
2. **Quote directly** when possible - use "..." for exact text
3. **Cite location** - indicate section name (e.g., "from Introduction", "from Section 3.2")
4. **Never invent** numbers, metrics, author names, or paper titles
5. **If not found**, write: "Not explicitly discussed in this paper"
6. **Distinguish facts from inference** - mark any inference with "[Inference]"

### Required Analysis Fields

| Field | What to Extract | Source Section |
|-------|-----------------|----------------|
| **objective** | Research question or goal stated by authors | Introduction |
| **background** | Prior work explicitly cited and discussed | Introduction / Related Work |
| **methods** | Data, methodology, experimental setup described | Methods / Methodology |
| **contribution** | Results and findings with exact numbers | Results / Findings |
| **gaps** | Limitations explicitly acknowledged by authors | Discussion / Limitations |
| **discussion** | Future work mentioned by authors | Conclusion / Future Work |
| **quotes** | Direct quotes with section reference | Any section |
| **to_read** | Papers explicitly cited as important | References mentioned in text |

### Output Format

For each field, use this structure:
```
[Section: X] "Direct quote or paraphrase" - Your brief explanation
```

Example:
```
objective: [Section: Introduction] "This study aims to develop a framework for..." - The authors seek to create an automated compliance checking system.
```

### Handling Missing Information

- If a field cannot be filled from the paper: `"Not explicitly discussed in this paper"`
- If information is implied but not stated: `"[Inference] Based on... it appears that..."`
- **NEVER fabricate** content to fill empty fields

## Phase 3: Note Creation

After presenting the analysis, ask:
"Would you like me to save this review as a note in Zotero?"

If user agrees, call `zotero_create_review`:

```
zotero_create_review(
    item_key="{item_key}",
    analysis={
        "objective": "[Introduction] 'exact quote' - explanation",
        "background": "[Related Work] Authors cite X, Y, Z as foundational...",
        "methods": "[Methods] The study uses... with N=X samples...",
        "contribution": "[Results] Achieved X% accuracy, Y% precision...",
        "gaps": "[Limitations] Authors acknowledge...",
        "discussion": "[Conclusion] Future work includes...",
        "quotes": "'Quote 1' (Section X); 'Quote 2' (Section Y)",
        "to_read": "Author1 (Year) cited for X; Author2 (Year) cited for Y"
    }
)
```

**Reminder:** Metadata is auto-filled from Zotero. Focus on extracting verifiable content from the FULL TEXT with proper citations.
