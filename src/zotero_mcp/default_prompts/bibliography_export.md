# Bibliography Export Prompt

Export citations for papers: {keys_list}

For each paper, call `zotero_get_item_metadata(key, include_bibtex=True)`.

Output for each:
1. **In-text citation**: (Author, Year)
2. **APA-style reference**: Full reference in APA format
3. **IEEE-style reference**: Full reference in IEEE format [1]
4. **BibTeX entry**: For LaTeX

Reminder: Add the "Cited" tag to these items in Zotero Desktop to track citation status.
