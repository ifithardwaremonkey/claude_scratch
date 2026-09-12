# Cesium Hardware Root-of-Trust Authorization Plan

**Consolidated test, production and decision plan for burning the SBC eFuse on Cesium AOSP 15 tablets at CVTE, then Malata**

| | |
|---|---|
| Product | Cesium tablet (iFitG520), MediaTek MT8371 / Genio 520 (tool reports MT8189), AOSP 15, A/B seamless update, battery-less console |
| Current build | VKC1_20260909 (software root of trust, fingerprint `:user/dev-keys`) |
| MP-intent build | VKC1_20260919 (expected 19 Sep 2026) |
| Mass production | ~3 Oct 2026 (three weeks from this revision) |
| Revision | 1.2 draft, 12 September 2026 (1.0 and 1.1 issued earlier the same day) |
| Owner | Allen Middleton (Tablet Engineer, ICON Health & Fitness) |
| Supersedes | Cesium Closed-Config Field Brick-Resistance Test Plan r0.4 (test content carried forward with its case IDs); Android 15 Virtual A/B & AVB 2.0 Resiliency Test Plan v2.0 (glitch matrix carried forward with errata); Remote eFuse MT8371 Feasibility Study (conclusion adopted); MediaTek Security 2.1 Software Root of Trust Report (three-way comparison adopted, probability figures reinterpreted) |

**Changes in revision 1.2.** Source F, the MediaTek MT8391/MT8371 Android 15 Secure Boot Developer Guide V1.1, ingested and used to verify Source E. Flag names, the CERT1/CERT2 chain and the DAA flow in Source E are confirmed verbatim. Two facts from the guide change the plan. First, BROM fallback to the second preloader copy is documented **for NAND only**; Cesium boots from eMMC, which is the likely reason `preloader_b` did not take over on the bricked first article, so E2 is rescoped from a pass/fail to a characterisation and R1's mitigation rests on E1 and E5 alone. Second, the eFuse configuration file carries a `Disable_Rom_Cmd` option that MediaTek "highly recommends" and that permanently disables BROM command mode; if it is set in `efuse_iFitG520.img`, forced download (E5) is impossible on every fused unit, which would also explain the no-enumeration brick. G7 now reads back that bit explicitly and a new Day 1 action inspects the fuse XML.

**Changes in revision 1.1.** Source E (software root of trust report) ingested. Section 2 rewritten as a three-way comparison (unsigned, software RoT, hardware RoT). The corrupt-preloader brick mode is now classified as **new with fusing**, because under software RoT the BootROM does not verify the preloader and still offers download mode. Case A0 is sharpened to read the preloader security flag and `sboot_state`. A key-freeze rule is added: any key rotation must complete before the first unit ships under either option, because the preloader is outside OTA scope. Three new source conflicts (7 to 9) and two new missing assumptions (19, 20).

---

## 0. Decision summary

**1. Field fusing is ruled out.** The feasibility study is adopted in full: eFuse writes on MT8371 are only possible from BROM/DA mode or a preloader self-blow, and self-blow via OTA on a battery-less unit with no hold-up supply is a brick-rate machine. Every Cesium unit is therefore either fused on the production line or never fused. There is no "ship open, close later" path. That makes the per-unit fuse decision permanent in both directions.

**2. Hardware root of trust does not raise the probability that a bad OTA is applied. It changes what can be recovered afterwards, and it adds exactly one new brick mode.** The question in the brief is answered in Section 2. On the A/B path (everything `update_engine` writes) a corrupt or truncated payload is rejected before any write regardless of fuse state, and slot fallback is fuse-independent. If the 0909 preloader is built with `ATTR_SBOOT_ENABLE` (to be confirmed by A0), the software root of trust already enforces LK, TEE and AVB signatures, so a mis-signed image already halts boot today. The fuse adds exposure in four places, none of which a 30-day soak measures well:

- **The preloader itself becomes verified.** Under software RoT the BootROM does not check the preloader; a corrupt preloader drops to BROM download mode and is re-flashed with no authorization. Under hardware RoT the BootROM halts on a hash mismatch, which is what the bricked first article shows (no USB enumeration). This is the one failure mode that is genuinely new with fusing, and E1 plus E5 exist to close it.
- **Key and fuse-image mistakes** become permanent and batch-scale (wrong hash, dev key, leaked key).
- **Every recovery path narrows** to signed artefacts: signed DA, re-signed firmware, older rescue images rejected. Leaving DAA unblown (G7, G11) keeps this narrower than Source E's worst case.
- **Keys are frozen for the life of the fleet.** Source E's software-RoT brick mode is a key rotation that updates LK but not the preloader. Since the preloader is excluded from OTA (E1), rotation is impossible after shipment in **both** configurations. Any rotation must happen before lot 1 ships.

Those four are controlled by gates, custody and rehearsal before the first unit is fused, not by field time. This is good news for the schedule: the risks that actually differ between open and closed are front-loadable.

**3. The full r0.4 gate set cannot complete in three weeks.** The 30-day fused pilot soak (Group K) alone overruns MP. Two authorization options are defined in Section 3. The recommended posture:

- **Plan to Option A**: MP lot 1 ships on software root of trust (the configuration every fielded Xenon runs and that passed NIST 8259), except a 25–50 unit fused pilot ring built by the MP-intent line process. CVTE fusing of full production is authorized at the first lot after the pilot soak completes and the Tier 0 and Tier 1 gates in Section 4 pass. Malata follows after Tier 2.
- **Allow Option B** (fuse all of MP lot 1) only by an explicit go decision on Day 18 if every Tier 0 STOP-SHIP gate has passed, **and** with the compensating control that no production OTA is pushed to fused units until Tier 3 (rollout controls plus pilot soak) is complete. Since field bricks are OTA-induced, an OTA freeze on the fused population removes the untested exposure during the soak window.

**4. Four items must start today** because they have the longest lead time and each one alone blocks fusing:

1. Revive bricked unit J26080143-0A00076 via forced BROM download (E5). If this cannot be shown, closed configuration is not accepted at all.
2. Resolve the `dev-keys` fingerprint versus ICON certificates (G1, G2) on 0909 now and again on 0919.
3. Key custody (G3, G5): AVB private keys (`img_prvk.pem`, `da_prvk.pem`, `root_prvk.pem`) were posted as Basecamp attachments to a 19-person distribution including ODM client accounts. Keys distributed that way cannot be considered in custody. Decide within 48 hours whether to rotate to an ICON-held key and regenerate `efuse_iFitG520.img` before any MP unit is fused. Rotation costs roughly 3 to 5 days of re-signing and re-test; not rotating means the fleet permanently trusts a key at least 19 people have handled. Whatever is decided, rotation must complete before the first unit ships under either option, because the preloader carries the root key (software RoT) or is verified against it (hardware RoT) and is outside OTA scope.
4. Written CVTE confirmation of exactly which partitions the OTA payload writes and that preloader/boot0 are never in scope (E1).
5. Open the eFuse configuration (`security/efuse/input.xml`) and the generated `efuse_iFitG520.img` and read the state of `Disable_Rom_Cmd`, `jtag_en` and `debug_en`. MediaTek's guide recommends `Disable_Rom_Cmd="true"` for high security; set, it permanently removes BROM command mode and therefore every USB recovery path including E5. If it is true in the image that was burned on the first articles and the 100-unit trial, those units cannot be recovered by any documented procedure, and the fuse image must be regenerated before any MP unit is fused. This is the leading hypothesis for why the bricked unit does not enumerate.

---

## 1. Sources and reconciliation

| Source | What it contributes | Trust and scope |
|---|---|---|
| **A. Android 15 Virtual A/B & AVB 2.0 Resiliency Test Plan v2.0** (MediaTek app-note derived) | Glitch matrix PWR-01..04, USR-01, AVB-01; build and kernel configuration table; CTS/VTS module list; 1,000-iteration open-config pass criterion. | Trusted for generic AOSP 15 mechanism. Written for open configuration. Two premises do not hold on this part (below). |
| **B. Cesium Closed-Config Field Brick-Resistance Test Plan r0.4** (two years of Basecamp record with CVTE and Malata) | Program history, 19-item risk register, groups A–N with STOP-SHIP and GATE badges, sample matrix, exit criteria, 16 open questions for the ODMs and MediaTek. | Trusted and platform-specific. Not yet issued to the ODMs. This document carries its case IDs forward unchanged so the two can be read side by side. |
| **C. Remote eFuse Programming MT8371 Feasibility Study** | Fuse programming modes; self-blow pipeline; field failure modes (3.7 V threshold, hash mismatch, magic-key mismatch, unreadable failure log). Verdict: not feasible for field deployment. | Trusted. Its conclusion is adopted; its "enable anti-rollback for field counters" recommendation is **not** adopted (see conflict 1). |
| **D. Cesium 0831 Boot Log Analysis** (this repository) | Corroborating evidence: `keystore2 ROLLBACK_RESISTANCE_UNAVAILABLE`; no reliable RTC, wall clock set to build time each cold boot. | Supporting only. |
| **E. MediaTek Security 2.1 Software Root of Trust Report** (MediaTek Secure Boot Developer Guide V1.1, Secure 2.1 Configuration SOP, eFuse Writer Guide) | Definition of software RoT: preloader built with `MTK_SEC_BOOT = ATTR_SBOOT_ENABLE` enforces CERT1/CERT2 verification of LK, TEE and AVB descriptors with the root public key compiled into the preloader (`sw_root_pubk.h`); BootROM does not verify the preloader while `SBC_EN = 0`. Contrast flag `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP` enforces only once fused. Three-way comparison of unsigned, software RoT and hardware RoT; recovery paths for each; recommendation of software RoT for 100 to 500 unit field trials. | Trusted for mechanism and configuration flags. Its bricking-probability percentages are conditional estimates without a cited measurement and are reinterpreted in conflict 7. The document is machine-generated from the cited MediaTek guides. Checked against Source F in revision 1.2: flag names, the CERT1/CERT2 chain, `oemkey.h` placement, key file names and the DAA flow are accurate. Its `sboot_state = 0x1` detail and the "anti-rollback software version check" step in the software-RoT flow do not appear in Source F and remain unverified. |
| **F. MediaTek MT8391 MT8371 Android 15 Security Secure Boot Developer Guide V1.1** (MediaTek Confidential, watermarked to ICON, retrieved 30 Jul 2026) | Authoritative BROM, preloader, LK and TEE verification flow; `MTK_SEC_BOOT` / `MTK_SEC_USBDL` flag semantics (5.2.1); key generation and `oemkey.h` embedding into preloader, DA and LK (5.1); DAA AuthFile flow (4); eFuse `input.xml` options `Enable_SBC`, `Enable_DAA`, `Disable_Rom_Cmd` (7); preloader second-copy fallback stated for NAND (3.1 note). | Primary vendor source. Used to verify Source E and to correct two premises in Source B (see conflicts 10 and 11). Confidential: cite section numbers to the ODMs, do not reproduce. |

### 1.1 Conflicts between trusted sources and how this plan resolves them

| # | Conflict | Resolution in this plan |
|---|---|---|
| 1 | **Anti-rollback.** Source A says `MTK_SECURITY_ANTI_ROLLBACK = yes` is supported and required; Source C recommends relying on it for field version management. Source B records MediaTek stating in Mar 2024 that it cannot be enabled on this project and CVTE reconfirming in Aug 2026 that it remains disabled on 8371. Source D shows the KeyMint side reports rollback resistance unavailable. | Treat anti-rollback as **disabled and to stay disabled for MP** (Group F). A signed known-good older build is then the fleet-wide escape hatch (F1), which matters more on a fused fleet than downgrade protection does. Source A case AVB-01 is rescoped to signature-based rejection only (F2); its "ARB counter check" pass criterion cannot be met. Obtain one written MediaTek statement to close the disagreement (open question 6). Agree a compensating control for signed-but-old pushes (open question 16). |
| 2 | **Virtual A/B.** Source A assumes copy-on-write snapshots and userspace merge (`snapuserd`, `dm-user`) throughout; roughly a third of its cases depend on this. Source B confirms A/B from the paired slot table (M1) but not the snapshot layer. | M2 and M3 run on Day 1. If virtual A/B is not enabled, PWR-02, PWR-04 and USR-01 are re-scoped to plain A/B slot writes rather than reported as failures. |
| 3 | **Verity error handling.** Source A corrects `CONFIG_DM_VERITY_AVB` to `y` for managed restart. Source B case M4 asks to confirm the verity-AVB immediate-invalidate option is **not** selected. | Do not edit kernel configuration on the basis of either document. The binding evidence is behavioural: M5 induces a single-block verity error on a sacrificial fused unit and must produce a controlled restart and slot fallback, never a loop or a brick. Record the actual defconfig and LK hashtree error mode alongside the result. |
| 4 | **Battery threshold.** Source C's 3.7 V cut-off applies to self-blow on battery. Cesium has no battery. | Irrelevant to field OTA (no self-blow ships). Relevant to the factory station: the burn depends entirely on the 12 V bench supply and the manual power sequence, so station power conditioning and interruption behaviour are tested (L2, I4). |
| 5 | **Non-A/B boot chain.** Source A treats non-A/B as deprecated and out of scope. Source B records that the one demonstrated brick on this program was a non-A/B boot stage (corrupt `preloader_a`, intact `preloader_b` did not fail over, no USB enumeration). | Group E is the highest-value group in this plan. E5 is the single stop-ship. |
| 6 | **Iteration counts.** Source A requires 1,000 consecutive passing iterations. Source B requires zero unrecoverable units over a 200-cycle randomised soak. | 1,000 iterations on **open** units (cheap, automated, no scrap). 200 randomised interruptions on **fused** units, bounded by sacrificial hardware, with zero unrecoverable as the binding criterion. |
| 7 | **Bricking probability figures.** Source E estimates OTA bricking at 5 to 12 percent for software RoT and 25 to 40 percent for hardware RoT "if mismatched". Read as per-OTA rates these would make any OTA plan unshippable and would contradict Sources A and B. | Read them as **P(brick given a key or hash mismatch has already been shipped)**, which is what the wording says. The mismatch event is exactly what G1 to G6 and J1 prevent from ever leaving the build pipeline. The figures therefore quantify the cost of a gate failure, not the field rate of a gated fleet. They are not used as inputs to Section 6.3 until a measured source is found. |
| 8 | **DAA state.** Source E's hardware-RoT recovery case assumes both `SBC_EN` and `DAA_EN` are blown, so BROM refuses every unsigned Download Agent and recovery needs a signed `da.auth` or a MediaTek RMA certificate. Source B's plan blows SBC only and the SOP trace shows DA authentication disabled. | Cesium recovery is less constrained than Source E's worst case **as long as G7 and G11 hold** (only SBC set, DAA decision recorded, never blown in the same pass). Source E is the description of what Cesium becomes if DAA is ever blown without a demonstrated recovery path, which is why G11 is STOP-SHIP. |
| 9 | **What "software root of trust" enforces on 0909.** Source E: enforcement depends on the preloader build flag. `ATTR_SBOOT_ENABLE` verifies LK, TEE and AVB regardless of fuse state; `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP` verifies nothing until fused. Source B records both "mismatches are ignored" (Feb 2024) and "software AVB verifies bootloader/Android binding" (May 2026), which are consistent with different flags at different times. | A0 reads the flag from the 0909 and 0919 preloader configuration and `sboot_state` from the console, then confirms behaviourally with a wrong-key LK. If 0909 is `ONLY_ENABLE_ON_SCHIP`, the open lot 1 under Option A ships with **no** boot-chain signature enforcement and the plan must require `ATTR_SBOOT_ENABLE` for open units (new gate A0-b). If it is `ATTR_SBOOT_ENABLE`, the brief's premise is correct and Section 2 stands as written. **Confirmed against Source F 5.2.1**, which states the SCHIP flags enable secure boot "according to eFuse SBC field" and the plain flags enable it "forcedly without eFuse to verify SW secure boot flow first". |
| 10 | **Preloader A/B failover.** Source B case E2 expects a fused unit with corrupt `preloader_a` to boot from `preloader_b`, and open question 1 asks why it did not. Source F 3.1 note B states BROM fallback to the second preloader copy is supported **if the external storage is NAND flash**. Cesium boots from eMMC. | E2 and E3 are rescoped from pass/fail to characterisation: record whether eMMC boot1 fallback exists on MT8371 at all and obtain MediaTek's written answer. Until then, assume **no preloader redundancy** on this product. R1's mitigation is therefore E1 (preloader never in OTA scope, enforced by pipeline) plus E5 (forced BROM download proven), with no third leg. |
| 11 | **BROM command-mode disable.** Source B's fuse-map gate G7 lists SBC, DAA, JTAG and PTSB. Source F section 7 adds `Disable_Rom_Cmd` (also `brom_magic_cmd_mode_permanent_dis` in the preloader GFH config) and "highly recommends" setting it: BROM "cannot receive any commands to download, disable secure boot check, and so on anymore". Source E's hardware-RoT recovery column assumes DAA only. | If this bit is set, forced download does not exist and E5 cannot pass on any fused unit. G7 now reads it back explicitly and requires it **unset**. Day 1 action 5 inspects `input.xml` and the burned image. The observed no-enumeration brick is consistent with either a BROM halt on hash mismatch (Source E 5.3) or this bit being set; the two are distinguished by whether the forced-download button sequence produces enumeration on a fused, otherwise healthy unit (CLOSED-5). |

---

## 2. Does hardware root of trust increase field brick risk?

The brief's hypothesis: the 0909 build already enforces a software root of trust, so a corrupt signature already risks a non-booting unit, and the hardware root of trust may add no brick risk at all.

With Source E in hand the hypothesis is **correct for the A/B update path and for everything the preloader verifies, provided 0909 is built with `ATTR_SBOOT_ENABLE`. It is incorrect for the preloader itself, for recovery, and for key handling.** The Basecamp record contains both "signature mismatches are ignored" (Feb 2024) and "software AVB verifies bootloader/Android binding" (May 2026). Source E shows these describe two different preloader build flags, so which one 0909 carries must be read on Day 1 (A0), not inferred.

### 2.1 Three configurations (from Source E, applied to Cesium)

| Dimension | Unsigned boot (`ATTR_SBOOT_DISABLE`) | Software RoT (`ATTR_SBOOT_ENABLE`, `SBC_EN = 0`) | Hardware RoT (`ONLY_ENABLE_ON_SCHIP`, `SBC_EN = 1`) |
|---|---|---|---|
| Root key anchor | None | Public key compiled into preloader (`sw_root_pubk.h`) | Hash of public key in OTP (`SBC_PUBK_HASH`) |
| Who verifies the preloader | Nobody | **Nobody.** BootROM loads it unchecked (Source F 3.1: secure boot flow "can be enabled by blowing SBC_EN") | BootROM, in silicon: hash of `SBC_PUBK` from eFuse, key from NVM, then RSA over the preloader |
| Preloader redundancy | Second copy tried by BROM on NAND only (Source F 3.1 note B) | Same | Same. Cesium is eMMC: assume none until MediaTek confirms otherwise |
| Who verifies LK, TEE, AVB descriptors | Nobody | Preloader software, enforcing (`sboot_state = 0x1`) | Preloader, whose own integrity is now guaranteed |
| Behaviour on LK/TEE signature mismatch | Boots | Halts at preloader assertion | Halts at preloader assertion |
| Behaviour on preloader corruption or mismatch | BROM download mode | BROM download mode; re-flash preloader, no auth file | **BROM halts.** No enumeration observed on Cesium. Forced-download entry (E5) is the only path |
| USB flashing protection | Any DA | Any DA unless `ATTR_SUSBDL_ENABLE`; SOP trace shows DA auth disabled on Cesium | Signed DA if DAA blown; Cesium leaves DAA unblown (G7) |
| Key rotation | Re-flash | Re-flash preloader (not possible by OTA on Cesium, E1) | Impossible |
| Reversibility | Full | Full, by re-flash | None |
| Source E's recommendation | Bring-up only | 100 to 500 unit field trials | Production shipping mode |

### 2.2 Failure modes, open versus closed

| Failure mode | Software RoT (open, if `ATTR_SBOOT_ENABLE`) | Hardware RoT (SBC fused) | Marginal risk from fusing |
|---|---|---|---|
| Corrupt, truncated or bit-flipped OTA payload (C1, C2) | Rejected by `update_engine` hash check before any write | Same | **None.** Fuse is not consulted. |
| Delta against wrong source build (C12) | Rejected before write | Same | **None.** |
| Package signed with wrong or test key (C3, C4) | Slot fails preloader/AVB check at boot; falls back to previous slot | Same | **None on the mechanism, if fallback works on a fused unit** (C5–C10). If 0909 is `ONLY_ENABLE_ON_SCHIP`, the open unit boots foreign code instead and security, not brick risk, is what changes. |
| Corrupt `vbmeta`, `boot.img`, hash tree in the inactive slot (C5–C7) | Fallback to good slot | Fallback to good slot | **None, conditional on C5–C10 and M5.** |
| Power loss during download, write, post-install, slot switch, first boot (D1–D9, PWR-01..04) | A/B protects; boots good slot | Same | **None on the A/B mechanism.** Slot-metadata behaviour (M6–M8) must be verified once; it is fuse-independent. |
| Panic before boot-success marker (C8) | Auto revert | Auto revert | **None.** |
| Corrupt non-A/B stage: preloader / boot0 (E2–E4) | Soft brick: BROM download mode, re-flash with any DA and any preloader. No second-copy fallback on eMMC (Source F) | **Hard brick unless forced download works.** BootROM halts on hash mismatch; observed on J26080143-0A00076. If `Disable_Rom_Cmd` is set, no download mode exists at all | **High until E5 passes. This is the one new brick mode.** Mitigation is contractual: OTA never writes preloader/boot0 (E1), and the fuse map leaves BROM command mode enabled (G7). |
| Key rotation that updates LK but not preloader (Source E 5.2) | Halts at preloader; recoverable by USB re-flash of preloader | Halts; recoverable only with signed artefacts; hash cannot change | **Both fatal in the field** because the preloader is outside OTA scope. Rule: keys are frozen before lot 1 ships. |
| Wrong key hash, dev key, or leaked private key burned (R2, R3) | N/A: re-flash preloader with new key | Permanent, fleet-wide | **Critical and new.** Only gates prevent it (G1–G6). |
| Depot re-flash of a failed unit (H1) | Any image, any DA | Signed DA and re-signed image; earlier rescue images rejected | **Medium: cost and process, not probability.** Less severe than Source E's case because DAA stays unblown. |
| Storage bit rot in active slot (C11) | Verity detects (AVB enforced by preloader) | Same | **None if M5 passes.** |
| Factory fuse write itself (L1–L8, I1–I5) | N/A | Manual, ordered, irreversible | **Medium, line-side only.** 100-unit CVTE trial with zero failures is encouraging, not sufficient. Malata has no fuse experience at all. |

**Conclusion.** If 0909 enforces software RoT, fusing changes nothing about how an OTA is verified or how a slot falls back. It adds one brick mode (preloader), removes every unsigned recovery route, and makes key errors permanent. The financial exposure therefore moves from "unforeseen OTA bug" (bounded by staged rollout regardless of fuse state) to "preloader integrity, key custody, and recovery procedure" (bounded only by E1, E5 and the Group G gates). Source E's own recommendation, software RoT for field trials of 100 to 500 units and hardware RoT for shipping, is the same posture as Option A.

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
| G7 | STOP-SHIP Fuse map | Read back from an MP-process unit and from the burned first articles: only SBC set. DAA, JTAG-disable, PTSB **and `Disable_Rom_Cmd` / `brom_magic_cmd_mode_permanent_dis`** unblown. Cross-check against `input.xml` and the GFH config used to build `efuse_iFitG520.img`. A set `Disable_Rom_Cmd` bit removes every USB recovery path and blocks fusing outright | CVTE, ICON |
| E2 (rescoped) | Characterisation | Corrupt `preloader_a` on a fused unit and on an open unit. Record whether BROM tries the second copy on eMMC. Source F documents second-copy fallback for NAND only, so a fail here is information, not a defect | Test lead, MediaTek written answer |
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
| **A0 (new)** | Baseline | Read `MTK_SEC_BOOT` and `MTK_SEC_USBDL` from the 0909 and 0919 preloader project configuration and `sboot_state` from the preloader console. Then on an open 0909 unit flash a wrong-key LK and a wrong-key `vbmeta`; record halt, warning or boot. Result settles Section 1.1 conflict 9 | CVTE (config), test lead (behaviour) |
| **A0-b (new)** | STOP-SHIP for open units under Option A | Any unit shipped unfused must carry a preloader built with `ATTR_SBOOT_ENABLE`, verified by A0 on the shipping build. An unfused unit built with `ONLY_ENABLE_ON_SCHIP` has no boot-chain signature enforcement at all | CVTE, ICON |
| **K0 (new)** | STOP-SHIP Key freeze | Root, image and DA keys are frozen before the first unit ships under either option. Rotation after shipment requires a preloader update, which E1 excludes from OTA. Recorded as a signed decision alongside G3 | ICON |

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
| A0 (new) | Read preloader security flags and `sboot_state`; wrong-key LK and wrong-key `vbmeta` on an open 0909 unit | Source E shows enforcement depends on the build flag. Settles whether the brief's premise holds and whether open lot 1 units under Option A enforce anything |
| A0-b, K0 (new) | Open units must be `ATTR_SBOOT_ENABLE`; keys frozen before first shipment | Source E section 5.2 brick mode (LK re-keyed without preloader) is unrecoverable by OTA on Cesium in either configuration |
| E2, E3 | Rescoped to characterisation. Add the open-unit control: corrupt `preloader_a` on an OPEN unit and record whether BROM download mode enumerates and whether the second copy is tried | Source F documents second-copy fallback for NAND only; Cesium is eMMC. Source E predicts a soft brick on open units and a halt on fused units. The open case proves the preloader mode is new with fusing rather than pre-existing |
| E5 | Add: run the forced-download button sequence first on CLOSED-5 (healthy fused unit) and confirm BROM enumerates before trying it on BRICK-1 | Separates "the bricked unit is unreachable" from "BROM command mode is fused off on every unit" (conflict 11) |
| G7 | Add `Disable_Rom_Cmd`, `jtag_en`, `debug_en` to the read-back and to the `input.xml` audit | Source F section 7 and 5.4 |
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
19. Which preloader security flag the 0909 and 0919 builds carry (`ATTR_SBOOT_ENABLE` versus `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP`), and whether `MTK_SEC_USBDL` is set. Everything the brief assumes about "software root of trust already enforcing signatures" rests on this one makefile line, and the Basecamp record is consistent with either answer at different dates.
20. Whether the ICON platform keys that sign the Android OTA (the `dev-keys` question) and the MediaTek boot-chain keys (`root_prvk.pem`, `img_prvk.pem`, `da_prvk.pem`, `epp_prvk.pem`) are managed as one custody problem or two. Source F section 5 and 6 show the root public key is compiled into the preloader, the DA and LK, so a root rotation rebuilds all three; G3 must name a holder for each key, and K0 freezes all of them.
21. What `efuse_iFitG520.img` actually encodes. Source F section 7 lists `Enable_SBC`, `Enable_DAA` and `Disable_Rom_Cmd` as the three `input.xml` switches, and the preloader GFH config carries `brom_magic_cmd_mode_permanent_dis`, `jtag_en` and `debug_en`. No source in this set states the values CVTE used. The plan has been assuming SBC only; that is unverified until the XML and a read-back are on file.
22. Whether BROM on MT8371 with eMMC ever falls back to the second preloader copy. Source F documents the fallback for NAND. If eMMC has none, the product has no preloader redundancy in either configuration and `preloader_b` is inert.

---

## 8. Open questions to CVTE, Malata and MediaTek

Plan B section 7 questions 1–16 are carried forward unchanged and should be sent as one letter on Day 1, quoting both chip designators (MT8371 / Genio 520 and MT8189 as the tool reports it). Add:

17. Can the MP line run unfused and switch to fused mid-lot without re-qualification, and what changes on the station when it does?
18. Will CVTE and Malata accept a key rotation and a regenerated fuse image before their first fused lot, and what is the lead time?
19. What is the per-unit depot cost and turnaround for a fused unit at each ODM's service path, and does either require an additional auth file or certificate for secure download?
20. To CVTE: provide the `input.xml` and preloader GFH configuration used to generate `efuse_iFitG520.img`, with the values of `Enable_SBC`, `Enable_DAA`, `Disable_Rom_Cmd`, `brom_magic_cmd_mode_permanent_dis`, `jtag_en` and `debug_en`, and a read-back from a first-article unit showing the same.
21. To MediaTek: does BROM on MT8371 attempt the second preloader copy (eMMC boot1) when boot0 fails to load or fails authentication? The Secure Boot Developer Guide V1.1 section 3.1 documents this for NAND only.
22. To CVTE: which `MTK_SEC_BOOT` and `MTK_SEC_USBDL` values are set in the VKC1_20260909 and VKC1_20260919 preloader project makefiles?

---

## 9. Traceability

| This document | Source |
|---|---|
| Section 0 item 1, Section 1.1 conflicts 4 and 5 | Feasibility study: programming modes table, risk analysis 1–4, recommendations 1 and 3 |
| Section 1.1 conflicts 1, 2, 3, 6; glitch matrix IDs; kernel and build flag table; CTS/VTS modules | A/B Resiliency Test Plan v2.0 sections 3–6 |
| Program history, risk register R1–R19, groups A–N, sample matrix, exit criteria, open questions 1–16 | Closed-Config Brick-Resistance Test Plan r0.4 sections 2–7 |
| No RTC, rollback resistance unavailable | Cesium 0831 Boot Log Analysis, items 1 and 6 |
| Section 2.1 three-way table; preloader unverified under software RoT; `ATTR_SBOOT_ENABLE` versus `ONLY_ENABLE_ON_SCHIP`; key-rotation brick mode; DAA recovery constraint; conflicts 7 to 9; cases A0, A0-b, K0; assumptions 19 and 20 | Software Root of Trust Report sections 1.1, 3, 4, 5.1 to 5.3 |
| Verification of Source E; BROM secure boot flow and SBC_EN dependency; CERT1/CERT2 chain; `oemkey.h` into preloader, DA and LK; DAA AuthFile flow; NAND-only second preloader copy; `Disable_Rom_Cmd`, `jtag_en`, `debug_en`; conflicts 10 and 11; E2 rescope; G7 extension; Day 1 action 5; assumptions 21 and 22; open questions 20 to 22 | MT8391 MT8371 Android 15 Security Secure Boot Developer Guide V1.1, sections 2, 3.1, 4, 5.1, 5.2.1, 5.4, 6, 7 |

*Prepared for internal ICON review. Contains no verbatim reproduction of vendor documentation. Not yet issued to CVTE or Malata.*
