# The Calligrapher's Secret — Final Report

## Production Summary

- **Title:** The Calligrapher's Secret
- **Author:** Barış Kısır
- **Genre:** Literary Historical
- **Chapters:** 50
- **Total Word Count:** 10,137
- **Status:** complete_txt_epub_available

## Files Created

| File | Path |
|------|------|
| Outline | `The_Calligraphers_Secret/planning/The_Calligraphers_Secret_outline.md` |
| Manuscript | `The_Calligraphers_Secret/txt/The_Calligraphers_Secret.txt` |
| Metadata | `The_Calligraphers_Secret/metadata/The_Calligraphers_Secret_metadata.json` |
| Cover Image | `The_Calligraphers_Secret/covers/The_Calligraphers_Secret.png` |
| EPUB | `The_Calligraphers_Secret/epub/The_Calligraphers_Secret.epub` |
| EPUB Build Script | `The_Calligraphers_Secret/tools/build_epub.py` |
| Cover Script | `The_Calligraphers_Secret/tools/create_cover.py` |
| README | `The_Calligraphers_Secret/README.md` |

## Story Summary

Layla bint Yusuf, a master calligrapher in 10th-century Baghdad, works disguised as a male apprentice named Laith in the caliph's library. She falls in love with Hassan, a Persian poet, and hides a love letter within an illuminated manuscript of the Mu'allaqat commissioned for the caliph. The letter survives a thousand years — through the Mongol sack of Baghdad, the Ottoman conquest, European collectors, and modern archives — until a scholar discovers it in the present day.

## Chapter Structure

- **Part I (Chapters 1-12):** The Apprentice — Layla's secret life in the caliph's library, her disguise, and the beginning of her relationship with Hassan.
- **Part II (Chapters 13-25):** The Hidden Letter — The love affair deepens; Layla conceals her letter within the manuscript.
- **Part III (Chapters 26-38):** The Breaking — Layla is exposed by the Caliph, banished from the library, and separated from Hassan.
- **Part IV (Chapters 39-45):** The Thousand Years — The manuscript's journey through centuries of history.
- **Part V (Chapters 46-50):** The Unfolding — Modern scholar Amira Nasr discovers and deciphers the hidden letter.

## Build Pipeline

1. Cover generated: `create_cover.py --metadata metadata/... --out covers/...`
2. EPUB built: `build_epub.py --metadata metadata/... --cover covers/... --out epub/...`
3. All reports written.

## Notes

- No repeated refrains. Prose is literary and spare.
- All characters are adult. Content is clean.
- Chapter headings follow the required format for EPUB build script.
- Cover uses arialbd.ttf for title text (dark panel with white text).
