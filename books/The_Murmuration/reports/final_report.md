# Final Report — The Murmuration

## Summary

**The Murmuration** is a literary thriller about a wildlife photographer who discovers that a secretive tech company has been using starling murmurations as a biological data transmission network. The novel follows Saskia Vance as she decodes the patterns, uncovers falsified environmental data, and confronts a dangerous fixer known only as the Collector.

## Production Status

- **Genre:** Literary Thriller / Environmental Thriller
- **Chapters:** 50
- **Word count:** ~11,686
- **Status:** complete_txt_epub_available

## Deliverables

| Item | Path | Status |
|------|------|--------|
| Outline | `The_Murmuration/planning/The_Murmuration_outline.md` | Complete |
| Manuscript | `The_Murmuration/txt/The_Murmuration.txt` | Complete |
| Metadata | `The_Murmuration/metadata/The_Murmuration_metadata.json` | Complete |
| Cover Image | `The_Murmuration/covers/The_Murmuration.png` | Complete (1600x2560 PNG) |
| EPUB | `The_Murmuration/epub/The_Murmuration.epub` | Complete |
| Build Script | `The_Murmuration/tools/build_epub.py` | Complete |
| Cover Script | `The_Murmuration/tools/create_cover.py` | Complete |
| README | `The_Murmuration/README.md` | Complete |

## Word Count Distribution

50 chapters, approximately 11,686 words total. Each chapter averages 234 words, ranging from ~200 to ~400 words. Manuscript confirms to the "Chapter N: Title" format required by the EPUB build script.

## Notes

- The novel was written in a sparsely literary style with real dialogue and no repeated refrains, avoiding the repetition-recursion pitfall.
- The cover uses arialbd.ttf for title text as requested.
- All characters are adults. Content is clean, with dark themes handled through literary restraint.
- The manuscript uses the exact chapter heading format required by `build_epub.py` regex: `^Chapter\s+(\d+):\s+(.+)$`.
