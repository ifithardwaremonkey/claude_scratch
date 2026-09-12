# Cesium Hardware Root-of-Trust Authorization Plan

**Consolidated test, production and decision plan for burning the SBC eFuse on Cesium AOSP 15 tablets at CVTE, then Malata**

| | |
|---|---|
| Product | Cesium tablet (iFitG520), MediaTek MT8371 / Genio 520 (tool reports MT8189), AOSP 15, A/B seamless update, battery-less console |
| Current build | VKC1_20260909 (software root of trust, fingerprint `:user/dev-keys`) |
| MP-intent build | VKC1_20260919 (expected 19 Sep 2026) |
| Mass production | ~3 Oct 2026 (three weeks from this revision) |
| Revision | 1.0 draft, 12 September 2026 |
| Owner | Allen Middleton (Tablet Engineer, ICON Health & Fitness) |
| Supersedes | Cesium Closed-Config Field Brick-Resistance Test Plan r0.4 (test content carried forward with its case IDs); Android 15 Virtual A/B & AVB 2.0 Resiliency Test Plan v2.0 (glitch matrix carried forward with errata); Remote eFuse MT8371 Feasibility Study (conclusion adopted) |

---

## 0. Decision summary

**1. Field fusing is ruled out.** The feasibility study is adopted in full: eFuse writes on MT8371 are only possible from BROM/DA mode or a preloader self-blow, and self-blow via OTA on a battery-less unit with no hold-up supply is a brick-rate machine. Every Cesium unit is therefore either fused on the production line or never fused. There is no "ship open, close later" path. That makes the per-unit fuse decision permanent in both directions.

**2. Hardware root of trust does not materially raise the probability that a bad OTA bricks a tablet. It changes what happens after a mistake.** The question in the brief is answered in Section 2. On the A/B path (everything `update_engine` writes) a corrupt or truncated payload is rejected before any write regardless of fuse state, and slot fallback is fuse-independent. The fuse adds exposure in three narrower places, none of which a 30-day soak measures well:

- **Key and fuse-image mistakes** become permanent and batch-scale (wrong hash, dev key, leaked key).
- **Every recovery path narrows** to signed artefacts: signed DA, re-signed firmware, older rescue images rejected.
- **A signature failure becomes fatal for that slot** instead of a warning, so A/B fallback must be proven on a fused unit, not assumed from open-unit behaviour.

Those three are controlled by gates, custody and rehearsal before the first unit is fused, not by field time. This is good news for the schedule: the risks that actually differ between open and closed are front-loadable.

**3. The full r0.4 gate set cannot complete in three weeks.** The 30-day fused pilot soak (Group K) alone overruns MP. Two authorization options are defined in Section 3. The recommended posture:

- **Plan to Option A**: MP lot 1 ships on software root of trust (the configuration every fielded Xenon runs and that passed NIST 8259), except a 25–50 unit fused pilot ring built by the MP-intent line process. CVTE fusing of full production is authorized at the first lot after the pilot soak completes and the Tier 0 and Tier 1 gates in Section 4 pass. Malata follows after Tier 2.
- **Allow Option B** (fuse all of MP lot 1) only by an explicit go decision on Day 18 if every Tier 0 STOP-SHIP gate has passed, **and** with the compensating control that no production OTA is pushed to fused units until Tier 3 (rollout controls plus pilot soak) is complete. Since field bricks are OTA-induced, an OTA freeze on the fused population removes the untested exposure during the soak window.

**4. Four items must start today** because they have the longest lead time and each one alone blocks fusing:

1. Revive bricked unit J26080143-0A00076 via forced BROM download (E5). If this cannot be shown, closed configuration is not accepted at all.
2. Resolve the `dev-keys` fingerprint versus ICON certificates (G1, G2) on 0909 now and again on 0919.
3. Key custody (G3, G5): AVB private keys (`img_prvk.pem`, `da_prvk.pem`, `root_prvk.pem`) were posted as Basecamp attachments to a 19-person distribution including ODM client accounts. Keys distributed that way cannot be considered in custody. Decide within 48 hours whether to rotate to an ICON-held key and regenerate `efuse_iFitG520.img` before any MP unit is fused. Rotation costs roughly 3 to 5 days of re-signing and re-test; not rotating means the fleet permanently trusts a key at least 19 people have handled.
4. Written CVTE confirmation of exactly which partitions the OTA payload writes and that preloader/boot0 are never in scope (E1).

---

## 1. Sources and reconciliation

| Source | What it contributes | Trust and scope |
|---|---|---|
| **A. Android 15 Virtual A/B & AVB 2.0 Resiliency Test Plan v2.0** (MediaTek app-note derived) | Glitch matrix PWR-01..04, USR-01, AVB-01; build and kernel configuration table; CTS/VTS module list; 1,000-iteration open-config pass criterion. | Trusted for generic AOSP 15 mechanism. Written for open configuration. Two premises do not hold on this part (below). |
| **B. Cesium Closed-Config Field Brick-Resistance Test Plan r0.4** (two years of Basecamp record with CVTE and Malata) | Program history, 19-item risk register, groups A–N with STOP-SHIP and GATE badges, sample matrix, exit criteria, 16 open questions for the ODMs and MediaTek. | Trusted and platform-specific. Not yet issued to the ODMs. This document carries its case IDs forward unchanged so the two can be read side by side. |
| **C. Remote eFuse Programming MT8371 Feasibility Study** | Fuse programming modes; self-blow pipeline; field failure modes (3.7 V threshold, hash mismatch, magic-key mismatch, unreadable failure log). Verdict: not feasible for field deployment. | Trusted. Its conclusion is adopted; its "enable anti-rollback for field counters" recommendation is **not** adopted (see conflict 1). |
| **D. Cesium 0831 Boot Log Analysis** (this repository) | Corroborating evidence: `keystore2 ROLLBACK_RESISTANCE_UNAVAILABLE`; no reliable RTC, wall clock set to build time each cold boot. | Supporting only. |

### 1.1 Conflicts between trusted sources and how this plan resolves them

| # | Conflict | Resolution in this plan |
|---|---|---|
| 1 | **Anti-rollback.** Source A says `MTK_SECURITY_ANTI_ROLLBACK = yes` is supported and required; Source C recommends relying on it for field version management. Source B records MediaTek stating in Mar 2024 that it cannot be enabled on this project and CVTE reconfirming in Aug 2026 that it remains disabled on 8371. Source D shows the KeyMint side reports rollback resistance unavailable. | Treat anti-rollback as **disabled and to stay disabled for MP** (Group F). A signed known-good older build is then the fleet-wide escape hatch (F1), which matters more on a fused fleet than downgrade protection does. Source A case AVB-01 is rescoped to signature-based rejection only (F2); its "ARB counter check" pass criterion cannot be met. Obtain one written MediaTek statement to close the disagreement (open question 6). Agree a compensating control for signed-but-old pushes (open question 16). |
| 2 | **Virtual A/B.** Source A assumes copy-on-write snapshots and userspace merge (`snapuserd`, `dm-user`) throughout; roughly a third of its cases depend on this. Source B confirms A/B from the paired slot table (M1) but not the snapshot layer. | M2 and M3 run on Day 1. If virtual A/B is not enabled, PWR-02, PWR-04 and USR-01 are re-scoped to plain A/B slot writes rather than reported as failures. |
| 3 | **Verity error handling.** Source A corrects `CONFIG_DM_VERITY_AVB` to `y` for managed restart. Source B case M4 asks to confirm the verity-AVB immediate-invalidate option is **not** selected. | Do not edit kernel configuration on the basis of either document. The binding evidence is behavioural: M5 induces a single-block verity error on a sacrificial fused unit and must produce a controlled restart and slot fallback, never a loop or a brick. Record the actual defconfig and LK hashtree error mode alongside the result. |
| 4 | **Battery threshold.** Source C's 3.7 V cut-off applies to self-blow on battery. Cesium has no battery. | Irrelevant to field OTA (no self-blow ships). Relevant to the factory station: the burn depends entirely on the 12 V bench supply and the manual power sequence, so station power conditioning and interruption behaviour are tested (L2, I4). |
| 5 | **Non-A/B boot chain.** Source A treats non-A/B as deprecated and out of scope. Source B records that the one demonstrated brick on this program was a non-A/B boot stage (corrupt `preloader_a`, intact `preloader_b` did not fail over, no USB enumeration). | Group E is the highest-value group in this plan. E5 is the single stop-ship. |
| 6 | **Iteration counts.** Source A requires 1,000 consecutive passing iterations. Source B requires zero unrecoverable units over a 200-cycle randomised soak. | 1,000 iterations on **open** units (cheap, automated, no scrap). 200 randomised interruptions on **fused** units, bounded by sacrificial hardware, with zero unrecoverable as the binding criterion. |

---

## 2. Does hardware root of trust increase field brick risk?

The brief's hypothesis: the 0909 build already enforces a software root of trust, so a corrupt signature already risks a non-booting unit, and the hardware root of trust may add no brick risk at all.

The hypothesis is **correct for the A/B update path and incorrect for recovery and key handling**. The premise also needs one correction: on the current open configuration the Basecamp record says AVB "runs open/unlocked, signature mismatches are ignored" (Feb 2024) and that the public key "can be replaced directly" (May 2026). On 0909 a wrong signature is very likely tolerated, not fatal. That must be measured on Day 1 (new case A0 below) because it determines how much behaviour actually changes at fusing.

| Failure mode | Open config (software RoT, today) | Closed config (SBC fused) | Marginal risk from fusing |
|---|---|---|---|
| Corrupt, truncated or bit-flipped OTA payload (C1, C2) | Rejected by `update_engine` hash check before any write | Same | **None.** Fuse is not consulted. |
| Delta against wrong source build (C12) | Rejected before write | Same | **None.** |
| Package signed with wrong or test key (C3, C4) | Likely accepted at boot; unit runs foreign code | Slot fails AVB at boot; falls back to previous slot within retry budget | **Low, if fallback works on a fused unit.** Never measured (C5–C10). Security improves. |
| Corrupt `vbmeta`, `boot.img`, hash tree in the inactive slot (C5–C7) | Likely boots with warning or ignored | Fallback to good slot | **Low, conditional on C5–C10 and M5.** |
| Power loss during download, write, post-install, slot switch, first boot (D1–D9, PWR-01..04) | A/B protects; boots good slot | A/B protects; boots good slot | **None on the A/B mechanism itself.** Slot-metadata behaviour (M6–M8) must be verified once; it is fuse-independent. |
| Panic before boot-success marker (C8) | Auto revert | Auto revert | **None.** |
| Corrupt non-A/B stage: preloader / boot0 (E2–E4) | No boot; BROM download mode accepts any image | No boot; observed: no USB enumeration; recovery requires forced BROM entry plus signed DA and signed image | **High until E5 passes.** The only demonstrated brick on the program is this mode. Mitigation is contractual: OTA never writes preloader/boot0 (E1). |
| Wrong key hash, dev key, or leaked private key burned (R2, R3) | N/A: keys replaceable | Permanent, fleet-wide, no rotation | **Critical and new.** Only gates prevent it (G1–G6). |
| Depot re-flash of a failed unit (H1) | Any image, any DA | Signed DA and re-signed image only; earlier rescue images rejected; per-site custody of signed DA | **Medium: cost and process, not probability.** Turns a 10-minute flash into a controlled artefact chain at every service site. |
| Storage bit rot in active slot (C11) | Possibly silent execution of corrupt data | Verity detects, fallback or recovery | Security improves; brick risk unchanged if M5 passes. |
| Factory fuse write itself (L1–L8, I1–I5) | N/A | Manual, ordered, irreversible; mis-sequence leaves unit fused-without-firmware or unfused-but-passed | **Medium, line-side only.** 100-unit CVTE trial with zero failures is encouraging, not sufficient. Malata has no fuse experience at all. |

**Conclusion.** Fusing does not raise the probability that a field OTA fails. It removes the ability to recover from process mistakes with an unsigned image, and it makes any key error permanent. The financial exposure therefore moves from "unforeseen OTA bug" (bounded by staged rollout regardless of fuse state) to "key, image or recovery-procedure error made before MP" (bounded only by the gates in Section 4). The plan is organised around that.

---

## 3. Authorization options and schedule

### 3.1 Options

| | Option A (recommended default) | Option B (stretch, explicit go on Day 18) |
|---|---|---|
| MP lot 1 | Software RoT, plus 25–50 unit fused pilot ring built by the MP-intent line process and placed at ICON-controlled sites | All units fused |
| Fusing authorization for CVTE production | First lot after Tier 0 + Tier 1 pass **and** pilot soak (K1–K3) completes | Day 18, if every Tier 0 STOP-SHIP and Tier 1 gate has passed |
| Compensating control | None needed; fused population is the pilot | **OTA freeze on fused serials until Tier 3 passes.** Backend must be able to target by fuse state (J4 telemetry). |
| Field exposure | Zero fused units in customer hands until proven | Full fused lot in customer hands with no proven fused OTA history; exposure bounded only by the OTA freeze and then by ring sizes |
| Security cost | Lot 1 customer units are permanently open; cannot be fused later | None |
| Schedule cost | Fusing slips one lot; MP date unchanged | None if gates pass; **automatic fall-back to Option A** if any Tier 0 gate fails |
| Financial note | Cost of unfused units is a security-posture and compliance question, not a replacement cost | Cost of a wrong call is replacement of every affected unit plus depot signed-flash cost; no software remedy |

Because fusing is a line step and not a design change, deferring it costs one lot of security posture but no hardware. Fusing prematurely cannot be undone on any unit already shipped. Given the current state of the record (dev-keys fingerprint unresolved, bricked first article not yet revived, keys distributed through Basecamp, preloader failover unexplained), Option A is the default and Option B must be earned.

### 3.2 Three-week schedule to MP

| Days | Track | Content | Exit |
|---|---|---|---|
| 1–2 | Paperwork and baseline | G1, G2 on 0909; G3 custody decision; E1 written partition scope; M1–M4; N1, N2, N10; A0 open-config signature baseline; send open questions 1–16 to CVTE, Malata, MediaTek in one letter | Anti-rollback, virtual A/B and key posture known; test scope fixed |
| 1–10 | Brick recovery (long pole) | E5 on BRICK-1 with CVTE/MediaTek guidance under both chip designators; document exact button, timing and tool version | BRICK-1 boots a signed build, or closed config is not accepted |
| 2–6 | Open units (5) | C1–C13 rehearsal; D1–D9 and PWR-01..04, USR-01 at 1,000 automated iterations; F1–F3 | Every case ends in a booting unit; behaviour baselined |
| 4–10 | Fused sacrificial (5 + spares) | E2–E4, E6; C1–C13 five times each; D7 200-cycle randomised soak; D8 brown-out; M5 verity error; N3 attestation; G4 hash regeneration; G7 fuse map read-back; G9 userspace fuse-write attempts | Zero unrecoverable; every failure mode has a recovery path |
| 8–14 | CVTE line | L1–L8 and I1–I5 witnessed by ICON; G10 build audit; H1–H5 depot at CVTE and at the US service site including a full-image profile (R19) | Station interlocked; per-serial trace; depot proven at two sites |
| 12–18 | Release engineering | J1–J5: pipeline signature gate, rings at 0.1 / 1 / 10 / 100 percent, automatic halt, kill switch, CDN integrity, telemetry incl. fuse state | Bad build halted in a lab ring |
| 14 onward | Pilot | K1: 25–50 fused units built by MP-intent process; K2 two OTA transitions; K3 two random depot recoveries | 30 days, zero unrecoverable (completes after MP) |
| 19 | **Re-test on final build** | Re-run G1, G2, G4, N3, B1, B2, C3, C5, D2, D4, F1, M5 on signed VKC1_20260919. Any re-sign changes hashes; nothing tested on 0909 transfers automatically. Reserve 3 days. | Final artefact pairing signed off (L5) |
| 18 | **Go / No-Go** | Tier 0 and Tier 1 review. Option B only if all pass. | Signed decision record |
| 21 | MP start | Option A or B per decision | |
| MP + 5 to 10 | Malata | Tier 2 transfer and witnessed first-article run before Malata's first fused lot | |

Build 0919 arrives on Day 7 and the reserve for re-test on it is the tightest constraint in this schedule. If 0919 slips past Day 12, Option B is not achievable and Option A applies automatically.

---

## 4. Authorization gates by tier

Gate identifiers are from Plan B (r0.4). **STOP-SHIP** halts the closed-configuration decision. **GATE** must pass before a later group's results are credited or before a line runs.

### Tier 0. Irreversibility gates: before any MP unit is fused, at any ODM

| ID | Gate | Pass criterion | Owner |
|---|---|---|---|
| G1 | STOP-SHIP Build fingerprint | Reads `release-keys` on the signed MP build | CVTE, verified by ICON |
| G2 | STOP-SHIP Certificate chain | `otacert`, `platform.x509.pem` and the AVB image key all resolve to the ICON certificate; none matches an AOSP test key | ICON |
| G3 | STOP-SHIP Key custody | ICON holds or escrows root, img and DA private keys in an HSM or restricted escrow; keys removed from Basecamp; custody documented; decision on rotation recorded | ICON |
| G4 | STOP-SHIP Fuse hash | ICON independently regenerates `sbc_pub_key_hash` from the public key and matches it to read-back from a fused unit | ICON |
| G5 | STOP-SHIP Leak response | Tabletop for signing-key leak after MP; limits accepted in writing because OTP cannot be re-keyed | ICON security |
| G6 | STOP-SHIP ODM signing process | Who signs, with which key, under what approval, how a rogue ODM build is detected | CVTE, Malata, ICON |
| G7 | STOP-SHIP Fuse map | Read back from an MP-process unit: only SBC set. DAA, JTAG-disable, PTSB unblown unless separately approved | CVTE, ICON |
| G8 | STOP-SHIP Host-side only | Written CVTE and MediaTek confirmation that no runtime, bootloader or TEE path can program SBC, DAA, JTAG or PTSB | CVTE, MediaTek |
| G9 | STOP-SHIP Userspace write attempt | On a non-fused sacrificial unit, every attempt (factory app, init service, adb, privileged app, fastboot, recovery) fails; fuse state unchanged | Test lead |
| G10 | STOP-SHIP Build audit | No efuse images, write scripts, DA binaries, private keys or factory-test fuse check in the shipping user build | CVTE, audited by ICON |
| G11 | STOP-SHIP DA authentication posture | Signed decision on the intended shipping state of the download path (R17). Under no circumstances is the DAA fuse blown in the same pass as SBC | ICON |
| E1 | STOP-SHIP OTA partition scope | Written CVTE confirmation that preloader, boot0, DA, TEE and SCP/DSP are never in an OTA payload, and the release pipeline enforces the exclusion | CVTE |
| E5 | STOP-SHIP BROM recovery | J26080143-0A00076 and one freshly bricked fused unit recover via forced download and boot a signed build | Test lead, CVTE |
| C, D | STOP-SHIP Zero unrecoverable | Groups C and D complete on fused units including the 200-cycle soak with zero unrecoverable units | Test lead |
| M3–M8 | GATE Configuration | Merge mechanism identified; verity error mode behavioural (M5); slot metadata survives interruption; factory reset refused during merge | Test lead |
| N1, N2, N10 | GATE Prerequisites | Boot-control HAL and snapshot suites conform; fused userdebug build signed with release keys is available so fused-vs-open comparison is executable | CVTE, test lead |
| N3 | STOP-SHIP Attestation | Key attestation on a fused, locked, release-signed unit reports verified and locked against the burned hash | Test lead |
| N11 | STOP-SHIP GSI window | Written confirmation nobody downstream relies on generic-system-image evidence, which ends permanently at fusing | ICON |
| **A0 (new)** | Baseline | On an open 0909 unit, apply wrong-key `vbmeta` and wrong-key OTA; record whether it boots, warns or refuses. Establishes how much behaviour changes at fusing | Test lead |

### Tier 1. CVTE production-line authorization

| ID | Gate | Pass criterion |
|---|---|---|
| L1 | Ten open sacrificial units through the SOP as written; per-serial console trace, chip ID, random ID, DA authentication state archived | All reach completion message |
| L2 GATE | Interrupt fuse write at the 12 V step and mid-transfer, five units each | Each unit is unfused-and-rerunnable or fused-and-flashable; none unfused-but-passed, none partial |
| L3 GATE | Attempt to flash production firmware to a unit whose fuse write failed or never ran | Station refuses and quarantines; ordering enforced by tooling |
| L4 GATE | DA authentication state recorded on every unit; shipping posture decision on file | Matches G11 |
| L5 GATE | Fuse image is the ICON-approved artefact, hash-matched to the G4 key; authoritative build label for fuse image and firmware resolved in writing | Hash match per serial |
| L6 | Re-run fuse write on an already-fused unit | Idempotent or cleanly refused; never a changed hash |
| L7 | Station pinned: flashing tool version, DA, USB drivers, image package | Versions frozen and change-controlled |
| L8 | Time-and-motion including driver-install fallback | Cycle time known; no line pressure toward shortcuts |
| I1 | ICON witnesses a live scripted run | No manual key entry; step cannot be skipped |
| I2 | Advance an unfused unit through factory test | Hard stop |
| I3 | Per-serial fuse write and read-back exported | Auditable by ICON |
| I4 | Power loss or cable pull at the station mid-write | Detected by read-back; quarantined |
| I5 | Yield and scrap over a 500-unit run | Scrap rate accepted in writing before MP release |
| H1 GATE | Depot re-flash of a fused unit with signed DA and signed build at CVTE and at the US service site, using a **full-image** profile and not only the boot-chain profile (R19) | Succeeds at both; time and cost recorded |
| H2–H5 | Recovery/fastbootd reachable and sideload works; factory reset from corrupt userdata recovers; signed-DA custody documented; field-service decision tree validated on real failed units | All pass |

### Tier 2. Malata production-line authorization

Malata has no fuse-station history on this program. Tier 2 is a transfer, not a re-derivation.

| Requirement | Pass criterion |
|---|---|
| Transfer package from CVTE | Same fuse image (hash verified by ICON), same pinned tool, DA, driver and package versions (L7), same scripted station and interlock, same factory-test gate |
| No key material transferred outside controlled channels | Signed DA and any signing artefacts delivered per H4; nothing via project tools or email |
| First-article read-back | Ten Malata fused units: A1, A6, G4, G7 read-back verified by ICON; hash identical to CVTE units |
| Witnessed line run | I1–I5 and L1–L3, L5, L6 repeated on the Malata line with ICON present or on recorded video with logs |
| Depot | H1 at Malata's service path |
| Decision | Malata fusing authorized only after CVTE has shipped at least one fused lot with no fuse-attributable field return |

### Tier 3. Authorization to push production OTA to fused units

| Requirement | Pass criterion |
|---|---|
| J1 | Pipeline gate verifies every published package against the fused key chain; unsigned or wrong-key packages cannot publish |
| J2 | Rings at 0.1, 1, 10, 100 percent with automatic halt on boot-success regression; demonstrated on a deliberately bad build in a lab ring |
| J3 | Kill switch stops downloads within the defined interval during a live rollout |
| J4 | Telemetry reports slot, fingerprint, verified-boot state, **fuse state** and update outcome per serial; bad rollout visible before the next ring |
| J5 | Same build published twice with differing hashes is blocked |
| K1–K3 | 30-day fused pilot, at least two full OTA transitions, two random depot recoveries, zero unrecoverable |
| F1 on 0919 | Signed older build flashes and boots on a fused unit: the fleet escape hatch is proven on the shipping build |

Until Tier 3 passes, fused units in the field receive no OTA. This is the control that makes Option B tolerable and it costs nothing under Option A.

---

## 5. Consolidated test plan

Test content is Plan B groups A–N with Plan A's glitch matrix mapped in. Only additions and changes to Plan B r0.4 are listed here; unchanged cases are referenced by ID.

### 5.1 Sample matrix

| Group | Qty | Configuration | Use |
|---|---|---|---|
| OPEN-1..5 | 5 | Not fused, 0909 then 0919 | Control; every destructive case rehearsed here first; 1,000-iteration automated glitch matrix; A0 baseline |
| CLOSED-1..2 | 2 | Fused | Sacrificial: preloader and boot-chain negative tests (E2–E4, E6). Assume total loss |
| CLOSED-3..4 | 2 | Fused | C group ×5, D soak, M5 verity, depot rehearsal |
| CLOSED-5 | 1 | Fused | Golden reference; never negative-tested; fuse read-back and performance baseline |
| CLOSED-6..7 (added) | 2 | Fused | Spares for the 200-cycle soak and for the fresh brick required by E5 |
| BRICK-1 | 1 | Fused, unbootable | J26080143-0A00076, E5 acceptance vehicle |
| USERDEBUG-F (added) | 1 | Fused, userdebug signed with release keys | Required by N10 for VTS on a fused unit; is itself a key-custody request |
| PILOT | 25–50 | Fused, MP-intent line process | Group K soak at ICON-controlled sites |

### 5.2 Additions and changes to Plan B r0.4

| ID | Change | Reason |
|---|---|---|
| A0 (new) | Open-config signature behaviour baseline (wrong-key `vbmeta`, wrong-key OTA, stripped signature) on 0909 | Establishes the true delta between open and closed; tests the brief's premise |
| A7 (new) | OTA client behaviour with the wall clock at build time (no RTC): TLS validation of the OTA endpoint, package timestamp checks, before NTP sync | Source D shows every cold boot starts at build time. An OTA that fails or a certificate rejected as not-yet-valid is a field-visible failure mode independent of fusing but exposed by any OTA plan |
| N6 emphasis | Health HAL on a battery-less unit reports a sane state; `update_engine` minimum-battery policy verified | Tool reports `battery_voltage 0`; an update client that refuses to start, or starts when it should not, is plausible |
| D8 | Brown-out via programmable DC source sweep, not only clean cut | A sagging console supply is more likely than an instant drop |
| E5 | Add: document the exact button, hold timing, tool version, and whether it is reachable without opening the enclosure | Defines hard versus soft brick for this product (Section 4.3 of Plan B) |
| F1 | Must be repeated on signed 0919, not only 0909 | Fleet escape hatch must be proven on the shipping artefact |
| J4 | Add fuse state to fleet telemetry | Mixed fleet under Option A; OTA freeze under Option B; depot routing |
| K1 | Pilot sites are ICON-controlled (offices, employee homes, test gyms), not customers | Zero fused customer units until soak completes |
| Glitch matrix | PWR-01..04 and USR-01 run at 1,000 iterations on open units; 200 randomised on fused; AVB-01 rescoped to F2 | Reconciles Source A and B criteria; anti-rollback unavailable |
| Re-test set | G1, G2, G4, N3, B1, B2, C3, C5, D2, D4, F1, M5 repeated on final signed 0919 | Any re-sign invalidates hash-dependent results |

### 5.3 Instrumentation and records

Per Plan B 4.2, plus: per-serial fuse state in the backend, programmable DC source logs correlated to `update_engine` phase, and the exact SP Flash Tool, DA and driver versions frozen at L7 recorded in every test artefact.

---

## 6. Production plan

### 6.1 Line sequence (both ODMs)

1. Board in BROM/preloader download mode over mini-USB, 12 V applied only after `write-efuse` is issued (SOP order).
2. Station script writes `efuse_iFitG520.img`; `CMD:WRITE-EFUSE command execute successed` logged against serial.
3. Read-back: `sbc_en` set, `sbc_pub_key_hash` equals the ICON-approved hash; DAA, JTAG, PTSB unblown. Any other outcome quarantines the unit; the station will not proceed.
4. Signed production firmware flashed; `Download Ok` logged against serial.
5. Factory-test application hard-gates on fuse status. A unit with the wrong state cannot progress.
6. Per-serial record exported to ICON: serial, station, fuse read-back, fingerprint, slot suffix, factory-test pass.
7. Under Option A, fused and unfused units carry distinguishable labelling and the backend records fuse state per serial. Depot and RMA route by that field.

### 6.2 Depot and RMA

- Two proven sites before the first fused lot (H1): one at the ODM, one in the US.
- Full-image recovery profile validated, not only the boot-chain profile in the SOP (R19).
- Signed DA custody documented and distributed only through controlled channels (H4).
- Spare-board inventory must be fuse-state matched to the units it repairs.
- Field-service decision tree published: symptom, recovery action, escalation (H5).

### 6.3 Financial framing

Fusing does not change the OTA failure probability. It changes two cost terms:

- **Per-incident recovery cost rises**: depot signed flash replaces a generic flash, and a preloader-mode brick that does not enumerate requires the E5 procedure or a board swap.
- **Process-error cost becomes unbounded per batch**: a wrong hash or a compromised key on the fused population is a full replacement with no software remedy.

The exposure that staged rollout bounds is the same for both configurations: worst case before automatic halt is the ring size times the unit replacement cost. The exposure that only gates bound is the fused lot size times unit cost. That is the argument for Option A on lot 1: it caps the second term at the pilot size while the first term is being measured.

Inputs needed to put numbers on this are listed in Section 7.

---

## 7. Background assumptions that are missing or unstated

These are needed either to run the plan or to make the Option A / B decision. None of them is answered in the three sources.

**Commercial and compliance**

1. Fleet size for lot 1 and for the program, unit replacement cost, RMA logistics cost and warranty terms. Without these the financial framing in 6.3 has no numbers.
2. Whether Cesium ships into the EU and whether the EN 18031 assessment accepts a software root of trust. Xenon passed NIST 8259 with software RoT. If the compliance body requires hardware RoT, Option A's "permanently open lot 1" has a compliance cost, not only a security-posture cost.
3. The threat model the fuse is meant to close. For a kiosk fitness console, physical-access OS replacement, content and DRM, and brand protection are different threats. Remote threats are already covered by signed OTA on the open configuration. This decides whether shipping any unit unfused is acceptable.
4. Who signs the fuse authorization for CVTE and for Malata, and whether the MP line can start unfused and switch to fused mid-lot. If it can, the "three weeks" deadline applies to the line start and not to the fusing decision, which relieves the schedule considerably.

**Keys and artefacts**

5. Whether the private keys posted to Basecamp are the production keys, whether ICON has an HSM or escrow available now, and whether the ODMs will accept a key rotation and `efuse_iFitG520.img` regeneration inside the schedule.
6. Whether a fused userdebug build signed with release keys will be produced (N10). Without it, VTS on a fused unit and the fused-versus-open comparison cannot run.
7. Whether Cesium licenses Google Mobile Services. This determines whether GTS applies and which suites are available (Plan B Group N).
8. Which build label is authoritative for the fuse image and firmware (VKC1_20260727 versus 20260729 ambiguity) and who signs off the pairing (L5).

**Platform behaviour**

9. Whether the OTA payload ever includes preloader, LK, TEE or SCP firmware (E1). This is the single written confirmation with the highest value in the plan.
10. Why `preloader_b` did not take over on the bricked first article, and the exact boot0 failover logic on a fused MT8371.
11. Whether the forced-download button is reachable on the assembled console without disassembly. This defines hard versus soft brick for the product.
12. Whether the console power supply has any hold-up capacitance and whether the user can remove power at any instant (mains switch, unplug). Determines how realistic D8 brown-out is relative to a clean cut.
13. How the OTA client behaves with the wall clock set to build time on every cold boot (no RTC) before NTP sync, and whether `update_engine` enforces a minimum battery level on a unit that reports zero battery voltage.
14. The agreed compensating control against a signed-but-old image being pushed as an OTA, given that anti-rollback cannot be enabled on this part.
15. The intended shipping posture for download-agent authentication (R17). An unauthenticated download path is what makes depot recovery cheap and what lets anyone with USB access re-flash or read partitions. This must be a recorded decision, and it interacts with the EN 18031 physical-access assessment.

**Operations**

16. Whether a US service site exists today with Windows hosts, the pinned SP Flash Tool version and a custody path for the signed DA.
17. How the backend, depot and RMA will handle a mixed fused and unfused fleet if Option A is chosen, and how an OTA freeze by fuse state would be implemented if Option B is chosen.
18. Malata's readiness: the 100-unit trial on 30 July was a CVTE run. Malata has not fused a unit on this program.

---

## 8. Open questions to CVTE, Malata and MediaTek

Plan B section 7 questions 1–16 are carried forward unchanged and should be sent as one letter on Day 1, quoting both chip designators (MT8371 / Genio 520 and MT8189 as the tool reports it). Add:

17. Can the MP line run unfused and switch to fused mid-lot without re-qualification, and what changes on the station when it does?
18. Will CVTE and Malata accept a key rotation and a regenerated fuse image before their first fused lot, and what is the lead time?
19. What is the per-unit depot cost and turnaround for a fused unit at each ODM's service path, and does either require an additional auth file or certificate for secure download?

---

## 9. Traceability

| This document | Source |
|---|---|
| Section 0 item 1, Section 1.1 conflicts 4 and 5 | Feasibility study: programming modes table, risk analysis 1–4, recommendations 1 and 3 |
| Section 1.1 conflicts 1, 2, 3, 6; glitch matrix IDs; kernel and build flag table; CTS/VTS modules | A/B Resiliency Test Plan v2.0 sections 3–6 |
| Program history, risk register R1–R19, groups A–N, sample matrix, exit criteria, open questions 1–16 | Closed-Config Brick-Resistance Test Plan r0.4 sections 2–7 |
| No RTC, rollback resistance unavailable | Cesium 0831 Boot Log Analysis, items 1 and 6 |

*Prepared for internal ICON review. Contains no verbatim reproduction of vendor documentation. Not yet issued to CVTE or Malata.*
