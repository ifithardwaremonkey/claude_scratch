# Paste list — Revision 4 (MQTT reinstated, with source URLs), 2026-10-02

28 cells. Base is the live Sheet as of your edits today. Name Box → address → Enter (edit mode) → select all → paste → Tab.

## Tab: Read Me

**A35**

```
[REVERSED 10/2/26 — see Revision 4] 1. CORRECTION: 'MQTT' credentials/transport retracted from rows 4, 24, 33, 53 on the Asset Inventory sheet. That architecture (Event Bus over MQTT, MQTT User Biometrics, Apple Watch MQTT Transport Confluence pages) is a proposed FUTURE ToG (Tailor on Glass) tablet project, not current Valinor implementation — flagged by Dave Christensen after live review with the CSA consultant. Actual current telemetry transport mechanism is now an open GAP.
```

**A45**

```
[REVERSED 10/2/26 — see Revision 4] 3. Residual MQTT mentions scrubbed from Asset Inventory rows 5, 11, 19, 29, 34, 36, 42 (assets 4, 10, 18, 28, 33, 35, 41). Current product does not use MQTT. Where a transport/endpoint cell is concerned, a one-line 'Future note' records that a proposed ToG project may add an MQTT-like service, explicitly out of current scope, so the claim is not re-introduced by mistake.
```

**A46**

```
[REVERSED 10/2/26 — see Revision 4] 4. Same MQTT scrub applied to Interfaces row 11 (Cloud backend connection) and Where to Look step 7 (Cloud link).
```

**A48**

```
CHANGELOG — Revision 4 (10/2/26)
```

**A49**

```
1. MQTT reinstated. Retail-2026-04 release notes (Confluence CIED) and Jira ELD-2970 (Done, QA passed 6/23/26) show the MQTT client (AWS IoT, mqtt-glassos-bridge) shipping on embedded consoles. The 9/25/26 verbal retraction conflated the shipped Apple Watch MQTT integration with separate platform event-bus proposals. Rows 5, 11, 19, 25, 29, 34, 36, 42, Interfaces 11 and Where to Look 7 rewritten concisely against the shipped implementation.
Sources: https://ifitdev.atlassian.net/wiki/spaces/CIED/pages/4918411394/2026-06-24+Retail-2026-04+Tier+3+Build#Apple-Watch-MQTT (release note, ELD-2970); https://ifitdev.atlassian.net/wiki/spaces/AV/pages/4734451720/Event+Bus+over+MQTT+v2 (bus protocol spec).
```

**A50**

```
2. New open items from the MQTT review: production BridgeConfig adapter set (WORKOUT_COMMANDS), console-side storage of MQTT session credentials, authorizer token validation on connect, Xenon and Cesium build coverage.
```

## Tab: Asset Inventory

**B5**

```
Cloud API tokens / OAuth refresh tokens / MQTT session credentials
```

**K5**

```
OAuth tokens: GlassOS-Service SharedPreferences, GLSUSRAUTH_CREDENTIALS_STORAGE.xml (confirmed, NIST 8259A response 9/25/26). MQTT credentials: issued per session by mqtt-bridge /v1/discover with a connection-scoped IAM policy; console-side storage not documented (assume in-memory; confirm).
```

**L5**

```
Valinor cloud client (OkHttp GraphQL over HTTPS); MQTT client (AWS IoT via mqtt-glassos-bridge, shipped Retail-2026-04, ELD-2970).
```

**M5**

```
Xenon: EncryptedSharedPreferences disabled by OEM Keystore bug (GLS-913), so OAuth tokens sit in plaintext SharedPreferences with FBE as the only protection (GAP-004). Cesium: not independently confirmed. MQTT credentials are short-lived and derived from the OAuth token; storage location to confirm. Note: a 9/25/26 verbal retraction of MQTT was reversed 10/2/26 on release evidence (ELD-2970).
```

**L11**

```
HTTPS/GraphQL API; MQTT over TLS to AWS IoT (port 443).
```

**K19**

```
Android framework BoringSSL; Valinor OkHttp; AWS CRT MQTT5 client (mqtt-glassos-bridge).
```

**L19**

```
All TLS connections (GraphQL HTTPS; MQTT over TLS to AWS IoT).
```

**B25**

```
Cloud client (HTTPS/GraphQL + MQTT over AWS IoT)
```

**K25**

```
OkHttp GraphQL client in Valinor APKs; mqtt-client-api / mqtt-client-service / mqtt-glassos-bridge (AWS CRT) in the embedded console stack.
```

**M25**

```
HTTPS/GraphQL confirmed (NIST 8259A: TLS only, cleartext disabled). MQTT confirmed shipped in Retail-2026-04 (ELD-2970, QA passed 6/23/26): AWS IoT Core, TLS on 443, per-session credentials from /v1/discover. Carries workout state and summaries including HR metrics (special category). OPEN: which bridge adapters are enabled in production, in particular WORKOUT_COMMANDS (phone-to-console start/pause/stop).
Sources: https://ifitdev.atlassian.net/wiki/spaces/CIED/pages/4918411394/2026-06-24+Retail-2026-04+Tier+3+Build#Apple-Watch-MQTT (release note, ELD-2970); https://ifitdev.atlassian.net/wiki/spaces/AV/pages/4734451720/Event+Bus+over+MQTT+v2 (bus protocol spec).
```

**B29**

```
Cloud endpoint URL(s) / MQTT discovery endpoint
```

**K29**

```
Valinor BuildConfig / remote config; not user-editable in production builds. MQTT broker URI is obtained at runtime from mqtt-bridge discovery, not stored.
```

**K34**

```
BLE Heart Rate Service (strap/grip sensors) locally; watch HR received over MQTT; workout summaries including average HR published over MQTT (ifithome topics); local workout DB cache.
```

**L34**

```
BLE (HRM strap/grip); MQTT (AWS IoT, watch/phone to console); cloud sync.
```

**M34**

```
CONFIRMED: heart rate crosses MQTT in both directions (production fixes ELD-3152/ELD-3153; Confluence 'Apple Watch — MQTT Transport'). Special-category health data (GDPR Art. 9), highest privacy priority on both platforms. Topics are user- and connection-scoped under a per-connection IAM policy. OPEN: confirm the AWS IoT custom authorizer validates the iFIT token on every connect.
Sources: https://ifitdev.atlassian.net/wiki/spaces/CIED/pages/4918411394/2026-06-24+Retail-2026-04+Tier+3+Build#Apple-Watch-MQTT (release note, ELD-2970); https://ifitdev.atlassian.net/wiki/spaces/AV/pages/4734451720/Event+Bus+over+MQTT+v2 (bus protocol spec).
```

**K36**

```
Derived from workout history and cloud-synced workout events (GraphQL; MQTT workout-state and summary topics).
```

**K42**

```
Valinor Workout Player app; GlassOS Sindarin (brainboard bridge for speed/incline sensors); MQTT bridge adapters (HR, workout state, summary).
```

**M42**

```
CONFIRMED (Workout Player in Club-2026-03 build; MQTT bridge shipped Retail-2026-04). OPEN: WORKOUT_COMMANDS adapter state in production. If enabled, the phone can start/pause/stop a workout over MQTT, which is ACM/AUM relevant.
```

## Tab: Interfaces

**D11**

```
Telemetry, account sync, OTA delivery, GraphQL API over HTTPS; MQTT over AWS IoT (watch/phone to console: HR, workout state, summaries, optional workout commands).
```

**H11**

```
Primary remote interface for nearly all Security, Network and Privacy assets. MQTT confirmed shipped in Retail-2026-04 (ELD-2970); see Confluence 'Apple Watch — MQTT Transport'. OPEN: production BridgeConfig adapter set.
Sources: https://ifitdev.atlassian.net/wiki/spaces/CIED/pages/4918411394/2026-06-24+Retail-2026-04+Tier+3+Build#Apple-Watch-MQTT (release note, ELD-2970); https://ifitdev.atlassian.net/wiki/spaces/AV/pages/4734451720/Event+Bus+over+MQTT+v2 (bus protocol spec).
```

## Tab: Where to Look

**D7**

```
TLS keys, API/OAuth tokens, MQTT session credentials, cloud endpoint config, personal data in transit
```

**E7**

```
iFIT: GraphQL HTTPS API (OkHttp) plus MQTT over TLS to AWS IoT (AWS CRT client, per-session credentials from /v1/discover). Certificate pinning status not confirmed; recommend explicit check.
Sources: https://ifitdev.atlassian.net/wiki/spaces/CIED/pages/4918411394/2026-06-24+Retail-2026-04+Tier+3+Build#Apple-Watch-MQTT (release note, ELD-2970); https://ifitdev.atlassian.net/wiki/spaces/AV/pages/4734451720/Event+Bus+over+MQTT+v2 (bus protocol spec).
```
