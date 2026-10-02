# Action Report — iFIT EN 18031 Asset Inventory (Xenon & Cesium Tablets)

**Prepared:** 2026-09-25
**Purpose:** Handoff context for continuing this work in Claude Code.
**Project:** EN 18031-1 / EN 18031-2 (2024) asset inventory for AOSP Xenon & Cesium tablets (Valinor software suite), part of iFIT's CSA Group RED Article 3(3)(d)(e)(f) certification effort.

---

## 1. Where things stand

This is a **first-pass draft**, compiled from Confluence/Jira research, now entering live engineering/CSA-consultant review. One review session has happened; one confirmed hallucination was caught and corrected (see §3). Zero rows in the register carry formal engineering sign-off beyond the NIST 8259A confirmations described below.

## 2. Files and their state

| File | Location | Status |
|---|---|---|
| **Latest corrected workbook (v2)** | `/mnt/user-data/outputs/iFIT_Xenon_Cesium_EN18031_Asset_Inventory_v2.xlsx` | ✅ Correct, verified cell-by-cell. **Not yet live on Google Sheets** — upload failed (see §4). |
| Original workbook (v1) | `/mnt/user-data/outputs/iFIT_Xenon_Cesium_EN18031_Asset_Inventory.xlsx` | Superseded by v2. Still the live Google Sheet version (stale — has the MQTT error). |
| Live Google Sheet (v1, stale) | https://docs.google.com/spreadsheets/d/1mrJxtoJ40JwcSh6KfEz5AvzjxA6vjufEDew8kyS-17M/edit | Needs replacing with v2 content. |
| Original docx-format register (superseded by the xlsx) | `/mnt/user-data/outputs/Xenon_Valinor_EN18031_Asset_Register.docx` | Historical — CSA's own xlsx template is now the canonical format. |
| CSA Group's original template (reference) | `/mnt/user-data/uploads/EN18031_Treadmill_Asset_Inventory_Sample.xlsx` | Source format being followed. |
| Console/SKU priority list (image, attached 9/25/26) | Not yet saved as a file — was provided as an inline image | **Not yet incorporated** into the register (see §6). |
| NIST 8259A response from iFIT to CSA Group (PDF, attached 9/25/26) | `/mnt/user-data/uploads/Re___EXTERNAL__Request_for_Clarification___NIST_IR_8259A_Assessment__Project_80308127.pdf` | Fully incorporated into v2 (see §3). |

## 3. Corrections already applied in v2 (not yet live)

### 3a. MQTT retraction
Rows 4, 24, 33, 53 previously asserted MQTT as confirmed current Valinor architecture (sourced from Confluence pages: *Event Bus over MQTT*, *MQTT User Biometrics*, *Apple Watch MQTT Transport*). **These describe a proposed future ToG (Tailor on Glass) tablet project, not current implementation** — flagged by Dave Christensen after live review with the CSA consultant. Corrected to retract the MQTT claim and open a new GAP: *what is the actual current telemetry/biometric transport mechanism, if not MQTT?*

### 3b. NIST IR 8259A engineering-confirmed findings
Source: official iFIT response to CSA Group (Mindi Strong → Albert Bennett, 9/25/26, Project 80308127, **Eway Xenon1 tablet specifically**). This is the first engineering-confirmed, submitted-to-certifier source in the register. Applied to:

| Row | Asset | Update |
|---|---|---|
| 5 | Cloud API tokens / OAuth | Credential storage path confirmed (`GlassOS-Service`, `GLSUSRAUTH_CREDENTIALS_STORAGE.xml`) — confirms the GLS-913 risk (plaintext SharedPreferences + FBE-only protection), doesn't resolve it |
| 8 | Hard-coded credentials | Partial — USB debugging lockdown confirmed; hardcoded-credential question (H1-456 precedent) still open |
| 9 | Web/local session keys (N/A) | Kiosk lockdown corroborates the NOT APPLICABLE finding |
| 10 | Firmware signature key / AVB | **AVB/verified boot confirmed enabled** — but only for Xenon1/Eway. Xenon-V and Xenon1.2 remain open per the earlier Confluence finding (do not assume parity) |
| 14 | Anti-rollback | Confirmed at the OS/build-timestamp layer for Xenon1 — distinct from Cesium's separately-confirmed chip-level absence |
| 15 | Authentication mechanism | **GAP-014 resolved** — exact lockout/throttling figures captured (10 failed attempts, 20/48 per-15-min throttle, etc.) |
| 17 | Secure update mechanism | **GAP-019 resolved** for Xenon1/Eway — RSA-2048 + SHA-256 OTA signing, APK Signature Scheme v2, signer continuity |
| 20 | Secure storage | Backup/extraction controls added (`allowBackup=false`) |
| 41 | Logs/diagnostics | Partial — HTTP log redaction confirmed; the WOLF- ticket PII-in-CS-logs issue is separate and still open |

**Important scope nuance baked into every "resolved" row above:** confirmations are specific to the **Eway-built Xenon1** tablet. Xenon-V, Xenon1.2, and Cesium are not automatically covered and remain open per their original status.

## 4. Open technical issue: Google Sheets upload failing

The last attempt to push v2 to Google Sheets via `mcp__Google_Drive__create_file` (with `contentMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` to trigger conversion) returned: `Request contains an invalid argument.`

**Context for debugging:**
- The same approach worked earlier in this session for the v1 upload (succeeded, produced the live Sheet linked above).
- The base64 payload for v2 was generated via `base64 -w 0 working.xlsx` in the sandbox and passed as the `base64Content` parameter.
- Earlier in this session, a *different* base64 round-trip (downloading the live Sheet's content back into the sandbox) failed with a corruption error (`number of data characters cannot be 1 more than a multiple of 4`) — that was abandoned in favor of rebuilding from the last-known-good local file, which is the v2 file now sitting correct on disk.
- The upload failure this time may be a transient API issue, a payload-size/formatting issue, or something about how the base64 string was passed through the tool call (possible truncation or whitespace injection given the string is ~48KB).

**Suggested next steps for Claude Code:**
1. Retry the upload as-is — may have been transient.
2. If it fails again, verify the base64 string has no injected whitespace/newlines (write it to a file and re-read programmatically rather than passing through a chat-message code path, if that distinction is available in Claude Code's tool surface).
3. Confirm the Google Drive connector/tool schema hasn't changed `create_file`'s required parameters.
4. If it continues to fail, fall back to presenting `iFIT_Xenon_Cesium_EN18031_Asset_Inventory_v2.xlsx` as a downloadable file and having a human manually re-upload/replace the Google Sheet content (File → Import → Replace spreadsheet, in Google Sheets UI) — this also sidesteps the earlier-identified limitation that Claude's Drive tools can't update an existing Sheet's content in place (only create new or edit metadata).

## 5. Standing limitation: no in-place Google Sheet editing

Confirmed earlier in this session: the available Google Drive tools (`create_file`, `search_files`, `read_file_content`, `download_file_content`, `copy_file`, `get_file_metadata`, `get_file_permissions`, `list_recent_files`, `share_file`, `trash_file`, `update_file`) do not include a way to push new *content* into an existing Sheet — `update_file` only changes metadata (e.g. title). Every revision currently means a **new file / new Google Sheet link**, which breaks any comment threads or @-tags collaborators added to the previous version.

**User preference on record (saved to memory):** when revising Google Sheets/Docs that colleagues have commented on or tagged for review, read existing comments first and account for them in the revision rather than silently replacing the file. Given the tooling limitation, the practical compromise agreed with the user is: read comments before revising, fold their substance into the new version's content, and clearly flag that the link will change.

If Claude Code has access to the Google Sheets API directly (rather than only the Drive MCP connector), it's worth checking whether `spreadsheets.values.update` or batchUpdate calls are available — that would allow true in-place editing and should be preferred going forward if accessible.

## 6. Pending work — not yet started

1. **Console/SKU priority list.** An image was shared (9/25/26) listing Console PN, associated SKUs, tablet size (10"/16"/24"), test sample, test start/end dates, and modality (Treadmill/Aerobic), with a note: *"Will go to Cesium when INT model goes to Stannite."* This has not yet been cross-referenced into the asset register. Suggested use: sequence the asset-by-asset decision tree walkthrough to match physical test completion order, and/or map each Console PN to its underlying tablet platform (Xenon vs. Cesium) where currently ambiguous.

2. **iconservice.com evaluation.** Confirmed via direct fetch: this is a **public consumer-facing parts/manual-ordering portal** (model lookup → user manuals, replacement parts, assembly videos). It is **not a substitute for Confluence/Jira** on internal engineering/security details (AOSP versions, encryption implementation, debug port state, etc.) — those aren't published there. It could supplement the register for externally-verifiable facts (SKU-to-model mapping, physical specs) but should be treated as a tertiary source, clearly flagged as public-source-only where used, not a replacement for the primary Confluence/Jira research path.

3. **Weekly review cadence (agreed, not yet run).** Plan: pull all collaborator comments/tags added to the live Google Sheet since the last pass, fold each into a revision, produce a corrected sheet, and report gap-closure progress (how many of the ~32 numbered GAP items have moved from open to confirmed/resolved). This has not yet executed as a cycle — today's MQTT fix and NIST 8259A pass are effectively the first (manual) instance of it, triggered mid-session rather than on a weekly schedule.

## 7. Gap register snapshot (as of v2, pre-upload)

Original severity breakdown: **7 Critical, 8 High, 13 Medium, 4 Low** (32 numbered GAP items), plus several unnumbered open items tied to the 6 iFIT-specific rows added beyond CSA's template (brainboard control-link authentication, USB port exposure, etc.).

**Resolved/confirmed in this session:** GAP-014 (auth lockout), GAP-019 (OTA/APK signing, Xenon1/Eway only). **Partially addressed:** GAP-004 (credential storage — confirmed-as-designed, not fixed), GAP-029 (log PII — HTTP path only). **Still fully open and Critical:** JTAG/debug-port state on Xenon-V/Xenon1.2, SELinux enforcing mode, hardcoded-credential re-verification (H1-456 precedent), brainboard control-link authentication, DLM-1 factory-reset crypto-erase.

## 8. Row-numbering convention (to avoid repeating a bug hit twice this session)

In the `Asset Inventory` sheet: **row 1 is the header; asset #N is always at row N+1.** This tripped up two separate correction passes in this session (content landed one row off from intended). Any future script touching this sheet by row number should verify against `ws.cell(row, 1).value` (the asset number column) before writing, not just compute `row = asset_num + 1` blind.

## 9. Key sources referenced this session

- Confluence: *Android Tablet Security*, *Tablet Bluetooth Requirements*, *EncryptedSharedPreferences Xenon Tablet Issue*, *CVTE Xenon1*, *Cesium SystemSpec*, *MQTT User Biometrics* (now known to be future/proposed), *Event Bus over MQTT* (same), *Historical Form Tracking*, *3rd Party Apps by User*, *Valinor Error Code Documentation*, *Xenon Firmware Updates*, *Tablet and Brain Board Variations*, *ICON BLE OTA Service*
- Jira: GLS-913 (Keystore bug), H1-456 (HackerOne hardcoded credential, legacy Malata units), TROL-4827 (camera test), VAL-8960 (Ethernet reliability), TSCH-756 (Guest Mode), WOLF- tickets (PII in CS logs)
- External: iFIT's 9/25/26 NIST IR 8259A response to CSA Group (Project 80308127, Eway Xenon1) — the first engineering-confirmed source
- CSA Group template: `EN18031_Treadmill_Asset_Inventory_Sample.xlsx`
