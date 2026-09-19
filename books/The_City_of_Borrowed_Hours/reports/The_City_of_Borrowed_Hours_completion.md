# Manuscript completion report

- Date: 2026-09-19
- Title: The City of Borrowed Hours
- Language: English
- Genre: Science Fiction / Speculative Thriller
- Model metadata: gpt-6-astra, as requested
- Manuscript status: Complete, including the resolution and aftermath
- Requested word target: 50,000
- Permitted variation: ±50%
- Accepted range: 25,000–75,000
- Verified word count: 26,461
- Count convention: Nonempty whitespace-delimited tokens in the complete UTF-8 TXT, including title, byline, chapter headings, and end marker
- Verified chapter count: 20
- Chapter numbering: Consecutive, 1–20
- Repeated long paragraphs: None detected by exact comparison of paragraphs longer than 150 characters
- Trailing whitespace: None detected

The prose was composed directly and saved through file patches. No script, template expansion, or programmatic text generator produced the book's content. Read-only PowerShell checks counted words and headings and inspected file integrity.

The final review corrected the remaining time before the storm and clarified the controlled reopening of the spill basin. It also resolved the fate of the original memory deposit. The novel ends with the survivors' recovery, institutional accountability, and the siblings' changed relationship.

The book uses the repository's standalone-book directory layout and relative metadata paths. The manuscript was initially completed without running repository scripts. At the user's subsequent request, a PNG cover was generated with the built-in image generation tool, the EPUB was built using `tools/build_epub.py` in single-book mode, and the root README was regenerated using `tools/build_readme.py`.

The EPUB includes the generated cover, a title page, a linked table of contents, and all 20 chapters. A broken stylesheet reference in the builder's navigation document was corrected before the final build. The manuscript and its model metadata remain unchanged. No commit was created.

Artifact verification passed: PNG signature and 1024 × 1536 dimensions; EPUB ZIP integrity and uncompressed first `mimetype` entry; XML parsing; embedded cover byte equality; title, author, and language metadata; 20 table-of-contents links; internal resource references; and paragraph-by-paragraph comparison of all 20 EPUB chapters with the original TXT. The rebuilt root README includes the book's cover and EPUB links. Its existing CRLF line-ending convention was retained; the Git whitespace check passed with `core.whitespace=cr-at-eol`.
