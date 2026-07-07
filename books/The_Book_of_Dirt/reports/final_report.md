# Final Report — The Book of Dirt

## Summary

**The Book of Dirt** is an eco-literary novel about soil scientist Dr. Thomas Winton, who discovers that the earth holds a molecular memory of every living thing that has touched it. In drought-stricken Australia, with the help of Aboriginal elder Ruby Djarragun, he uncovers an environmental crime buried by a ruthless developer. The novel explores themes of memory, loss, land rights, and the slow intelligence of the earth.

## Production Status

- **Genre:** Eco-Literary
- **Chapters:** 50
- **Word count:** ~11,203
- **Status:** complete_txt_epub_available

## Deliverables

| Item | Path | Status |
|------|------|--------|
| Outline | `The_Book_of_Dirt/planning/The_Book_of_Dirt_outline.md` | Complete |
| Manuscript | `The_Book_of_Dirt/txt/The_Book_of_Dirt.txt` | Complete |
| Metadata | `The_Book_of_Dirt/metadata/The_Book_of_Dirt_metadata.json` | Complete |
| Cover Image | `The_Book_of_Dirt/covers/The_Book_of_Dirt.png` | Complete (1600x2560 PNG) |
| EPUB | `The_Book_of_Dirt/epub/The_Book_of_Dirt.epub` | Complete |
| Build Script | `The_Book_of_Dirt/tools/build_epub.py` | Complete |
| Cover Script | `The_Book_of_Dirt/tools/create_cover.py` | Complete |
| README | `The_Book_of_Dirt/README.md` | Complete |

## Word Count Distribution

50 chapters, approximately 11,203 words total. Each chapter averages 224 words, ranging from ~200 to ~400 words. Manuscript conforms to the "Chapter N: Title" format required by the EPUB build script.

## Notes

- The novel was written in a sparsely literary style with real dialogue and no repeated refrains, avoiding the repetition-recursion pitfall.
- The cover uses arialbd.ttf for title text as requested. No georgiab.ttf was used.
- The cover features cracked earth, a lone dead tree, red dirt hills, and a harsh Australian sun on a terracotta-ochre gradient.
- The title panel is dark with white text, positioned at y=1920-2560.
- No "A Novel of" subtitle was included on the cover.
- All characters are adults. Content is clean, with dark themes handled through literary restraint.
- The manuscript uses the exact chapter heading format required by `build_epub.py` regex: `^Chapter\s+(\d+):\s+(.+)$`.
- The series line in build_epub.py has been updated to "The_Book_of_Dirt".
