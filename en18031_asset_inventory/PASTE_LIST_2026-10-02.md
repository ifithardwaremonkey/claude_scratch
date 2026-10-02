# Cell-by-cell paste list — live Sheet → merged (2026-10-02)

Use this if File → Import orphans the comment threads. Paste each value into the named cell of the live Sheet.
Pasting into existing cells does not touch tab IDs, so comment anchors are untouched.
Total cells to paste: 44

## Tab: Read Me  (12 cells)

**A29**

```
Yellow cells = to be completed by the manufacturer. Blue rows = Security assets. Green rows = Network assets. Pink rows = Privacy assets. Grey rows = confirmed NOT APPLICABLE.
```

**A34**

```
CHANGELOG — Revision 2 (9/25/26)
```

**A35**

```
1. CORRECTION: 'MQTT' credentials/transport retracted from rows 4, 24, 33, 53 on the Asset Inventory sheet. That architecture (Event Bus over MQTT, MQTT User Biometrics, Apple Watch MQTT Transport Confluence pages) is a proposed FUTURE ToG (Tailor on Glass) tablet project, not current Valinor implementation — flagged by Dave Christensen after live review with the CSA consultant. Actual current telemetry transport mechanism is now an open GAP.
```

**A36**

```
2. NEW SOURCE: iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — the first ENGINEERING-CONFIRMED, submitted-to-certifier source in this register. Rows updated: 5 (credential storage path/mechanism confirmed), 8 (kiosk lockdown corroboration), 9 (partial — USB debugging lockdown, but hardcoded-credential question still open), 10 (AVB/verified boot CONFIRMED for Xenon1/Eway specifically), 14 (anti-rollback CONFIRMED for Xenon1/Eway, software/timestamp-layer), 15 (auth lockout thresholds RESOLVED), 17 (OTA + APK signature verification RESOLVED for Xenon1/Eway), 20 (backup/extraction controls added), 41 (partially addressed — HTTP log redaction confirmed, CS-log PII exposure still open).
```

**A37**

```
3. IMPORTANT SCOPE NUANCE: the NIST 8259A response is specific to the Eway-built Xenon1 tablet. Several 'RESOLVED' items above apply to that variant only — Xenon-V, Xenon1.2, and Cesium are NOT automatically covered by the same confirmation and remain open per their original GAP status unless separately confirmed.
```

**A38**

```
4. Zero rows in this register carry engineering sign-off beyond what's captured above — everything else remains sourced from Confluence/Jira documentation review, not validated by iFIT engineering or accepted by CSA Group.
```

**A40**

```
Pending: console/SKU priority test list (attached 9/25/26) not yet cross-referenced into this register.
```

**A42**

```
CHANGELOG — Revision 3 (10/2/26)
```

**A43**

```
1. Merged Revision 2 corrections (items 1–4 above) into this live sheet. Only the corrected cells were ported: Asset Inventory rows 5, 8, 9, 10, 14, 15, 17, 20, 25, 34, 56 (cols B/K/L/M as applicable). All reviewer edits made directly in this sheet since 9/18/26 (asset 1 annotations, candidate assets rows 60–66, scoping notes rows 74–77, Interfaces rows 14–18, ArcX note) were preserved unchanged.
```

**A44**

```
2. Source of truth is now this Google Sheet; a git-tracked snapshot (xlsx + per-tab CSV) is kept in the claude_scratch repo under en18031_asset_inventory/.
```

**A45**

```
3. Residual MQTT mentions scrubbed from Asset Inventory rows 5, 11, 19, 29, 34, 36, 42 (assets 4, 10, 18, 28, 33, 35, 41). Current product does not use MQTT. Where a transport/endpoint cell is concerned, a one-line 'Future note' records that a proposed ToG project may add an MQTT-like service, explicitly out of current scope, so the claim is not re-introduced by mistake.
```

**A46**

```
4. Same MQTT scrub applied to Interfaces row 11 (Cloud backend connection) and Where to Look step 7 (Cloud link).
```

## Tab: Asset Inventory  (28 cells)

**B5**

```
Cloud API tokens / OAuth refresh tokens
```

**K5**

```
val-local-storage / GlassOS-Service SharedPreferences: /data/data/com.ifit.glassos_service/shared_prefs/GLSUSRAUTH_CREDENTIALS_STORAGE.xml (path CONFIRMED per official NIST 8259A response, 9/25/26).
```

**L5**

```
Valinor cloud client (OkHttp GraphQL over HTTPS). (Prior 'MQTT client (mqtt-client-api)' reference retracted 10/2/26 — not in current product.)
```

**M5**

```
CORRECTED 9/25/26: earlier entry cited 'MQTT credentials' as a confirmed CSP. Per Dave Christensen (Asset Owner), the MQTT event-bus architecture (Event Bus over MQTT, MQTT User Biometrics, Apple Watch MQTT Transport Confluence pages) describes a PROPOSED FUTURE ToG (Tailor on Glass) tablet project, NOT current Valinor implementation. MQTT is NOT implemented on Xenon or Cesium today. GAP-004 (SharedPreferences/GLS-913 Keystore bug) still applies to the OAuth/API tokens that ARE current, but the MQTT-specific claim is retracted. NEW OPEN GAP: what is the actual current transport mechanism for biometric/telemetry data, if not MQTT? Needs engineering confirmation — do not assume GraphQL/HTTPS without checking.

ENGINEERING-CONFIRMED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier): credentials are persisted by a single privileged platform service (GlassOS-Service) at the path above; other apps hold credentials in memory only for process lifetime. Protection is FBE at rest + Linux UID sandboxing (0700 perms, kernel-enforced) + mTLS client-cert-authenticated IPC for retrieval — NOT application-layer encryption. This CONFIRMS the GLS-913 risk profile (plaintext SharedPreferences) rather than resolving it: the file itself is not separately encrypted, protection is entirely at the OS/sandbox layer. GAP-004 status: CONFIRMED-AS-DESIGNED (this is iFIT's stated architecture, submitted to CSA Group as the answer) — but specific to the Eway Xenon1 tablet; Cesium not yet independently confirmed.
```

**M8**

```
NOT APPLICABLE — no local web configuration service is exposed by Valinor/GlassOS on Xenon or Cesium in any reviewed Confluence architecture document (Event Bus over MQTT; Valinor Error Code Documentation). All configuration occurs via native Android UI or the cloud GraphQL API; there is no local session-cookie mechanism. Row greyed out and excluded from further decision-tree analysis absent new evidence.

CORROBORATED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier): production consoles run as a locked-down kiosk appliance; the stock Android web browser, file manager, documents UI, email, camera app, MTP, and platform dev tools are disabled at the package level; system UI runs in global immersive mode; no user-reachable path to Settings or a file browser exists. This independently corroborates the NOT APPLICABLE finding for this row.
```

**M9**

```
CRITICAL OPEN GAP, tied to a CONFIRMED HISTORICAL FINDING: HackerOne report H1-456 documents a hardcoded root-access password found in plaintext in Settings.odex on legacy Malata-built iFIT head units (full write-up in new row 57). This exact defect class must be explicitly re-verified as ABSENT on current CVTE/Compal/Eway Xenon and Cesium (Malata/Genio 520) builds before CCK-3 can be asserted — do not assume it is fixed.

PARTIALLY ADDRESSED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier): USB debugging is disabled by default via secure settings on production consoles and enabled only within an 'audited privileged service mode.' Production application packages are non-debuggable (run-as cannot access app-private storage). This reduces exposure but does NOT confirm the absence of hard-coded service-menu credentials themselves — GAP-007 remains open for that specific question; the H1-456 historical finding (row 57) still requires explicit re-verification.
```

**M10**

```
Cesium: Secure Boot CONFIRMED present. Xenon: CRITICAL OPEN GAP — AVB NOT enabled on Xenon-V/Xenon1.2 per Android Tablet Security blog (status shown as '--', 'desired but on hold due to test resources'). Material disparity between the two platforms; Xenon requires resolution or formal risk acceptance before SUM-1/SSM-1 can be asserted.

ENGINEERING-CONFIRMED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier) for Xenon1 (Eway ODM specifically): 'Production consoles boot with verified boot enabled and the bootloader locked.' AVB 2.0/vbmeta with dm-verity runs in enforcing mode on every boot — a tampered image will not boot even if installed. OTA packages are RSA-2048 signed and SHA-256 digest-verified before any partition is written; failure aborts before commit and is logged as a distinct error (not retried/ignored). IMPORTANT NUANCE: this updates the prior GAP-008 (CRITICAL, open) status, but ONLY for Xenon1/Eway specifically. The Confluence 'Android Tablet Security' blog's '--' (not enabled) status was reported for Xenon-V and Xenon1.2 — different model variants, possibly different ODMs/build configs. Treat as a per-variant confirmation, not a blanket resolution: Xenon1/Eway = CONFIRMED enabled; Xenon-V and Xenon1.2 = STILL OPEN, require the same explicit confirmation before assuming parity.
```

**L11**

```
HTTPS/GraphQL API (TLS). Future note: a proposed ToG tablet project may add an MQTT-like pub/sub service; NOT in current Xenon/Cesium scope and excluded from this assessment.
```

**M14**

```
Cesium: CONFIRMED 'Anti-Rollback: No' per MTK BSP spec — CRITICAL finding, Cesium currently has no hardware rollback protection; a downgrade to a vulnerable firmware version cannot be blocked. Requires explicit risk treatment. Xenon: OPEN, tied to AVB status (row 9).

ENGINEERING-CONFIRMED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier) for Xenon1 (Eway): 'The device additionally enforces anti-rollback by comparing the running build's timestamp against the maximum timestamp declared in the update, rejecting downgrades.' This is a software/OTA-installer-level check (build-timestamp comparison), distinct from a hardware rollback-index/eFuse counter. IMPORTANT NUANCE: Cesium's MTK BSP spec separately confirmed 'Anti-Rollback: No' at the CHIP/eFuse level — a different, lower layer than what iFIT just confirmed for Xenon1. Not necessarily contradictory (Xenon1 has OS-level timestamp-based anti-rollback; Cesium's hardware-level rollback index is separately absent and its OS-level equivalent is still unconfirmed). Do not treat Xenon1's confirmation as resolving Cesium's gap.
```

**K15**

```
Centralized at iFIT's identity provider (IdP), not local to the console. Configuration declared as Terraform IaC in a version-controlled repo, applied via automated deployment pipeline (CONFIRMED 9/25/26).
```

**L15**

```
OAuth 2.0 device authorization grant (QR code completed on a second device) or direct credential-forward to the IdP. Failed-attempt counter is keyed to the ACCOUNT identifier, not the device — cannot be bypassed by switching devices/interfaces.
```

**M15**

```
CONFIRMED: Gandalf manages account login (Club-2026-03 build, v1.47.1.1300). OPEN: brute-force lockout / rate-limiting on console PIN and cloud login not confirmed for either platform.

ENGINEERING-CONFIRMED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier), RESOLVES the prior GAP-014 (brute-force lockout, previously open) with exact figures: 10 consecutive failed attempts -> account lockout + email notification with unblock path; per-source IP throttling at 20 pre-auth / 48 registration attempts per 15-minute window; breached-password detection blocks auth and registration; password policy = min length 8, no reuse of last 5, common-password blocklist; iFIT blocks on threshold rather than an incremental delay. Change authority rests with the iFIT Gateway (platform identity) team; staff/admin access is separately federated to Okta, cloud infra access governed by AWS IAM. GAP-014: RESOLVED.
```

**M17**

```
Cesium: chip supports RSA Secure Boot verification but Anti-Rollback=No (row 13). Xenon: AVB not enabled (row 9) weakens OS-level OTA signature enforcement. App-level (Eru): OPEN — confirm APK signature validation before install, both platforms.

ENGINEERING-CONFIRMED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier) for Xenon1 (Eway): OS updates — RSA-2048 signature + SHA-256 digest verification before any partition write; reject-and-abort (not retry/ignore) on failure, distinctly logged; AVB 2.0/dm-verity enforcing on every subsequent boot. APK updates — standard Android APK Signature Scheme v2 (RSA-2048 over whole-file SHA-256), signer-continuity enforced (can't replace with a different-key-signed package regardless of version number), the updater component itself is a platform-signed privileged system app, updates fetched only over TLS/HTTPS (cleartext disabled in production). The MD5 value in the update manifest is explicitly NOT relied on for integrity/authentication — logging/inventory only. GAP-019 (Eru APK signature validation): RESOLVED for Xenon1/Eway. Same nuance as row 10: confirmed for Xenon1/Eway specifically, not yet extended to Xenon-V, Xenon1.2, or Cesium.
```

**K19**

```
Android framework BoringSSL; Valinor OkHttp client library.
```

**L19**

```
All TLS connections (GraphQL HTTPS). Future note: a proposed ToG tablet project may add an MQTT-like pub/sub service; NOT in current Xenon/Cesium scope and excluded from this assessment.
```

**M20**

```
CONFIRMED FBE on both platforms. PARTIAL GAP: app-layer EncryptedSharedPreferences disabled on Xenon (GLS-913) — FBE is the only protection for val-local-storage contents there. OPEN: confirm whether Cesium's Keystore has an equivalent defect (different SoC/vendor — do not assume inherited).

CORROBORATED 9/25/26 (iFIT's official NIST IR 8259A response to CSA Group (Mindi Strong to Albert Bennett, 9/25/26, Project 80308127, Eway Xenon1 Tablet) — ENGINEERING-CONFIRMED, submitted to certifier) for Xenon1: metadata encryption enabled on the FBE volume; filenames AES-256-CTS (as previously stated); file CONTENTS use 'the platform default cipher' (not explicitly stated as AES-256 in this response — minor wording difference from earlier register text, worth a follow-up to pin down the exact cipher). Each app runs under its own Linux UID with 0700 private-directory permissions; allowBackup=false and fullBackupContent=false on all production apps, so cached data cannot be extracted via platform or host-side backup tooling (NEW finding, not previously in this register).
```

**B25**

```
Cloud client (HTTPS/GraphQL confirmed; MQTT NOT implemented)
```

**K25**

```
OkHttp GraphQL client in Valinor APKs. (MQTT client library reference retracted — see correction below.)
```

**M25**

```
CORRECTED 9/25/26: MQTT was erroneously listed as confirmed here. It is a future ToG tablet project proposal, not current Valinor architecture. HTTPS/GraphQL remains confirmed (independently corroborated by iFIT's 9/25/26 NIST 8259A response to CSA Group: 'Update packages are retrieved only over TLS (HTTPS), with cleartext transport disabled on production builds'). GAP: actual current transport for real-time telemetry/biometric data (if any exists beyond periodic GraphQL sync) is unconfirmed.
```

**B29**

```
Cloud endpoint URL(s)
```

**K29**

```
Valinor BuildConfig / remote config; not user-editable in production builds. (Prior 'MQTT broker URL' wording retracted 10/2/26 — no broker in current product. Future note: a proposed ToG tablet project may add an MQTT-like pub/sub service; NOT in current Xenon/Cesium scope and excluded from this assessment.)
```

**K34**

```
BLE Heart Rate Service (HRM strap/grip sensors) locally; local workout DB cache. Cloud transport mechanism CORRECTED 9/25/26 — see Notes.
```

**L34**

```
BLE (HRM strap/grip sensors); cloud sync (transport mechanism is an open gap — see col M).
```

**M34**

```
CORRECTED 9/25/26: 'MQTT v1/u/<userId>/bio/hr' transport claim retracted — that architecture is a proposed future ToG tablet project, not current Valinor implementation, per Dave Christensen. Special-category health data (GDPR Art. 9) classification stands regardless of transport mechanism. OPEN GAP: actual current cloud transport for heart-rate/biometric data not confirmed — needs engineering confirmation before this row can be closed.
```

**K36**

```
Derived from workout history and cloud-synced workout event timestamps (transport per row 34 — currently an open gap).
```

**K42**

```
Valinor Workout Player app; GlassOS Sindarin (brainboard bridge for speed/incline sensors). Cloud transport for biometrics: see row 34 (open gap).
```

**M42**

```
CONFIRMED (Workout Player component present in Club-2026-03 build). Prior 'MQTT biometrics stream confirmed' claim retracted 10/2/26 — MQTT is not implemented on current product.
```

**B56**

```
SoftAP mode (Wi-Fi chip-level capability, Cesium)
```

## Tab: Interfaces  (2 cells)

**D11**

```
Telemetry, account sync, OTA delivery, GraphQL API over HTTPS (carries special-category biometric data). Real-time transport, if any beyond GraphQL sync, is an open gap (Asset Inventory row 34).
```

**H11**

```
Primary remote interface for nearly all Security, Network, and Privacy assets in this register. Prior reference to the Event Bus over MQTT / MQTT User Biometrics Confluence pages retracted 10/2/26 — those describe a proposed future ToG project, not current Valinor. Future note: a proposed ToG tablet project may add an MQTT-like pub/sub service; NOT in current Xenon/Cesium scope and excluded from this assessment.
```

## Tab: Where to Look  (2 cells)

**D7**

```
TLS keys, API/OAuth tokens, cloud endpoint config, personal data in transit
```

**E7**

```
iFIT: GraphQL HTTPS API (OkHttp). Certificate pinning status not confirmed — recommend explicit check. (Prior 'MQTT-over-TLS' reference retracted 10/2/26. Future note: a proposed ToG tablet project may add an MQTT-like pub/sub service; NOT in current Xenon/Cesium scope and excluded from this assessment.)
```
