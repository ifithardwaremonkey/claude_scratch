# What the v2 workbook changed vs the live Google Sheet

Compared cell-by-cell on 2026-10-02. Both files descend from the same base. The live Sheet is master.
`v2_from_chat.xlsx` is kept only as the donor for the corrections below.

## A. Corrections only v2 has (candidates to port INTO the live Sheet)

Asset Inventory tab. Row = sheet row, asset # = row − 1.

| Row | Asset | Cells | Change |
|---|---|---|---|
| 5 | 4 Cloud API tokens | B, K, M | **MQTT retracted** from asset name. K: credential path confirmed (`GlassOS-Service` SharedPreferences, `GLSUSRAUTH_CREDENTIALS_STORAGE.xml`). M: retraction note + new open gap on actual telemetry transport. |
| 8 | 7 Web session keys (N/A) | M | Appends NIST 8259A corroboration of the N/A finding (kiosk lockdown). |
| 9 | 8 Hard-coded credentials | M | Appends "partially addressed": USB debugging lockdown confirmed; H1-456 re-verification still open. |
| 10 | 9 Firmware-signature key / AVB | M | Appends: AVB/verified boot **confirmed for Xenon1 (Eway) only**. Xenon-V / Xenon1.2 gap stands. |
| 14 | 13 Anti-rollback | M | Appends: Xenon1 (Eway) enforces anti-rollback via build timestamp comparison. Cesium chip-level gap stands. |
| 15 | 14 Authentication mechanism | K, L, M | K/L rewritten: IdP-centralised, Terraform IaC, OAuth 2.0 device grant, account-keyed lockout. M appends **GAP-014 resolved** with figures (10 failed attempts → lockout; per-IP throttling). |
| 17 | 16 Secure update mechanism | M | Appends **GAP-019 resolved** for Xenon1 (Eway): RSA-2048 + SHA-256 OTA verification, APK Signature Scheme v2. |
| 20 | 19 Secure storage | M | Appends: metadata encryption on FBE volume, `allowBackup=false`. |
| 25 | 24 Cloud client | B, K, M | **MQTT retracted**; HTTPS/GraphQL stands, corroborated by NIST response. |
| 34 | 33 Heart-rate data | K, M | **MQTT retracted**; GDPR Art. 9 classification stands; transport is an open gap. ⚠ Live cell M already carries a manual note "MQTT is not implemented - this is an hallucination". v2 text supersedes it. |
| 41 | 40 Logs / diagnostics | M | Appends "partially addressed": Authorization/Cookie headers redacted in HTTP logs; WOLF- CS-log PII gap stands. |
| 54 | 53 Ethernet | L | Removes a stray MQTT client reference. ⚠ v2 replaced the whole cell with "N/A — hardware access path"; the live text ("Physical RJ45 port; active on Xenon1.2 and Cesium") is more useful. Port only the MQTT removal. |
| 56 | 55 SoftAP | B | Adds "(Cesium)" qualifier to the asset name. |

Read Me tab: v2 adds a CHANGELOG block (rows 34–40) describing items 1–4 above and the pending Console/SKU list.
Also five minor wording tweaks (rows 14, 23, 29, 31, 32); row 29 adds "Grey rows = confirmed NOT APPLICABLE" which is worth keeping.

## B. Human edits only the live Sheet has (must be PRESERVED, v2 would overwrite them)

- Asset 1 (row 2): reviewer annotations in B, G, L, M (open-network question, debug UART note, user-build/no-root note).
- Asset 33 (row 34) M: manual MQTT hallucination note (superseded by v2's fuller text, see above).
- Rows 60–66: candidate new assets jotted in column B (GymKit/Argon3, ANT+, eGYM NFC, Samsung Health, Apple Health, Google Health, iFIT personnel).
- Rows 69–72: colour-code key.
- Rows 74–77: scoping notes (TEE not user-accessible, assets 55–56 maybe not user-accessible, Widevine L1 would not trigger EN 18031-3).
- Interfaces row 3 D: ArcX SmartRing marked disqualified/OBS, internal only.
- Interfaces rows 14–18: candidate new interfaces (HR strap, earbuds out of scope, GymKit, ANT+, eGYM NFC).

## C. Identical

Where to Look tab: no differences.

## Merge rule

Start from the live Sheet. Apply only section A, cell by cell. Never overwrite anything in section B.
Two cells need a hand merge: asset 33 col M (take v2 text) and asset 53 col L (keep live text, drop nothing — the MQTT reference v2 removed was not in the live cell anyway).
