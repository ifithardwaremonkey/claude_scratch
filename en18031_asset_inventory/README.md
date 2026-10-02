# EN 18031 Asset Inventory — Xenon & Cesium Tablets (Valinor)

Working folder for the EN 18031-1 / 18031-2 (2024) asset inventory supporting
iFIT's CSA Group RED Article 3(3)(d)(e)(f) certification. Migrated here from
Claude chat on 2026-10-02 because Google Sheets uploads from chat were failing
(see `ACTION_REPORT_2026-09-25.md` §4–§5).

## Migration status

| Item | Status |
|---|---|
| Action report (handoff context, 2026-09-25) | ✅ `ACTION_REPORT_2026-09-25.md` |
| Live Google Sheet (chosen source of truth, 2026-10-02) | https://docs.google.com/spreadsheets/d/1I8rTEYzTkyLlGrpW8jjURBv6sgxAJCbayEPl-sFG-2Q/edit |
| Snapshot of live Sheet as xlsx | ✅ `iFIT_Xenon_Cesium_EN18031_Asset_Inventory.xlsx` (exported 2026-10-02; Sheet last modified 2026-09-25) |
| Snapshot as diffable CSV, one file per tab | ✅ `csv/` |
| Workbook v2 from chat (MQTT retraction + NIST 8259A updates) | ❌ Abandoned in favour of the live Sheet. Its corrections are **not** in the live Sheet and must be re-applied. |
| CSA Group template (`EN18031_Treadmill_Asset_Inventory_Sample.xlsx`) | ⬜ Not yet imported |
| NIST IR 8259A response PDF (Project 80308127) | ⬜ Not yet imported |
| Console/SKU priority list (image) | ⬜ Never saved as a file; needs re-upload |
| Older Google Sheet from the action report (superseded) | https://docs.google.com/spreadsheets/d/1mrJxtoJ40JwcSh6KfEz5AvzjxA6vjufEDew8kyS-17M/edit |

## State of the live Sheet vs the action report

The live Sheet predates the v2 corrections in `ACTION_REPORT_2026-09-25.md` §3:

- MQTT is still asserted as current architecture in assets 4, 7, 10, 18, 24, 28, 33, 35, 41. Only asset 33 carries a
  manual note that MQTT is not implemented. The §3a retraction still needs applying.
- None of the NIST IR 8259A confirmations (§3b: assets 5, 8, 9, 10, 14, 15, 17, 20, 41) are present.
- The GAP-NNN numbering scheme is mostly absent (only GAP-002 and GAP-007 appear).
- 58 assets, 13 columns (A–M); K–M are the yellow fill-in columns. Tabs: Read Me, Asset Inventory, Interfaces, Where to Look.
- Six reviewer comment threads are open on the Sheet (assets 7, 9, 32, 33). They live on the Sheet; any content update
  must keep the same file ID (in-place edit or File → Import → Replace) so they are not orphaned.

## Merge of v2 corrections (2026-10-02)

`merged_for_import_2026-10-02.xlsx` = live snapshot + section A of `V2_vs_LIVE_DIFF_2026-10-02.md`. Cell-by-cell record in
`MERGE_LOG_2026-10-02.md`. To apply: open the live Sheet → File → Import → Upload → "Replace spreadsheet". This keeps the
file ID and all comment threads. After import, re-export the Sheet here and refresh `csv/` so the snapshot matches.

Known residue not covered by v2: assets 10, 18, 28, 35, 41 still mention MQTT in passing (cols B/K/L/M). Not yet edited.

## Next steps

1. Import `merged_for_import_2026-10-02.xlsx` over the live Sheet (manual, see above), then refresh the snapshot here.
1b. Decide whether to scrub the residual MQTT mentions in assets 10, 18, 28, 35, 41.
2. Work the six open comment threads.
3. Incorporate the Console/SKU priority list (action report §6.1) once re-uploaded.
4. Start the weekly comment-review cycle (action report §6.3).

## Conventions

- `Asset Inventory` sheet: row 1 is the header, asset #N is at row N+1.
  Always verify `ws.cell(row, 1).value` before writing by row number.
- Engineering confirmations from the NIST 8259A response apply to the
  Eway-built Xenon1 only. Do not assume parity for Xenon-V, Xenon1.2, or Cesium.
