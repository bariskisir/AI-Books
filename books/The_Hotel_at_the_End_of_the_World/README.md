# The Hotel at the End of the World

**Genre:** Surreal Fiction  
**Author:** Barış Kısır  
**Status:** Complete (txt + epub available)  

## Synopsis

Travel writer Leo Mercer accepts an assignment to review a mysterious hotel in remote Patagonia. The Hotel at the End of the World is not on any map. Its concierge knows every guest's name before they speak. Inside, each floor is a different decade — 1920s speakeasies, 1950s diners, 1970s discos, and floors that show the future. The concierge knows the death date of every guest who checks in.

On the 1920s floor, Leo meets a woman in blue who has been trapped in the hotel since 1968, neither alive nor dead. As he explores the floors and uncovers the hotel's secrets, Leo must confront his own buried past and decide whether knowledge of his end is a gift or a curse.

## Files

| File | Path |
|------|------|
| Manuscript | `txt/The_Hotel_at_the_End_of_the_World.txt` |
| EPUB | `epub/The_Hotel_at_the_End_of_the_World.epub` |
| Cover | `covers/The_Hotel_at_the_End_of_the_World.png` |
| Outline | `planning/The_Hotel_at_the_End_of_the_World_outline.md` |
| Metadata | `metadata/The_Hotel_at_the_End_of_the_World_metadata.json` |

## Tools

- `tools/build_epub.py` — Build the EPUB from manuscript
- `tools/create_cover.py` — Generate the cover image

## Build Commands

```bash
# Generate cover
python3 tools/create_cover.py --metadata metadata/The_Hotel_at_the_End_of_the_World_metadata.json --out covers/The_Hotel_at_the_End_of_the_World.png

# Build EPUB
python3 tools/build_epub.py --metadata metadata/The_Hotel_at_the_End_of_the_World_metadata.json --cover covers/The_Hotel_at_the_End_of_the_World.png --out epub/The_Hotel_at_the_End_of_the_World.epub
```
