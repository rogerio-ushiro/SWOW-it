# SWOW-it

Italian adaptation of the **Small World of Words (SWOW)** word-association dataset. The English
version (SWOW-EN, 2018) records, for each *cue* word, the first words that came to the mind of
thousands of participants. This repo translates that vocabulary into Italian, rebuilds the derived
statistics, and ships a small proof-of-concept web explorer.

## Status

Work in progress. The translation is done in stages, and the Italian dataset is not assembled yet.

| Stage | State |
|---|---|
| Vocabulary extracted from SWOW-EN (cues and responses) | done |
| Scripts to recompute derived files and validate tables | done |
| Pilot + seed translation of cues (`SWOW-IT/traducao/cues.tsv`, 1,003 rows) | done, under review |
| Remaining cues, responses, markers | pending |
| Italian R100 / `strength` / `cueStats` / `responseStats` assembled | pending |

The PoC explorer only shows words that are already translated, so it grows as the translation does.

## Repository layout

| Path | Content |
|---|---|
| `SWOW-EN18/` | Original English CSVs (2018). Read-only input, not versioned. |
| `SWOW-RP22/` | SWOW-RP (2022) reference CSVs. Read-only input, not versioned. |
| `SWOW-IT/traducao/` | Translation tables (TSV, UTF-8) and the translation rules in `GUIA.md`. |
| `scripts/` | Python 3 scripts (standard library only). |
| `web/` | The PoC explorer (plain HTML/CSS/JS + `data.it.json`). |
| `viz/` | An earlier graph view (`index.html` + `data.js`), opens straight from disk. |

### Translation tables

Columns: `en`, `it`, `status`, `nota`. The key is the exact English string
(case matters). `it` is never empty. Status values: `ok`, `ambiguo`, `sem_equivalente`,
`nome_proprio`, `erro_digitacao`. All rules (inflections, case, false friends, register) are in
[`SWOW-IT/traducao/GUIA.md`](SWOW-IT/traducao/GUIA.md).

### Scripts

Run them from the repo root.

| Script | Purpose |
|---|---|
| `scripts/extract_words.py` | Extracts the SWOW-EN vocabulary into `SWOW-IT/traducao/vocab_*.tsv`. |
| `scripts/derive.py` | Recomputes `strength`, `cueStats` and `responseStats` from R100; must match the originals. |
| `scripts/check_table.py <file.tsv>` | Validates a translation table against `GUIA.md`. |
| `scripts/make_batch.py` | Builds translation batches ("cue \| 10 most frequent responses"). |
| `scripts/build_web_data.py` | Builds `web/data.it.json` for the explorer. |
| `scripts/make_viz_data.py` | Builds `viz/data.js`. |

## Running the PoC explorer

Requirements: Python 3 and any modern browser. No install, no build, no dependencies.

1. Go to the repo root:

   ```sh
   cd /Users/rrocco/git/webskunk/rogerio-ushiro/SWOW-it
   ```

2. (Optional) regenerate the data after `cues.tsv` changes. It reads `SWOW-IT/traducao/cues.tsv` and
   `SWOW-EN18/strength.SWOW-EN.R123.20180827.csv`:

   ```sh
   python3 -I scripts/build_web_data.py
   ```

3. Serve the `web/` folder (a server is needed because the page loads `data.it.json` with `fetch`;
   opening the file directly from disk will not work):

   ```sh
   python3 -m http.server 8000 --directory web
   ```

4. Open <http://localhost:8000>. Stop the server with `Ctrl+C`. If the port is busy, use another
   one (e.g. `8765`).

### How to use it

- Type a word (suggestions appear) or click one: the 20 strongest associations are listed, each
  with a bar and its percentage (`R123.Strength`, i.e. response count / N).
- Click any association to open its own associations. The trail at the top (e.g. *cane → gatto → …*)
  is clickable to go back.
- The address keeps the current word (`#cane`), so links can be shared.

### Limits of the PoC

- Only translated cues are nodes (941 words, 18,747 links in the current data). A response shows up
  only if its English string is also a translated cue, because responses are not translated yet.
- Percentages are over all responses given to the cue, including those left out of the list.
- English cues that translate to the same Italian word are merged (counts and N are summed).
- Words removed from `cues.tsv` (`sem_equivalente`, `nome_proprio`, `erro_digitacao`) do not appear.

## Conventions

- Code comments, commit messages: English.
- UI and external-facing text: Italian.
- Original datasets in `SWOW-EN18/` and `SWOW-RP22/` are never modified; outputs go to `SWOW-IT/`.
