# EN 18031 Asset Inventory — Xenon & Cesium Tablets (Valinor)

Working folder for the EN 18031-1 / 18031-2 (2024) asset inventory supporting
iFIT's CSA Group RED Article 3(3)(d)(e)(f) certification. Migrated here from
Claude chat on 2026-10-02 because Google Sheets uploads from chat were failing
(see `ACTION_REPORT_2026-09-25.md` §4–§5).

## Migration status

| Item | Status |
|---|---|
| Action report (handoff context, 2026-09-25) | ✅ `ACTION_REPORT_2026-09-25.md` |
| Workbook v2 (`iFIT_Xenon_Cesium_EN18031_Asset_Inventory_v2.xlsx`) — latest correct version | ⬜ Not yet imported (still only in the chat sandbox / local download) |
| Workbook v1 (superseded, matches stale live Sheet) | ⬜ Not imported; low priority |
| CSA Group template (`EN18031_Treadmill_Asset_Inventory_Sample.xlsx`) | ⬜ Not yet imported |
| NIST IR 8259A response PDF (Project 80308127) | ⬜ Not yet imported |
| Console/SKU priority list (image) | ⬜ Never saved as a file; needs re-upload |
| Live Google Sheet (v1, stale) | https://docs.google.com/spreadsheets/d/1mrJxtoJ40JwcSh6KfEz5AvzjxA6vjufEDew8kyS-17M/edit |

## Next steps

1. Upload the v2 workbook here so it becomes the source of truth under git.
2. Replace the stale Google Sheet content with v2 (manual File → Import → Replace, or via Drive connector if upload works from here).
3. Incorporate the Console/SKU priority list (action report §6.1).
4. Start the weekly comment-review cycle (action report §6.3).

## Conventions

- `Asset Inventory` sheet: row 1 is the header, asset #N is at row N+1.
  Always verify `ws.cell(row, 1).value` before writing by row number.
- Engineering confirmations from the NIST 8259A response apply to the
  Eway-built Xenon1 only. Do not assume parity for Xenon-V, Xenon1.2, or Cesium.
