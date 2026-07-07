# Final Report — The Glass Self

## Production Summary

**Title:** The Glass Self
**Author:** Barış Kısır
**Model:** claude-sonnet-4-6
**Genre:** Psychological Horror / Existential Fiction
**Subgenre:** Cotard Delusion / Existential Fiction
**Status:** Complete

## Deliverables

| File | Path | Status |
|------|------|--------|
| Outline | books/The_Glass_Self/planning/The_Glass_Self_outline.md | Complete |
| Manuscript | books/The_Glass_Self/txt/The_Glass_Self.txt | Complete |
| Metadata | books/The_Glass_Self/metadata/The_Glass_Self_metadata.json | Complete |
| Cover PNG | books/The_Glass_Self/covers/The_Glass_Self.png | Complete |
| EPUB | books/The_Glass_Self/epub/The_Glass_Self.epub | Complete |
| Build Script | books/The_Glass_Self/tools/build_epub.py | Complete |
| Cover Script | books/The_Glass_Self/tools/create_cover.py | Complete |
| Final Report | books/The_Glass_Self/reports/final_report.md | Complete |
| Manifest | books/The_Glass_Self/reports/manifest.csv | Complete |
| Progress | books/The_Glass_Self/reports/progress.md | Complete |
| README | books/The_Glass_Self/README.md | Complete |

## Validation Results

- Chapter count: 50 (confirmed via regex ^Chapter\s+(\d+):\s+(.+)$)
- EPUB mimetype: application/epub+zip (correct)
- EPUB chapter XHTML files: 50
- Model on title page: claude-sonnet-4-6 (confirmed)
- Author in metadata: Barış Kısır (confirmed, Turkish characters correct)
- Cover PNG: Non-empty, unique corridor-with-absent-reflection scene
- Cover includes all 8 standard helpers (confirmed)
- Metadata author read at runtime via metadata.get()

## Book Description

The Glass Self is a psychological horror novel in the Cotard Delusion / Existential Fiction subgenre. The premise centers on Dr. Vincent Crane, a psychiatrist who has spent twenty years treating Cotard's syndrome — the rare condition in which patients believe they are dead — and now develops the condition himself after surviving a cardiac arrest in a car accident.

The novel is structured in five parts of ten chapters each:

- **Part One (Chapters 1–10): The Accident and Its Aftermath** — The crash, hospitalization, discharge, and the first signs of the delusion.
- **Part Two (Chapters 11–20): The Diagnosis Diagnosed** — Vincent's colleague Sarah Ng begins informal assessment; the clinical and personal stakes are established.
- **Part Three (Chapters 21–30): The Interior Country** — The phenomenology of the delusion from inside, family dynamics, and the medication trial.
- **Part Four (Chapters 31–40): The Treatment and the Test** — Supervised return to clinical practice, a pivotal dream, and a crisis call that marks a turning point.
- **Part Five (Chapters 41–50): The Return and the Remainder** — Gradual, incomplete recovery; the scar rather than the absence.

## Cover Design

The cover depicts a hospital corridor at night with a standing figure at the near end. The figure is fully solid and present. His reflection in the polished floor is completely absent — a perfect black void. A single warm yellow light burns at the vanishing point at the far end. The palette is cold institutional blue-white. The absent reflection is the central visual conceit: present person, absent reflection, inverting the expected relationship between living being and mirror image.

## Word Count Estimate

50 chapters × average ~950 words = approximately 47,500 words.
