# The Meridian Cycle Final Report

Last updated: 2026-05-27

Status: English TXT manuscripts, EPUB files, covers, metadata, manifest, and public README links exist for Books 0-9. Book 8 expansion is complete at 140,000 words after pass 69 and its EPUB has been rebuilt. Book 9 is finalized at the user-approved 110,000-word target and its EPUB has been rebuilt from the final TXT.

Author: Barış Kısır

## Scope

The Meridian Cycle is the first AI Books series in this repository. It is a 10-book English-language science-fiction cycle with shared continuity, standalone book arcs, and EPUB editions generated immediately after each completed book.

No Turkish editions are included in the current production scope.

## Artifact Counts

- Master universe bible: 1
- Book catalog rows: 10
- Book outlines: 10
- TXT manuscripts: 10
- EPUB files: 10
- Cover PNG files: 10
- Metadata JSON files: 10
- Manifest rows: 10

Total validated manuscript word count: 1,406,798

## Book Inventory

| Book | Title | Words | TXT | EPUB | Metadata |
| --- | --- | ---: | --- | --- | --- |
| 0 | The Gate at Kestrel Falling | 141,401 | `The_Meridian_Cycle/txt/Book_0_The_Gate_at_Kestrel_Falling.txt` | `The_Meridian_Cycle/epub/Book_0_The_Gate_at_Kestrel_Falling.epub` | `The_Meridian_Cycle/metadata/Book_0_The_Gate_at_Kestrel_Falling_metadata.json` |
| 1 | Beneath the Reef of Glass | 142,445 | `The_Meridian_Cycle/txt/Book_1_Beneath_the_Reef_of_Glass.txt` | `The_Meridian_Cycle/epub/Book_1_Beneath_the_Reef_of_Glass.epub` | `The_Meridian_Cycle/metadata/Book_1_Beneath_the_Reef_of_Glass_metadata.json` |
| 2 | Children of the Red Algorithm | 141,088 | `The_Meridian_Cycle/txt/Book_2_Children_of_the_Red_Algorithm.txt` | `The_Meridian_Cycle/epub/Book_2_Children_of_the_Red_Algorithm.epub` | `The_Meridian_Cycle/metadata/Book_2_Children_of_the_Red_Algorithm_metadata.json` |
| 3 | The Long Orchard | 150,377 | `The_Meridian_Cycle/txt/Book_3_The_Long_Orchard.txt` | `The_Meridian_Cycle/epub/Book_3_The_Long_Orchard.epub` | `The_Meridian_Cycle/metadata/Book_3_The_Long_Orchard_metadata.json` |
| 4 | Warship Without a War | 160,046 | `The_Meridian_Cycle/txt/Book_4_Warship_Without_a_War.txt` | `The_Meridian_Cycle/epub/Book_4_Warship_Without_a_War.epub` | `The_Meridian_Cycle/metadata/Book_4_Warship_Without_a_War_metadata.json` |
| 5 | The Silence Around Lumen | 141,377 | `The_Meridian_Cycle/txt/Book_5_The_Silence_Around_Lumen.txt` | `The_Meridian_Cycle/epub/Book_5_The_Silence_Around_Lumen.epub` | `The_Meridian_Cycle/metadata/Book_5_The_Silence_Around_Lumen_metadata.json` |
| 6 | Every Door a Mirror | 140,022 | `The_Meridian_Cycle/txt/Book_6_Every_Door_a_Mirror.txt` | `The_Meridian_Cycle/epub/Book_6_Every_Door_a_Mirror.epub` | `The_Meridian_Cycle/metadata/Book_6_Every_Door_a_Mirror_metadata.json` |
| 7 | The Salt Parliament | 140,042 | `The_Meridian_Cycle/txt/Book_7_The_Salt_Parliament.txt` | `The_Meridian_Cycle/epub/Book_7_The_Salt_Parliament.epub` | `The_Meridian_Cycle/metadata/Book_7_The_Salt_Parliament_metadata.json` |
| 8 | Ashes of the Meridian | 140,000 | `The_Meridian_Cycle/txt/Book_8_Ashes_of_the_Meridian.txt` | `The_Meridian_Cycle/epub/Book_8_Ashes_of_the_Meridian.epub` | `The_Meridian_Cycle/metadata/Book_8_Ashes_of_the_Meridian_metadata.json` |
| 9 | The Moon That Remembered Fire | 110,000 | `The_Meridian_Cycle/txt/Book_9_The_Moon_That_Remembered_Fire.txt` | `The_Meridian_Cycle/epub/Book_9_The_Moon_That_Remembered_Fire.epub` | `The_Meridian_Cycle/metadata/Book_9_The_Moon_That_Remembered_Fire_metadata.json` |

## Validation Results

- Manifest contains Books 0-9 in order. All Books 0-9 are marked `complete_txt_epub_available`.
- Metadata files and manifest rows agree on word counts, author, title, number, status, TXT path, EPUB path, and cover path; Book 9's final TXT-derived count validates at exactly 110,000 words under the current tokenizer.
- Each TXT manuscript contains 60 clean sequential chapter headings.
- Each EPUB contains `mimetype` as the first ZIP entry, `OEBPS/content.opf`, `OEBPS/nav.xhtml`, a cover image, and 60 chapter XHTML files.
- EPUB metadata includes the matching title, author, English language metadata, description, and cover asset.
- Each cover PNG validates at 1600x2560.
- The root README includes cover images, reader links, and raw EPUB download links for Books 0-9.
- The series README lists the completed 10-book cycle and this final report.

## Conversion Notes

EPUB files were generated with `The_Meridian_Cycle/tools/build_epub.py` from the TXT manuscripts and metadata JSON files. Cover PNG files were generated with `The_Meridian_Cycle/tools/create_cover.py`.

TXT manuscripts were preserved as the source files; EPUB generation did not rewrite them.

## Production Notes

The series was compressed from an earlier longer-cycle plan into 10 books. Books 5-9 accelerate the convergence of existing continuity arcs to close the cycle without leaving the prior long-series conflicts unresolved. Book 7 was expanded to deepen scene-level development and now exceeds the original 140,000-word minimum. Book 6 has also been expanded above the original 140,000-word minimum and its EPUB has been rebuilt from the preserved TXT manuscript. Book 8 has now been expanded to 140,000 words and its EPUB has been rebuilt from the preserved TXT manuscript. Book 9 has been finalized at the user-approved 110,000-word target and its EPUB has been rebuilt from the preserved TXT manuscript.
