# MQTT on Xenon/Cesium consoles — status as researched 2026-10-02

**Conclusion: MQTT IS implemented and shipping on the embedded console.** The 9/25/26 retraction (action report §3a, v2, merged into the live Sheet today) was wrong. The original v1 rows were directionally right but cited proposal pages instead of the shipped implementation.

## Evidence (all primary sources, read today)

| Source | What it shows |
|---|---|
| Confluence CIED: [2026-06-24 Retail-2026-04 Tier 3 Build](https://ifitdev.atlassian.net/wiki/spaces/CIED/pages/4918411394) | External console release notes. Section "Apple Watch MQTT" lists ELD-2970 as shipped. Same release carries Cesium support tickets (CRY-614, CRY-687, CRY-699…), so the build targets both platforms. |
| Jira [ELD-2970](https://ifitdev.atlassian.net/browse/ELD-2970) "Integrate MQTT client with embedded console" | Status Done, resolution Done, QA passed 2026-06-23 (Levi Long: phone connected to embedded console over MQTT). Components Retail-2026-04 / iOS-2026-04. Scope: integrate `mqtt-kotlin-sdk` into the embedded console Android stack (glassos-kotlin or rivendell) using AWS IoT MQTT alongside existing gRPC. |
| Jira epic [ELD-2934](https://ifitdev.atlassian.net/browse/ELD-2934) "Apple Watch MQTT" | Status Tier 2 (done category). ~45 child tickets Feb–Jul 2026, including production bug fixes on Retail-05 builds (ELD-3171, ELD-3152 "HR Frozen on Embedded Console MQTT", ELD-3153 "HR Not Displaying on Embedded Console MQTT"). |
| Confluence EL: [Apple Watch — MQTT Transport](https://ifitdev.atlassian.net/wiki/spaces/EL/pages/5079466012) (Aug 18 2026) | "Documents the current-state implementation." Full topic catalog, message shapes, bridge adapters, connection parameters. |
| Confluence AV: [MQTT Auth](https://ifitdev.atlassian.net/wiki/spaces/AV/pages/3992912021) | Discovery/credential model. |
| Jira [ELD-3035](https://ifitdev.atlassian.net/browse/ELD-3035) | Per-adapter `BridgeConfig` gating; all adapters default OFF, host must opt in. |

## What the console actually does (per the Transport page and ELD-2970)

- **Transport:** AWS IoT Core, MQTT5, Android client `AwsIotMqttClient` (AWS CRT SDK via JNI). **TLS on port 443 with ALPN `mqtt`.** Keep-alive 1200 s. QoS 1. No retained messages, no LWT.
- **Credentials (a real CSP):** console calls `PUT /v1/discover` on the `mqtt-bridge` service with the user's iFIT auth token. Response: `connectionId`, AWS IoT endpoint `uri`, optional `customAuthorizerName`, and `mqttCredentials` / `mqttUsername` / `mqttPassword`. Platform mints a **per-connection IAM policy** scoped to `v1/bus/<connectionId>/#`. Credentials are session-scoped and derived from the OAuth token; the bridge disconnects on auth loss and reconnects on valid auth. **Storage location on console not documented — presumably in-memory only; confirm.**
- **Data leaving the console** (HOME adapter): workout state, workout session metadata, live session, **post-workout activity summary incl. averageBpm, calories, distance, time-in-HR-zones** → `v0/u/{userId}/ifithome/{consoleUuid}/…`. HEART_RATE / HEART_RATE_ZONES adapters publish live HR from GlassOS if enabled.
- **Data entering the console:** watch/phone HR via bio bus (ELD-3152/3153 confirm console displays watch HR over MQTT); `DataRequest` replay triggers; and, if `WORKOUT_COMMANDS` is enabled, **`WorkoutCommand` start/pause/resume/stop/skip from the phone** → GlassOS Workout Service. **Which adapters are enabled in the console's `BridgeConfig` is not documented on the pages read — must confirm with the Eldamar/Valinor team.** This matters for ACM/AUM: a remote start/stop path on a treadmill is a control function.
- **Topics:** per-user and per-console scoped (`v0/u/{userId}/…`, `v1/bus/{connectionId}/…`). Legacy v0 user scratchpad is slated for retirement (ELD-3019, backlog).

## What was wrong in the original (v1) rows, and what was wrong in the retraction

- v1 cited *Event Bus over MQTT*, *MQTT User Biometrics*, *Apple Watch MQTT Transport* as sources. The first two are Activity Vertical platform specs (v2 event-bus protocol, bio/hr bus) — design docs, some marked out of date. The third is the current-state implementation doc and was a valid citation. v1's `v1/u/<userId>/bio/hr` topic is real but is the phone→broker route, not the console's.
- The 9/25 verbal correction conflated the platform *event-bus v2 / ToG* proposals with the shipped *Apple Watch MQTT* console integration. They share module names (`mqtt-client-api`, `mqtt-glassos-bridge`) because the console integration consumes the same SDK.

## Rows affected (to be re-corrected, pending Allen's decision)

Asset Inventory: 4 (B, K, L, M), 10 (L), 18 (K, L), 24 (B, K, M), 28 (B, K), 33 (K, L, M), 35 (K), 41 (K, M), 53 (none needed). Interfaces row 11 (D, H). Where to Look step 7 (D, E). Read Me: Revision 2 item 1 and Revision 3 items 3–4 need a Revision 4 counter-entry.

## New open gaps this surfaces

1. Which `BridgeConfig` adapters are enabled on the production console build (WORKOUT_COMMANDS especially).
2. Where discovery-issued MQTT credentials live on the console (memory vs persisted).
3. Whether the AWS IoT custom authorizer validates the iFIT token server-side on every connect (MQTT Auth page shows token passed in username).
4. Confirm MQTT is present on both Xenon and Cesium Retail-2026-04+ builds (release note implies yes).
