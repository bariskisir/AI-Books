# The Horse Whisperer's Daughter

**Genre:** Rural Fiction / Horse Racing Drama  
**Author:** Barış Kısır  
**Status:** Complete (txt + epub)

## About

Ellie McAllister has spent her whole life on her family's Kentucky horse farm, Shadow Hill, learning her craft from a father known throughout the Bluegrass as a horse whisperer. But the farm is drowning in debt, her father's health is failing, and the bank is circling.

Their last chance is a damaged three-year-old colt named Midnight — a horse with blazing speed and a shattered spirit. To save the farm, Ellie must do what no one believes she can: train a broken horse to win the Kentucky Derby.

## Files

| File | Path |
|------|------|
| Manuscript | `The_Horse_Whisperers_Daughter/txt/The_Horse_Whisperers_Daughter.txt` |
| EPUB | `The_Horse_Whisperers_Daughter/epub/The_Horse_Whisperers_Daughter.epub` |
| Cover | `The_Horse_Whisperers_Daughter/covers/The_Horse_Whisperers_Daughter.png` |
| Outline | `The_Horse_Whisperers_Daughter/planning/The_Horse_Whisperers_Daughter_outline.md` |
| Metadata | `The_Horse_Whisperers_Daughter/metadata/The_Horse_Whisperers_Daughter_metadata.json` |

## Characters

- **Ellie McAllister** — Horse trainer trying to save her family's farm
- **Dan McAllister** — Her father, the legendary horse whisperer
- **Midnight** — A damaged thoroughbred colt with untapped speed
- **Cole Landry** — Wealthy rival trainer who wants Shadow Hill
- **Rosa Vasquez** — Loyal stable hand
- **Dr. Alice Chen** — Equine veterinarian

## Build

```bash
# Generate cover
python3 "The_Horse_Whisperers_Daughter/tools/create_cover.py" \
  --metadata "The_Horse_Whisperers_Daughter/metadata/The_Horse_Whisperers_Daughter_metadata.json" \
  --out "The_Horse_Whisperers_Daughter/covers/The_Horse_Whisperers_Daughter.png"

# Build EPUB
python3 "The_Horse_Whisperers_Daughter/tools/build_epub.py" \
  --metadata "The_Horse_Whisperers_Daughter/metadata/The_Horse_Whisperers_Daughter_metadata.json" \
  --cover "The_Horse_Whisperers_Daughter/covers/The_Horse_Whisperers_Daughter.png" \
  --out "The_Horse_Whisperers_Daughter/epub/The_Horse_Whisperers_Daughter.epub"
```
