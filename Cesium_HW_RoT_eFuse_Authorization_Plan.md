# Cesium Hardware Root-of-Trust Authorization Plan

**Consolidated test, production and decision plan for burning the SBC eFuse on Cesium AOSP 15 tablets at CVTE, then Malata**

| | |
|---|---|
| Product | Cesium tablet (iFitG520), MediaTek MT8371 / Genio 520 (tool reports MT8189), AOSP 15, A/B seamless update, battery-less console |
| Current build | VKC1_20260909 (software root of trust, fingerprint `:user/dev-keys`) |
| MP release candidate | VKC1_20260909 (the last OS build; no 0919 build exists. Source B's header referred to a VKC1_20260919 that was never produced) |
| Mass production | ~3 Oct 2026 (three weeks from this revision) |
| Fused cohort | 100 units already fused by CVTE (line trial, 30 July 2026), serials recorded by the factory-test fuse check |
| Revision | 1.14 draft, 16 September 2026. Full history in Section 10 |
| Owner | Allen Middleton (Tablet Engineer, ICON Health & Fitness) |
| Supersedes | Cesium Closed-Config Field Brick-Resistance Test Plan r0.4 (test content carried forward with its case IDs); Android 15 Virtual A/B & AVB 2.0 Resiliency Test Plan v2.0 (glitch matrix carried forward with errata); Remote eFuse MT8371 Feasibility Study (conclusion adopted); MediaTek Security 2.1 Software Root of Trust Report (three-way comparison adopted, probability figures reinterpreted) |


**Reading this document.** Color badges mark what must happen and how badly it can go wrong.

<span style="background:#c62828;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">STOP-SHIP</span> blocks fusing or shipment until closed · <span style="background:#ef6c00;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">GATE</span> must pass before a later result counts · <span style="background:#1565c0;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">ACTION</span> someone must do this now · <span style="background:#2e7d32;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">CLOSED</span> evidence on file. Confidence levels in Section 3.5 use the same scale: <span style="background:#c62828;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">Not ready</span> <span style="background:#ef6c00;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">Low</span> <span style="background:#1565c0;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">Medium</span> <span style="background:#2e7d32;color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold">High</span>. Revision history is in Section 10.

---

## 0. Decision summary

**1. Field fusing is ruled out.** The feasibility study is adopted in full: eFuse writes on MT8371 are only possible from BROM/DA mode or a preloader self-blow, and self-blow via OTA on a battery-less unit with no hold-up supply is a brick-rate machine. Every Cesium unit is therefore either fused on the production line or never fused. There is no "ship open, close later" path. That makes the per-unit fuse decision permanent in both directions.

**2. Hardware root of trust does not raise the probability that a bad OTA is applied. It changes what can be recovered afterwards, and it adds exactly one new brick mode.** The question in the brief is answered in Section 2. On the A/B path (everything `update_engine` writes) a corrupt or truncated payload is rejected before any write regardless of fuse state, and slot fallback is fuse-independent. If the 0909 preloader is built with `ATTR_SBOOT_ENABLE` (to be confirmed by A0), the software root of trust already enforces LK, TEE and AVB signatures, so a mis-signed image already halts boot today. The fuse adds exposure in four places, none of which a 30-day soak measures well:

- **The preloader itself becomes verified.** Under software RoT the BootROM does not check the preloader; a corrupt preloader drops to BROM download mode and is re-flashed with no authorization. Under hardware RoT the BootROM halts on a hash mismatch, which is what the bricked first article shows (no USB enumeration). This is the one failure mode that is genuinely new with fusing, and E1 plus E5 exist to close it.
- **Key and fuse-image mistakes** become permanent and batch-scale (wrong hash, dev key, leaked key).
- **Every recovery path narrows** to signed artifacts: signed DA, re-signed firmware, older rescue images rejected. Leaving DAA unblown (G7, G11) keeps this narrower than Source E's worst case.
- **Keys are frozen for the life of the fleet.** Source E's software-RoT brick mode is a key rotation that updates LK but not the preloader. Since the preloader is excluded from OTA (E1), rotation is impossible after shipment in **both** configurations. Any rotation must happen before lot 1 ships.

Those four are controlled by gates, custody and rehearsal before the first unit is fused, not by field time. This is good news for the schedule: the risks that actually differ between open and closed are front-loadable.

**3. Program posture (decided): the 100 units CVTE has already fused are the field cohort; the remainder of mass production ships on software root of trust until the cohort has produced sufficient data.** This is Option A in Section 3.1 with a cohort that already exists, and it matches Source E's own recommendation for 100 to 500 unit field trials. Option B is withdrawn. Section 3.3 turns "track those serials for a period of time" into a protocol, because calendar time on its own measures nothing about OTA brick risk. The cohort must:

- **Pass release preconditions before any unit reaches a customer**: fuse-map read-back on a sample including `Disable_Rom_Cmd`, fingerprint and key checks on that build, and forced BROM download demonstrated on one healthy fused unit.
- **Receive at least two full OTA transitions** with per-serial telemetry, alongside a tracked unfused control group receiving the same packages.
- **Exit on evidence, not elapsed days**: zero unrecoverable units, outcomes indistinguishable from the control group, E5 demonstrated, and the Group G key gates closed.

Two consequences are accepted with this posture. Every unfused MP unit is permanently unfused. And every unfused MP unit must carry an `ATTR_SBOOT_ENABLE` preloader (A0-b), or the bulk of production ships with no boot-chain signature enforcement at all.

**4. Four items must start today** because they have the longest lead time and each one alone blocks fusing:

1. Revive bricked unit J26080143-0A00076 via forced BROM download (E5). If this cannot be shown, closed configuration is not accepted at all. **Status 15 Sep: attempted per CVTE's instruction (hold the download key during power-on) and failed; no enumeration in 120 seconds. Next step is S3 in Section 3.4: the same procedure on a healthy fused unit, with the on-board download switch CVTE photographed, SP Flash Tool V6 armed and the BROM VCOM driver installed.** This gates fused production (X3), not the cohort shipment.
2. ~~Resolve the `dev-keys` fingerprint versus ICON certificates.~~ **Resolved 12 Sep as to which key**: the certificates are ICON's (G2 closed on 0909, the MP release candidate). **Open as to custody**: the tag means the keys are consumed at compile time on CVTE's build system. G1 is now "release signing in a step separate from compilation, with keys ICON holds", requested from CVTE as item 12 of the 12 Sep consolidated ask.
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
| **G. 12 September 2026 inputs**: (i) 0909 `ro.build.fingerprint` and the separate dev-keys analysis with CVTE certificate evidence (OTA cert, `platform.x509.pem` and payload signature share SHA-256 `61:7C:CC:3A:...:1B:BF`, subject O = Icon Health and Fitness, CN = ifit.com; `delta_generator` verification against the ICON public key passed; `ro.boot.verifiedbootstate=green`, `ro.boot.veritymode=enforcing`); (ii) CVTE message describing the production-line fuse tool, compile-time signing and hash gate, and the factory-test fuse check; (iii) ICON's reply declining fusing on the next batch | The tag is a build-configuration artifact (`build/make/core/tasks/build_tags.mk`) and not evidence of which key signed. The certificate evidence settles G2. It does not settle custody: CVTE's own description places the private keys in the compilation pipeline. One follow-up from the analysis carried into Section 8: confirm the 39 APKs not signed with the ICON platform certificate are all expected third-party apps. |
| **H. 14–15 September 2026 inputs**: (i) CVTE (Simon Huang) answers to the 12-item ask: forced-flash instruction with a photo of the on-board download switch; `input.xml` and `GFH_CONFIG.ini`; `root_pubk.der`; `MTK_SEC_USBDL = ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP`; factory test configurable; keys unchanged since 27 July; `DA_BR.bin` and signed 0909 in VKC1_20260909.zip; SP Flash Tool Selector v1.2444 (use V6); cohort on VKC1_20260814 with 0814→0909 OTA package; schedule objection; release-keys deferred to the dev-keys analysis. (ii) CVTE anti-rollback explanation and confirmation `MTK_SECURITY_ANTI_ROLLBACK=no`, AVB rollback index 0. (iii) ICON verification by Shane Andrus: eFuse read-back, region diff, preloader `hw sbc = 1`, then a failed forced-download attempt on a deliberately bricked unit (no enumeration in 120 s) | First direct evidence on this program that the burn took effect through the whole stack, and the first measured failure of the only documented recovery path. Interpreted in Section 3.4. The attached `input.xml` and `GFH_CONFIG.ini` have not been read by the author of this plan; S1 reads them. |
| **I. G520 eFuse Burn Log** (Shane Andrus, 8 to 16 September 2026) | Chronological record on first article J26080143-0A00076: baseline (userdebug VKC1_20260907, orange, unlocked, both preloader slots identical); burn with CVTE's image over the BootROM path; read-back `sbc_en` on, hash `6da1756f…83730c68` matching the image, DAA, SLA, JTAG-disable off, no lock bits; silicon diff against unfused J26080163-0A00036; preloader log `hw sbc: 1`, `check sign pass`; a validly signed secure-boot-disable preloader accepted; 32 bytes flipped in the preloader RSA signature, written to boot0 only, BootROM halted; recovery attempts with tool armed, reset header, both images, CVTE's download key, 90 to 120 s bus monitoring each, zero enumeration; control unit enumerates on the same setup | Answers the stage question: the preloader, signature only, code intact. Identifies the bricked unit as ICON's first article, not a cohort unit. Records the depot hazard (tool wrote a mis-signed preloader) and the permissive-preloader finding. Names the next recovery step: eMMC test point. Interpreted in Section 2.3. |

### 1.1 Conflicts between trusted sources and how this plan resolves them

| # | Conflict | Resolution in this plan |
|---|---|---|
| 1 | **Anti-rollback.** Source A says `MTK_SECURITY_ANTI_ROLLBACK = yes` is supported and required; Source C recommends relying on it for field version management. Source B records MediaTek stating in Mar 2024 that it cannot be enabled on this project and CVTE reconfirming in Aug 2026 that it remains disabled on 8371. Source D shows the KeyMint side reports rollback resistance unavailable. | Treat anti-rollback as **disabled and to stay disabled for MP** (Group F). A signed known-good older build is then the fleet-wide escape hatch (F1), which matters more on a fused fleet than downgrade protection does. Source A case AVB-01 is rescoped to signature-based rejection only (F2); its "ARB counter check" pass criterion cannot be met. Obtain one written MediaTek statement to close the disagreement (open question 6). Agree a compensating control for signed-but-old pushes (open question 16). **Closed 15 Sep (Source H): CVTE confirms `MTK_SECURITY_ANTI_ROLLBACK=no` and AVB rollback index 0 on the current project, and explains the OTP mechanism: the minimum version per security group is pushed forward only when a valid higher-version image boots. Group F reduces to F1 (signed older build boots, the escape hatch) and F2 (unsigned downgrade rejected). F3 and F4 are moot. Residual: no downgrade protection anywhere, so a replayed signed old package is accepted; the control is OTA endpoint pinning (C13) and rollout telemetry (J4). The two-layer structure that caused this conflict is laid out in Section 2.5.** |
| 2 | **Virtual A/B.** Source A assumes copy-on-write snapshots and userspace merge (`snapuserd`, `dm-user`) throughout; roughly a third of its cases depend on this. Source B confirms A/B from the paired slot table (M1) but not the snapshot layer. | M2 and M3 run on Day 1. If virtual A/B is not enabled, PWR-02, PWR-04 and USR-01 are re-scoped to plain A/B slot writes rather than reported as failures. |
| 3 | **Verity error handling.** Source A corrects `CONFIG_DM_VERITY_AVB` to `y` for managed restart. Source B case M4 asks to confirm the verity-AVB immediate-invalidate option is **not** selected. | Do not edit kernel configuration on the basis of either document. The binding evidence is behavioral: M5 induces a single-block verity error on a sacrificial fused unit and must produce a controlled restart and slot fallback, never a loop or a brick. Record the actual defconfig and LK hashtree error mode alongside the result. |
| 4 | **Battery threshold.** Source C's 3.7 V cut-off applies to self-blow on battery. Cesium has no battery. | Irrelevant to field OTA (no self-blow ships). Relevant to the factory station: the burn depends entirely on the 12 V bench supply and the manual power sequence, so station power conditioning and interruption behavior are tested (L2, I4). |
| 5 | **Non-A/B boot chain.** Source A treats non-A/B as deprecated and out of scope. Source B records that the one demonstrated brick on this program was a non-A/B boot stage (corrupt `preloader_a`, intact `preloader_b` did not fail over, no USB enumeration). | Group E is the highest-value group in this plan. E5 is the single stop-ship. |
| 6 | **Iteration counts.** Source A requires 1,000 consecutive passing iterations. Source B requires zero unrecoverable units over a 200-cycle randomized soak. | 1,000 iterations on **open** units (cheap, automated, no scrap). 200 randomized interruptions on **fused** units, bounded by sacrificial hardware, with zero unrecoverable as the binding criterion. |
| 7 | **Bricking probability figures.** Source E estimates OTA bricking at 5 to 12 percent for software RoT and 25 to 40 percent for hardware RoT "if mismatched". Read as per-OTA rates these would make any OTA plan unshippable and would contradict Sources A and B. | Read them as **P(brick given a key or hash mismatch has already been shipped)**, which is what the wording says. The mismatch event is exactly what G1 to G6 and J1 prevent from ever leaving the build pipeline. The figures therefore quantify the cost of a gate failure, not the field rate of a gated fleet. They are not used as inputs to Section 6.3 until a measured source is found. |
| 8 | **DAA state.** Source E's hardware-RoT recovery case assumes both `SBC_EN` and `DAA_EN` are blown, so BROM refuses every unsigned Download Agent and recovery needs a signed `da.auth` or a MediaTek RMA certificate. Source B's plan blows SBC only and the SOP trace shows DA authentication disabled. | Cesium recovery is less constrained than Source E's worst case **as long as G7 and G11 hold** (only SBC set, DAA decision recorded, never blown in the same pass). Source E is the description of what Cesium becomes if DAA is ever blown without a demonstrated recovery path, which is why G11 is STOP-SHIP. |
| 9 | **What "software root of trust" enforces on 0909.** Source E: enforcement depends on the preloader build flag. `ATTR_SBOOT_ENABLE` verifies LK, TEE and AVB regardless of fuse state; `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP` verifies nothing until fused. Source B records both "mismatches are ignored" (Feb 2024) and "software AVB verifies bootloader/Android binding" (May 2026), which are consistent with different flags at different times. | A0 reads the flag from the 0909 preloader configuration and `sboot_state` from the console, then confirms behaviorally with a wrong-key LK. If 0909 is `ONLY_ENABLE_ON_SCHIP`, the open lot 1 under Option A ships with **no** boot-chain signature enforcement and the plan must require `ATTR_SBOOT_ENABLE` for open units (new gate A0-b). If it is `ATTR_SBOOT_ENABLE`, the brief's premise is correct and Section 2 stands as written. **Confirmed against Source F 5.2.1**, which states the SCHIP flags enable secure boot "according to eFuse SBC field" and the plain flags enable it "forcedly without eFuse to verify SW secure boot flow first". **Partly answered 15 Sep (Source H item 6): `MTK_SEC_USBDL = ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP`. `MTK_SEC_BOOT` not stated; the guide pairs the two, so assume `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP` until CVTE says otherwise. Consequence for unfused MP units: the preloader does not verify LK. Whether anything is enforced then depends on LK's lock state and AVB. A0-b is rescoped: instead of mandating a preloader rebuild before 2 October, verify on an unfused 0909 unit that `ro.boot.verifiedbootstate=green`, `ro.boot.flash.locked=1`, fastboot unlock is refused, and a wrong-key `vbmeta` is refused at boot. If all four hold, the unfused fleet enforces AVB from LK (a software root anchored in LK rather than the preloader) and ships as is; if not, the preloader flag change is required and re-test follows.** |
| 10 | **Preloader A/B failover.** Source B case E2 expects a fused unit with corrupt `preloader_a` to boot from `preloader_b`, and open question 1 asks why it did not. Source F 3.1 note B states BROM fallback to the second preloader copy is supported **if the external storage is NAND flash**. Cesium boots from eMMC. | E2 and E3 are rescoped from pass/fail to characterization: record whether eMMC boot1 fallback exists on MT8371 at all and obtain MediaTek's written answer. Until then, assume **no preloader redundancy** on this product. R1's mitigation is therefore E1 (preloader never in OTA scope, enforced by pipeline) plus E5 (forced BROM download proven), with no third leg. |
| 11 | **BROM command-mode disable.** Source B's fuse-map gate G7 lists SBC, DAA, JTAG and PTSB. Source F section 7 adds `Disable_Rom_Cmd` (also `brom_magic_cmd_mode_permanent_dis` in the preloader GFH config) and "highly recommends" setting it: BROM "cannot receive any commands to download, disable secure boot check, and so on anymore". Source E's hardware-RoT recovery column assumes DAA only. | If this bit is set, forced download does not exist and E5 cannot pass on any fused unit. G7 now reads it back explicitly and requires it **unset**. Day 1 action 5 inspects `input.xml` and the burned image. The observed no-enumeration brick is consistent with either a BROM halt on hash mismatch (Source E 5.3) or this bit being set; the two are distinguished by whether the forced-download button sequence produces enumeration on a fused, otherwise healthy unit (CLOSED-5). **Resolved 16 Sep: CVTE's 27 July build log shows `EFUSE_Disable_BROM_CMD = 0` and the project has no `brom_magic_cmd_mode_permanent_dis` setting. BROM command mode is enabled on the cohort. The brick is therefore a BootROM behavior or entry-path question, not a fuse-map error; MediaTek's answer to ask 15 decides it.** |
| 12 | **Pre-flash signature check (r1.13).** CVTE, Aug 2026: three-stage enforcement including a preloader-level check of the firmware signature against the eFuse key **before flashing**. Source I: SP Flash Tool wrote a preloader with a corrupted RSA signature to boot0 of a fused unit and reported success. | The pre-flash check does not exist on the download path used (DAA off, unsigned DA accepted, host writes whatever it is given). The download path is a depot hazard on fused units: a wrong or mis-signed preloader is a hard brick. Mitigations: depot profile excludes boot0 unless a chip-level fix requires it (H1, R19); depot artifacts hash-verified against the release manifest before use (H4); ask CVTE which stage, if any, performs the check they described (ask 25). |

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
| Behavior on LK/TEE signature mismatch | Boots | Halts at preloader assertion | Halts at preloader assertion |
| Behavior on preloader corruption or mismatch | BROM download mode | BROM download mode; re-flash preloader, no auth file | **BROM halts.** No enumeration observed on Cesium. Forced-download entry (E5) is the only path |
| USB flashing protection | Any DA | Any DA unless `ATTR_SUSBDL_ENABLE`; SOP trace shows DA auth disabled on Cesium | Signed DA if DAA blown; Cesium leaves DAA unblown (G7) |
| Key rotation | Re-flash | Re-flash preloader (not possible by OTA on Cesium, E1) | Impossible |
| Reversibility | Full | Full, by re-flash | None |
| Source E's recommendation | Bring-up only | 100 to 500 unit field trials | Production shipping mode |

*The unsigned column is reference only. It is not a program option: all Cesium testing has run on software root of trust and the 2 October MP date does not permit a configuration change. The comparison that matters is the right two columns.*

### 2.2 Failure modes, open versus closed

| Failure mode | Software RoT (open, if `ATTR_SBOOT_ENABLE`) | Hardware RoT (SBC fused) | Marginal risk from fusing |
|---|---|---|---|
| Corrupt, truncated or bit-flipped OTA payload (C1, C2) | Rejected by `update_engine` hash check before any write | Same | **None.** Fuse is not consulted. |
| Delta against wrong source build (C12) | Rejected before write | Same | **None.** |
| Package signed with wrong or test key (C3, C4) | Slot fails preloader/AVB check at boot; falls back to previous slot | Same | **None on the mechanism, if fallback works on a fused unit** (C5–C10). If 0909 is `ONLY_ENABLE_ON_SCHIP`, the open unit boots foreign code instead and security, not brick risk, is what changes. |
| Corrupt `vbmeta`, `boot.img`, hash tree in the inactive slot (C5–C7) | Fallback to good slot | Fallback to good slot | **None, conditional on C5–C10 and M5.** |
| Power loss during download, write, post-install, slot switch, first boot (D1–D9, PWR-01..04) | A/B protects; boots good slot | Same | **None on the A/B mechanism.** Slot-metadata behavior (M6–M8) must be verified once; it is fuse-independent. |
| Panic before boot-success marker (C8) | Auto revert | Auto revert | **None.** |
| Corrupt non-A/B stage: preloader / boot0 (E2–E4) | Soft brick: BROM download mode, re-flash with any DA and any preloader. No second-copy fallback on eMMC (Source F) | **Hard brick unless forced download works.** BootROM halts on hash mismatch; observed on J26080143-0A00076. If `Disable_Rom_Cmd` is set, no download mode exists at all | **High until E5 passes. This is the one new brick mode.** Mitigation is contractual: OTA never writes preloader/boot0 (E1), and the fuse map leaves BROM command mode enabled (G7). |
| Key rotation that updates LK but not preloader (Source E 5.2) | Halts at preloader; recoverable by USB re-flash of preloader | Halts; recoverable only with signed artifacts; hash cannot change | **Both fatal in the field** because the preloader is outside OTA scope. Rule: keys are frozen before lot 1 ships. |
| Wrong key hash, dev key, or leaked private key burned (R2, R3) | N/A: re-flash preloader with new key | Permanent, fleet-wide | **Critical and new.** Only gates prevent it (G1–G6). |
| Depot re-flash of a failed unit (H1) | Any image, any DA | Signed DA and re-signed image; earlier rescue images rejected | **Medium: cost and process, not probability.** Less severe than Source E's case because DAA stays unblown. |
| Storage bit rot in active slot (C11) | Verity detects (AVB enforced by preloader) | Same | **None if M5 passes.** |
| Factory fuse write itself (L1–L8, I1–I5) | N/A | Manual, ordered, irreversible | **Medium, line-side only.** 100-unit CVTE trial with zero failures is encouraging, not sufficient. Malata has no fuse experience at all. |

### 2.3 What the bricked first article does and does not prove (r1.13, from Source I)

**The method.** Shane fused J26080143-0A00076 on 8 September with CVTE's image over the BootROM download path (userdebug VKC1_20260907, unlocked, orange before and after; lock state is independent of the fuse). Read-back, silicon diff against an unfused sister and the preloader log (`hw sbc: 1`, `check sign pass`) confirmed the burn. A validly signed alternate preloader booted. Then 32 bytes inside the preloader's RSA signature were flipped, code untouched, and that copy was written to boot0 (`preloader_a`) only, `preloader_b` left good. BootROM refused it and halted. No USB interface since, through cold boot with the tool armed, the reset header, both signed images, and CVTE's download-key instruction, 90 to 120 seconds of bus monitoring each time. The control unit enumerates on the same cable, port and driver.

**What it proves.** The fuse works end to end, and a fused MT8371 whose preloader fails authentication has no USB recovery path by any documented method. That is the one failure mode Section 2.2 says is new with fusing, demonstrated cleanly.

**What it does not prove.** That the field will produce this failure. The corruption was signature-only. On an unfused unit the identical write does nothing: BootROM does not check the signature, the code is intact, the tablet boots. Nothing in the field produces a signature-only corruption. The two natural causes of a bad preloader are an OTA that writes it (excluded by E1, to be confirmed by S2 and the vendor-freeze check below) and eMMC boot0 failure, which corrupts code as well as signature. A code-corrupt preloader does not boot on an unfused unit either.

**Consequence for RMA cost, using the program's own constraint.** Most Cesium tablets cannot be feasibly disassembled to flash in the field, so a non-booting tablet is a field replacement in both configurations. Fusing therefore does **not** change the field RMA count from preloader failures. It changes whether the returned unit can be refurbished at the depot. The added cost is depot scrap on the rare boot0 failures, roughly the refurbishment value of a tablet per incident, unless a BootROM recovery (E5, or the eMMC test point in ask 24) is demonstrated, in which case the delta is zero. Section 6.3 is revised on this basis.

**Comparison the program already lives with.** On the AOSP 13 fleet with no image signing, an OTA that omitted the EMM APK would leave the tablet functionally useless. That is recoverable by manually installing the APK, which on a console that cannot be opened means a service visit or a remote path, not a re-flash. Software-level failures of that kind dominate real RMA cost and are identical under software and hardware root of trust. The fuse touches none of them.

**Two findings in the log unrelated to brick probability.**

1. SP Flash Tool wrote a preloader with a bad signature onto a fused unit and reported success. CVTE's August statement that the preloader level checks the firmware signature against the eFuse key before flashing did not hold on this path (conflict 12). The depot can brick a fused unit by mistake. Mitigation: the depot profile never writes boot0 unless a chip-level fix requires it (H1, R19), and every depot artifact is hash-verified against the release before use.
2. A validly signed "secure-boot-disable" preloader, differing from production only in build flags, exists and boots on a fused unit. Anyone holding that binary can downgrade the chain's enforcement on any fused Cesium. It is key material and falls under G3 custody and G6 signing process: it must never be signed with the production root key again, and existing copies must be inventoried.

**Vendor-freeze background (ICON note, 16 Sep).** MediaTek Android 15 BSPs commonly use a vendor-freeze model in which the framework moves to Android 15 while vendor and bootloader layers stay on the previous release; in that model the preloader is not changed or flashed by OTA. MediaTek can include `preloader.bin` in `payload.bin`, in which case `update_engine` writes the inactive slot before switching. OEMs generally exclude it unless a chip-level fix, DRAM initialization change or anti-rollback version requirement forces it. Two checks settle it for Cesium and both are now in S2 and E1: the partition list in `payload.bin`, and `AB_OTA_PARTITIONS` in the board configuration, which controls whether the OTA builder can ever emit a preloader image.

### 2.4 Random power loss during OTA: what fusing adds (r1.13)

iFIT's internal OTA testing runs under normal conditions. Random power loss is rare on a mains-powered console but it happens, and it is the scenario the brief most fears. This section isolates what fusing changes about it. The answer depends on which partition the write is in when power drops.

| Phase of the OTA when power is lost | What is on disk afterwards | Unfused unit | Fused unit | Delta from fusing |
|---|---|---|---|---|
| Download | Partial package in cache; no partition touched | Boots active slot; resumes or restarts download | Same | **None** |
| Writing Android partitions to the inactive slot (system, vendor, product, boot, dtbo, vbmeta*) | Inactive slot half-written; active slot untouched; slot not yet marked bootable | Boots active slot; update restarts | Same. AVB on the inactive slot is never consulted until it is selected | **None** |
| Writing **LK or TEE** to the inactive slot (only if they are in the payload) | Inactive LK/TEE half-written; active slot untouched; slot not marked bootable | Boots active slot | Same. Inactive slot not selected | **None**, because the slot switch has not happened |
| Slot switch written, before first boot of the new slot | Bootloader control block points at new slot; new slot fully written | New slot boots; if LK were somehow bad it would crash and the retry budget falls back | New slot boots; if LK were bad the **preloader refuses it** and the retry budget falls back | **The only real delta.** Refusal versus crash. Both rely on the same slot-fallback mechanism; fusing changes the failure signal, not the path. Tested by S5 unit 5 and by C5/C9 on fused units |
| First boot of the new slot, before success marker | Same as above | Retry budget, fallback to old slot | Same | **None** |
| Post-install, userdata migration | A/B partitions complete | Documented data reset at worst | Same | **None** |
| Preloader / boot0 | **Never written by OTA** (E1, S2, `AB_OTA_PARTITIONS`) | Not reachable | Not reachable | **None.** A power cut cannot create the Section 2.3 brick, because the OTA never opens boot0 for writing |

**Reading it.** The hard-brick mode of Section 2.3 requires a write to boot0. The OTA does not write boot0, so no power-loss event during an OTA can produce it, in either configuration. Every other interruption lands on an A/B partition, and the A/B mechanism does not consult the fuse until the slot is selected. The only point where a fused unit behaves differently is the first boot of a new slot whose LK or TEE is somehow bad: the fused preloader refuses it where an unfused preloader would crash on it. Both outcomes depend on the same boot-control retry and fallback logic, which is fuse-independent and is exactly what S5 unit 5 exercises by cutting power during the first boot up to three times.

**How big is the window.** If LK and TEE are in the payload at all, they are roughly a megabyte each in a package of several hundred megabytes, so a random cut lands during their write well under one percent of the time, and even then the slot is not yet selected. The exposure is not the write; it is the subsequent first boot, which S5 tests directly.

**What this means for the tests.** S5's two cuts (mid-write, first boot) are the minimum. The 200-cycle randomized soak (D7) on fused units is what turns "no difference expected" into a measured rate, and it is automatable with a programmable 12 V supply and a UART console. Recommendation: run D7 on the seven test units once they reach Logan, before customer release rather than before fused production. It takes about a week of unattended cycling and it is the direct answer to the question iFIT is actually asking.

### 2.5 Anti-rollback: two layers, and Cesium's state in each (r1.14)

"Anti-rollback" on this platform is two separate mechanisms that share only the idea of a one-way version counter in OTP. Conflating them caused conflict 1. The distinction matters for the fuse decision because one of them is the only OTP write an ordinary field update can trigger.

| | Level 1: MediaTek bootloader ARB | Level 2: AVB 2.0 rollback index |
|---|---|---|
| Defined by | MediaTek BSP, `MTK_SECURITY_ANTI_ROLLBACK = yes` in the project | Google AVB 2.0 specification, `BOARD_AVB_*_ROLLBACK_INDEX` at build time |
| Enforced by | BootROM, Preloader, LK, DA when they load the next stage | LK when it verifies `vbmeta` before booting Android |
| Images covered | Secure group: LK, ATF, TEE (loaded by Preloader). Non-Secure group: modem, SCP and similar (loaded by LK) | Android partitions described by `vbmeta` (`boot`, `system`, `vendor`, `product` and variants). Recovery group separately if `OTP_FRAMEWORK_v2` is enabled |
| Where the minimum version lives | OTP eFuse groups (or RPMB on some parts), one minimum per group | AVB OTP group (and Recovery group under `OTP_FRAMEWORK_v2`) |
| Check | Version in the image certificate compared to the group minimum; lower halts boot | `rollback_index` in `vbmeta` compared to the AVB counter; lower rejects the slot |
| When the counter advances | After a higher-version image boots successfully, one-way | After the new slot reaches `boot_completed` and passes health checks, LK or Preloader commits the new index atomically, one-way |
| **Cesium state** | **Disabled.** `MTK_SECURITY_ANTI_ROLLBACK=no` (CVTE, 15 Sep; MediaTek, Mar 2024). No Level 1 check runs, no Level 1 counter is ever written | **Present but inert.** AVB rollback index is 0 on every build so far. LK performs the comparison, it always passes, and the atomic commit never advances the counter because the index never rises |

**How the two layers interact with A/B fallback, and why fusing does not change it.** `update_engine` writes the new images and `vbmeta` to the inactive slot; the active slot and every OTP counter are untouched. On first boot LK checks the new slot's `rollback_index` against the AVB counter. If it is lower, LK rejects the slot and the boot-control retry logic falls back to the old slot, which still boots because no counter was advanced. If it is equal or higher, the slot boots, and only after `boot_completed` is the counter committed. This ordering is what makes an A/B update safe with anti-rollback on: the irreversible write happens last, after the new slot has proven itself. `OTP_FRAMEWORK_v2` keeps the AVB and Recovery groups separate so a system update cannot advance a bootloader counter by accident. None of this consults `SBC_EN`; the SBC fuse governs who may sign the preloader, not which version may boot.

**What this means for the plan.**

- With Level 1 disabled and Level 2 at index 0, **no OTA on Cesium writes OTP**. The one field-triggered OTP write on this platform, the AVB counter commit, is dormant. This is why Group F reduces to F1 and F2 and why the plan recommends leaving both levels as they are for MP: a signed older build remains the fleet escape hatch.
- The residual is that no downgrade protection exists at any layer. A replayed signed old package is accepted. The compensating controls are OTA endpoint pinning (C13) and rollout telemetry (J4), not a counter.
- If ICON ever raises the AVB rollback index or enables Level 1, the analysis in Section 2.4 changes: a power cut between `boot_completed` and the atomic commit becomes a case to test (F4), and a downgrade to a known-good build stops being available as a recovery lever. That is a decision to make deliberately, in writing, and not before the fused cohort has proven the fallback path.
- Whether `OTP_FRAMEWORK_v2` is enabled in Cesium's LK is unknown and is added as ask 28. It is harmless today with index 0 but decides how the Recovery slot would behave if the index ever moves.

**Conclusion.** If 0909 enforces software RoT, fusing changes nothing about how an OTA is verified or how a slot falls back. It adds one brick mode (preloader), removes every unsigned recovery route, and makes key errors permanent. The financial exposure therefore moves from "unforeseen OTA bug" (bounded by staged rollout regardless of fuse state) to "preloader integrity, key custody, and recovery procedure" (bounded only by E1, E5 and the Group G gates). Source E's own recommendation, software RoT for field trials of 100 to 500 units and hardware RoT for shipping, is the same posture as Option A.

---

## 3. Authorization options and schedule

### 3.1 Options

*Revision 1.3: Option A is the decided posture, with the 100 CVTE-fused units as the pilot ring (Section 3.3). Option B is retained in this table for the record only and is withdrawn.*

| | Option A (decided) | Option B (withdrawn) |
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
| 2–6 | Open units (5) | C1–C13 rehearsal; D1–D9 and PWR-01..04, USR-01 at 1,000 automated iterations; F1–F3 | Every case ends in a booting unit; behavior baselined |
| 4–10 | Fused sacrificial (5 + spares) | E2–E4, E6; C1–C13 five times each; D7 200-cycle randomized soak; D8 brown-out; M5 verity error; N3 attestation; G4 hash regeneration; G7 fuse map read-back; G9 userspace fuse-write attempts | Zero unrecoverable; every failure mode has a recovery path |
| 8–14 | CVTE line | L1–L8 and I1–I5 witnessed by ICON; G10 build audit; H1–H5 depot at CVTE and at the US service site including a full-image profile (R19) | Station interlocked; per-serial trace; depot proven at two sites |
| 12–18 | Release engineering | J1–J5: pipeline signature gate, rings at 0.1 / 1 / 10 / 100 percent, automatic halt, kill switch, CDN integrity, telemetry incl. fuse state | Bad build halted in a lab ring |
| 1–10 | Cohort preconditions | P1 fuse-map read-back on ten of the 100; P2 forced download on a healthy fused unit; P3 fingerprint, certificates, attestation on the cohort build; P4 key decision; P5 backend records; P6 software parity | Cohort cleared for ICON-controlled placement |
| 10 onward | Cohort field (Section 3.3) | ICON-controlled ring of 15 to 20 takes the first OTA; customer placement of the remainder after that; K2 two OTA transitions; K3 two depot recoveries; control group tracked in parallel | X1 to X4 (completes after MP, likely 60 to 90 days) |
| 19 | **Re-test only if re-signed** | 0909 is the MP release candidate, so no separate final-build re-test is scheduled. If G1 (separate release-signing step) or a key decision (K0) produces a re-signed 0909, re-run G2, G4, N3, B1, B2, C3, C5, D2, D4, F1, M5 on that artifact; reserve 3 days for it. Any re-sign changes hashes; nothing tested on the compile-signed 0909 transfers automatically | Final artifact pairing signed off (L5) |
| 18 | **Go / No-Go** | Tier 0 and Tier 1 review. Option B only if all pass. | Signed decision record |
| 21 | MP start | Option A or B per decision | |
| MP + 5 to 10 | Malata | Tier 2 transfer and witnessed first-article run before Malata's first fused lot | |

With 0909 confirmed as the release candidate, the schedule no longer waits on a new build; the only re-test trigger is a re-signed artifact from the G1 or K0 decisions. With Option B withdrawn, the Day 18 decision is narrower: it authorizes release of the fused cohort to the field and confirms the unfused MP configuration (A0-b), not fusing of production.

### 3.3 Fused field cohort protocol (the 100 CVTE units)

The cohort exists, so the question is not whether to build a pilot but how to extract a decision from it. "Track the serials for a period of time" is restated below as preconditions, a measurement, a control, and exit criteria.

**Release preconditions.** None of the 100 goes to a customer until all of these are on file.

| # | Precondition | Why |
|---|---|---|
| P1 | Fuse-map read-back on at least ten of the 100: `sbc_en` set, `sbc_pub_key_hash` matches the ICON-verified hash (G4), `Enable_DAA`, `Disable_Rom_Cmd`, `jtag_en`, `debug_en` recorded. Cross-check against the `input.xml` CVTE used (open question 20) | The image that was burned is unverified. If `Disable_Rom_Cmd` is set, the cohort has no USB recovery path and a field brick is a board swap |
| P2 | Forced BROM download demonstrated on one healthy unit from the cohort, then E5 on BRICK-1 | Proves the recovery path exists for this exact fuse map before customers depend on it |
| P3 | G2 and N3 on the cohort's build: certificate chain resolves to ICON (closed on 0909, repeat on the cohort's actual firmware), key attestation reporting verified and locked against the burned hash. G1 (release signing step) is not a precondition for the cohort, since re-signing would not change the fused hash | The 30 July build predates the dev-keys review; the cohort may not be on 0909 |
| P4 | Key-rotation decision recorded (G3, K0). If ICON rotates, the cohort keeps its own signing chain for life or is withdrawn; if not, the accepted residual risk of the Basecamp-distributed key is signed off | The cohort's hash is fixed. Rotation splits the fleet into two signing chains permanently |
| P5 | Per-serial record for every cohort unit in the OTA backend with fuse state, fingerprint, slot and the depot routing flag (J4) | Depot must never attempt an unsigned flash on a cohort unit, and OTA rings must be able to target by fuse state |
| P6 | Cohort units run the same OTA client, telemetry agent and release as the unfused MP units | Otherwise cohort and control are not comparable |

**Allocation of the 100.** Not all of them should go to customers.

| Allocation | Qty | Use |
|---|---|---|
| Sacrificial and golden test units | 7 | CLOSED-1..7 in the sample matrix (Groups C, D, E, H, M, N3). Replaces the need to build new fused units |
| ICON-controlled field units | 15 to 20 | Offices, employee homes, test gyms. First ring for every cohort OTA; depot rehearsal candidates (K3) |
| Customer field units | remainder (roughly 70 to 75) | Normal retail flow via console vendor, finished-goods vendor and warehouse or store. Held at CVTE until P1 to P6 and the ring's S5 pass; OTA'd 0814→0909 at CVTE with per-serial logs before leaving, so customers receive 0909 (r1.12) |

**CVTE deliverables to release the cohort (r1.7).** All were sent to CVTE on 12 September as one consolidated 12-item ask (Section 8). Column "Sent as" gives the item number in that message.

| # | Deliverable | Plan reference | Sent as |
|---|---|---|---|
| C1 | eFuse read-back log per serial for all 100, plus the `input.xml` and preloader GFH configuration used to build `efuse_iFitG520.img` | P1, G7 | Item 4 |
| C2 | Demonstrate forced BROM download mode on one healthy fused unit, then recover J26080143-0A00076 with a signed build. Video plus console trace, with the exact button, hold timing and tool version | P2, E5 | Items 1 to 3 |
| C3 | `MTK_SEC_BOOT` and `MTK_SEC_USBDL` values in the 0909 preloader makefile | A0, A0-b | Item 6 |
| C4 | Root public key (`root_pubk.der`) so ICON can regenerate `sbc_pub_key_hash` and match it to read-back | G4 | Item 5 |
| C5 | Signed `DA_BR.bin`, signed 0909 image, pinned SP Flash Tool and driver versions, and a written depot procedure including a full-image profile, not only the boot-chain profile | H1, H4, R19 | Item 9 |
| C6 | Firmware version currently on the 100, and confirmation that the 0909 OTA package (full or incremental) applies to it | P6, K2 | Item 10 |
| C7 | Seven of the 100 released to ICON as CLOSED-1..7 for destructive testing | Sample matrix | Item 11 |
| C8 | Same root, image, DA and platform keys for the cohort and the unfused batch | P6 | Item 8 |
| C9 | Factory test accepts unfused units and logs eFuse state per serial | I6 | Item 7 |
| C10 | Release-signing step separate from compilation | G1 | Item 12 |

ICON-side prerequisites: N3 key attestation on a cohort unit, P5 backend records with fuse state per serial, and the 0909 OTA applied to the ICON-controlled ring before any customer placement.

**Measurement.** Field time produces no data unless updates are pushed. The cohort must receive at least two full OTA transitions (K2), one of which should be the transition every MP unit will also take. Per serial and per transition, record: download outcome, install outcome, slot switch, boot-success marker, boot attempts before success, verified-boot state after update, and any depot or RMA event with its recovery result. Naturally occurring power interruptions on a battery-less console are part of the exposure and should be counted from boot-reason telemetry.

**Control group.** The unfused MP units are the control. Track a matched sample (at least the same size as the customer cohort, preferably ten times larger) through the same OTA transitions with the same telemetry. Since fusing does not change how an OTA is verified or how a slot falls back (Section 2), the two populations should be indistinguishable. Divergence is the finding.

**What the cohort can and cannot show.** With roughly 100 units and two transitions, zero failures bounds the fused OTA brick rate at about 1.5 percent at 95 percent confidence. That detects a systematic defect in the fused path. It does not detect a rare one, and it says nothing about key custody, depot readiness or line controls, which remain gated by Tiers 0 to 2 regardless of cohort results. The cohort retires R13 (no organizational experience) and R5 (fallback on a fused unit never measured); it does not retire R1, R2 or R3.

**Exit criteria for authorizing fused production.**

| # | Criterion |
|---|---|
| X1 | At least two OTA transitions completed across the cohort with zero unrecoverable units |
| X2 | Cohort update-outcome distribution indistinguishable from the control group on the same transitions |
| X3 | E5 passed: forced BROM recovery demonstrated on a bricked fused unit |
| X4 | At least two cohort units recovered at a depot using only the published procedure (K3, H1) |
| X5 | All Tier 0 gates closed, including G3/K0 key decision and G7 fuse map with `Disable_Rom_Cmd` unset |
| X6 | Tier 1 line controls passed at CVTE; Tier 2 at Malata before Malata's first fused lot |
| X7 | Decision recorded with the accepted count of permanently unfused units shipped during the cohort period |

Minimum elapsed time is set by X1, not by a calendar. Two transitions at a normal release cadence is likely 60 to 90 days.

### 3.4 Cohort release status and simplified remaining test set (15 September)

**Two decisions, two gate lists.** Revisions 1.3 to 1.7 let the cohort shipment and the fused-production authorization share one list. They should not. Fielding 100 fused units exposes ICON to a boot-chain brick only through storage failure of boot0, because the preloader is outside OTA scope. On 100 units that is a small fraction of a unit per year, about $220 of expected loss (Section 6.3). The 200-cycle soak, the five-times C group, the vendor suites, the key tabletop and the line-control witness all gate fusing 100,000 units. They do not gate fielding 100. This section lists only what the cohort needs.

**CVTE answers to the 12-item ask (Source H, 14 Sep) and ICON verification (Shane Andrus, 15 Sep).**

| Item | CVTE answer | Effect on plan |
|---|---|---|
| 1–3 Forced download | "Press and hold the Volume Up (Download) key during startup." Photo shows an on-board tact switch near the 12 V input on the C.G520.702 board; reaching it means opening the enclosure. No video, no tool log, no BROM versus preloader distinction | ICON attempted it on the deliberately bricked unit: **no USB enumeration in 120 s**, nothing in Device Manager, SP Flash Tool never connected. **E5 and P2 remain open.** See "Interpreting the failure" below |
| 4 `input.xml`, `GFH_CONFIG.ini` | Files attached (2.75 KB, 751 B). **16 Sep: build log of 27 July supplied: `Enable_SBC = 1`, `Enable_DAA = 0`, `Enable_SLA = 0`, `Disable_BROM_CMD = 0`, `Disable_DBGPORT_LOCK = 0`, `USB_download_type = 0`; no `brom_magic_cmd_mode_permanent_dis` in the project; MediaTek default configuration** | S1's ROM-command question closed by build evidence; ICON's read of the files and the read-back leg remain as confirmation. Shane's read-back already shows `daa_en`, `sla_en`, `jtag_dis` off, consistent with the log |
| 5 `root_pubk.der` | Attached (294 B) | G4 executable by ICON: regenerate the SHA-256 of the DER public key and compare to `sbc_pub_key_hash` read back. Shane reports the read-back matches `efuse_iFitG520.img` exactly; regeneration from the public key is the independent leg (S1) |
| 6 Preloader flags | `ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP` | Download authentication off on unfused units (good for depot). `MTK_SEC_BOOT` **not answered**; assume the matching SCHIP value. A0-b rescoped to an LK lock-state and AVB check on an unfused 0909 unit (conflict 9) |
| 7 Factory test | Test items configurable via configuration files | I6 achievable: an unfused profile that still logs eFuse state per serial. Confirm the profile is version-controlled and not operator-selectable |
| 8 Keys | `da_prvk.pem`, `root_prvk.pem`, `img_prvk.pem` unchanged since 27 July (AVB 3.0 firmware); OTA uses certificate verification; image signature identical fused or unfused | C8 closed. One signing chain for cohort and MP. **Key rotation is now off the table for the cohort** (P4 resolves to "no rotation; accept residual risk of the Basecamp-distributed key in writing; remove the attachments") |
| 9 Depot artifacts | `DA_BR.bin` and signed 0909 in VKC1_20260909.zip; SP Flash Tool Selector v1.2444 and USB driver attached; use V6 | Artifacts in hand. Written depot procedure with a full-image profile still missing (H1, R19). S4 exercises the artifacts |
| 10 Cohort firmware | Cohort on VKC1_20260814 user build; OTA 0814→0909 package `VKC1_20260814_20260909.zip` (436 MB) attached; same signature since 0726 | C6 closed. **The first counted OTA transition (X1) is ready to run** |
| 11 Schedule | "If we need to wait for test results, production won't be able to keep up." | Answer to CVTE: production is not waiting. The MP batch ships unfused (decision of 12 Sep). Only customer release of the 100 fused units waits, and only on S1 to S6 below |
| 12 Release keys | Refers to the dev-keys analysis link | Treated by CVTE as resolved. G1 (separate release-signing step, ICON custody) remains open but is **not** a cohort precondition (P3). It gates fused production |

**ICON verification results (Shane Andrus, 15 Sep), recorded as evidence.**

| Check | Result | Closes |
|---|---|---|
| SP Flash Tool `read-efuse` on a cohort unit | `sbc_en = on`; `sbc_pub_key_hash` matches `efuse_iFitG520.img` exactly; `daa_en`, `sla_en`, `jtag_dis` off | G7 except the BROM command-disable bit; P1 on one unit; G11 posture confirmed (DAA unblown) |
| eFuse region diff, fused unit versus unfused sister | Key hash present in silicon on the fused board, all-zero on the control | Independent confirmation the burn took |
| Normal boot after read-back | dm-verity enforcing; `vbmeta` digest and AVB metadata intact; preloader log `hw sbc = 1`, firmware signature check passed | Software stack sees the fuse; N3-equivalent evidence for the cohort |
| Negative test: bad signature written to "the bootloader" | Unit unbootable, as intended | Confirms enforcement |
| Recovery: download key held during power-on, 120 s USB monitoring | **No MediaTek device enumerated** | E5, P2 **fail as executed** |

**Interpreting the failure.** Three facts are needed before the result means anything, and the first two are ICON-side.

1. **Which stage was corrupted.** **Answered by Source I: the preloader, 32 bytes inside its RSA signature, code intact, boot0 only.** The download-key path is polled by the preloader, so it never ran; the instruction from CVTE could not have applied. BROM entry therefore depends on BROM's own behavior after an authentication failure, which on this unit is a halt with no USB. The next path to try is one where BROM finds no preloader at all (eMMC test point, ask 24), which is a different BootROM code path from a failed authentication.
2. **The BROM command-disable bit.** It is in the `input.xml` and `GFH_CONFIG.ini` ICON now holds (S1). Set, no procedure can reach a fused unit whose preloader is bad.
3. **Whether the procedure works on a healthy fused unit** (S3). This is the discriminator the plan has asked for since revision 1.2. A healthy unit that enumerates in BROM or preloader mode proves the path exists on this fuse map; a healthy unit that does not proves the map or the procedure is wrong for all 100.

**Where the units are (corrected 16 Sep).** The 100 fused units are at CVTE. ICON holds the bricked unit from Shane's negative test and at most two other fused units. S1 and S2 are desk work and run at ICON today. S3 to S6 need fused hardware, so they are split by location:

| Step | Executor | Location | How ICON gets evidence |
|---|---|---|---|
| S1, S2 | ICON | Logan | Own records |
| S3 | CVTE first, on a healthy fused unit, with ICON's attempt A/B/C procedure; ICON repeats on its own healthy fused unit if it has one | CVTE (and ICON) | Video of the bus monitor and tool console, VID:PID log, unit serial |
| S4 | CVTE, same unit, straight after S3 | CVTE | SP Flash Tool console log, before/after `read-efuse` logs |
| S5 | ICON, on the first shipment of ring units after they arrive | Logan | Own records. Cannot start until units arrive |
| S6 | CVTE, from the per-serial line logs plus three fresh `read-efuse` runs | CVTE | The 100 per-serial fuse logs (item 4 of the ask) plus three new logs |

**Shipment and manufacturing flow (corrected 16 Sep).** Production tablets from CVTE and Malata do not ship to Logan. The normal flow is ODM → console vendor (tablet integrated into the console) → finished-goods vendor (boxed) → warehouse or store → customer. A tablet on that path is not powered or connected until a customer sets it up. Three consequences:

| Consequence | Plan change |
|---|---|
| The ring and test units are an **exception shipment**. Nothing flows to Logan by default | CVTE pulls 15 to 20 ring units plus the 7 test units out of the lot and ships them directly to Logan, on 0814, not reflashed. ICON arranges the shipment and provides consoles or 12 V bench fixtures at ICON sites, since bare tablets are not the shipped product. Transit about one week; S5 cannot complete before about 25 September |
| The 70 to 75 customer cohort units would otherwise reach customers on 0814 and take their first fused OTA in a customer's home | **CVTE applies the 0814→0909 OTA to the customer cohort units at CVTE before they enter the console flow**, with the update log captured per serial. This adds roughly 75 logged fused transitions toward X1 under controlled conditions, and customers receive 0909 like every unfused MP unit. Their first field OTA is then the next MP release, on the same day as the unfused control group, which is what X2 requires. **Confirmed 16 Sep: CVTE's lab can reach the iFIT OTA server, so the update is applied by OTA in the lab, not by flash.** The "do not reflash to 0814" rule applies to the ring and test units only |
| Once the customer units enter the console vendor's flow they cannot be held or segregated by serial without disrupting three vendors | **The customer-release hold point is CVTE's outbound dock.** The 70 to 75 do not leave CVTE until the release decision in Section 3.4 is signed. **Confirmed 16 Sep: the console vendor captures the tablet serial at integration**, so the mapping exists; P5 requires that it reach the OTA backend and the depot so rings can be targeted by fuse state (J4) and returns routed by it |

The depot for a fielded fused unit is whoever receives returned consoles (the US service site in H1), not CVTE. Reaching the on-board download switch means opening the console and then the tablet, which fixes the answer to assumption 11: forced download is a depot operation, not a field or customer one.

**Simplified remaining set for cohort release.** Executor and location per the table above. Estimated two working days of effort, but elapsed time is set by shipment.

| # | Test | Pass | Effort | Gates |
|---|---|---|---|---|
| S1 | Open `input.xml` and `GFH_CONFIG.ini`: record `Enable_SBC`, `Enable_DAA`, `Disable_Rom_Cmd` (or `brom_magic_cmd_mode_permanent_dis`), `jtag_en`, `debug_en`. Regenerate SHA-256 of `root_pubk.der` and compare to the read-back hash | SBC true; DAA false; ROM command disable **false/0**; hash regenerated by ICON matches | 1 h | P1, G4, G7 |
| S2 | Inspect the partition list in `VKC1_20260814_20260909.zip` `payload.bin` metadata (and the 0909 full package) | **No preloader / boot0 entry.** LK, TEE and Android partitions may be present: a bad LK is refused by the fused preloader, which still offers preloader USB download, so it is depot-recoverable, not a hard brick | 1 h | E1 (by inspection, no CVTE letter needed) |
| S3 | Forced download on a **healthy** cohort unit: enclosure open, SP Flash Tool V6 armed in Download with the BROM VCOM driver installed, hold the on-board download switch, apply 12 V; log USB VID/PID seen (MediaTek BROM `0E8D:0003`, preloader `0E8D:2000`) | Enumerates and the tool connects; **do not flash** | 1 h | P2 (first half), conflict 11 |
| S4 | Depot flash of the same healthy fused unit in preloader mode with signed `DA_BR.bin` and signed 0909 | Download Ok; boots; read-back unchanged | 1 h | H1 (cohort scope) |
| S5 | Apply the 0814→0909 OTA to five cohort units. On two of them cut 12 V during payload write and during first boot of the new slot | All five on 0909; the two interrupted units fall back or resume; no brick | 1 day | X1 first transition; D2/D4 in cohort scope; P6 |
| S6 | `read-efuse` on three more randomly chosen cohort units | Same map and hash as S1 | 1 h | P1 sampling |
| Paper | P4 written: no rotation, residual risk accepted, keys removed from Basecamp. P5 backend records with fuse state. A0-b check on one unfused 0909 unit (lock state, AVB, wrong-key `vbmeta` refused) | Signed | 0.5 day | P4, P5, A0-b |

**Decision rule for the cohort.**

- **S1, S2, S4, S5, S6 and the paper items pass, S3 passes** → release the ICON-controlled ring immediately; release the customer units from CVTE's dock after S5 has passed on the ring and the customer units have taken the 0814→0909 OTA at CVTE with logs. Fused-production work continues in parallel on the full plan.
- **S1, S2, S4, S5, S6 pass, S3 fails, S1 shows ROM command disable unset** → release the ICON-controlled ring; hold customer placement for one written MediaTek answer on BROM entry with a failed preloader on a fused MT8371 (ask 15). Exposure meanwhile is bounded by S2: the OTA cannot write the preloader, so the only unrecoverable mode is boot0 storage failure.
- **S1 shows ROM command disable set** → no cohort unit to customers. The 100 stay ICON-internal as test and demonstration hardware, and the fuse image is regenerated before any further fusing. This outcome would also explain the two bricks.
- **S2 shows the preloader in OTA scope** → stop; this is a pipeline change before either the cohort or the unfused MP fleet ships.

### 3.5 Confidence framework for burning fuses on the production line

Defined before S1 to S6 execute so that the determination is read off the evidence rather than argued from it. Confidence is stated as one of four levels. Each level requires **every** item in its row; a single missing item holds the level below.

| Level | Meaning | Evidence required | Consequence |
|---|---|---|---|
| **Not ready** | A stop-ship finding is open | Any of: ROM command disable set (S1); preloader in OTA scope (S2); hash mismatch or DAA on (S1); a fused unit that neither boots nor recovers in S4 or S5 | No fusing anywhere. Cohort stays internal |
| **Low** | Fuse mechanism proven; recovery not proven | S1, S2, S4, S6 pass; S5 zero unrecoverable; S3 **failed** or not run; E5 not demonstrated | Cohort to ICON ring only. Production ships unfused. This is the level on 15 September |
| **Medium** | Recovery path exists; field behavior unmeasured at scale | All of Low, plus S3 pass on a healthy fused unit; E5 pass on a bricked fused unit; cohort in field with first OTA transition complete (X1 half); Group G key gates G3, G4, G7, G11 closed; A0-b passed on an unfused unit | Cohort to customers. Fusing of a **bounded** production lot (one lot, CVTE only) may be authorized with rings and kill switch (J1–J3) proven and the line controls L1–L8, I1–I6 witnessed |
| **High** | Fused units have survived the field | All of Medium, plus X1 (two transitions, zero unrecoverable), X2 (indistinguishable from control), X4 (two depot recoveries), G1 release-signing custody, G5, G6, G8–G10, Tier 2 at Malata | Fusing authorized for all CVTE production, then Malata |

**How the cohort results move the level.**

| Result | Effect |
|---|---|
| S3 pass | Low → eligible for Medium once E5 also passes on the bricked unit |
| S3 fail with ROM command disable unset | Stays Low; ask 15 to MediaTek becomes the blocker for Medium |
| S3 fail with ROM command disable set | Not ready |
| S5 pass | Satisfies the cohort half of X1; the second transition comes with the next MP OTA |
| S5 any unrecoverable unit | Not ready until root-caused, regardless of S3 |
| S2 shows preloader in OTA | Not ready for both configurations |

**Quantitative note.** The cohort cannot raise confidence above Medium on its own. One hundred units and two transitions bound the fused OTA brick rate near 1.5 percent at 95 percent confidence, which excludes a systematic defect but not a rare one. High is reached by process evidence (key custody, line controls, depot, rollout controls) plus the cohort, not by more cohort units.

**Reporting.** When S1 to S6 results arrive, this section is updated with the level, the evidence table filled in, and the date. The level is the answer to "how confident are we in burning fuses on the production line."

**Deferred to fused-production authorization, not required for the cohort:** Groups C×5 and D soak on fused units, M3–M8, N1–N11, G5, G6, G8–G10, L1–L8, I1–I5, H2–H5, J1–J5, Tier 2, and G1. They remain in Section 4 unchanged.

---

## 4. Authorization gates by tier

Gate identifiers are from Plan B (r0.4). **STOP-SHIP** halts the closed-configuration decision. **GATE** must pass before a later group's results are credited or before a line runs.

### Tier 0. Irreversibility gates: before any MP unit is fused, at any ODM

| ID | Gate | Pass criterion | Owner |
|---|---|---|---|
| G1 (restated r1.4) | STOP-SHIP Release signing | The MP build is signed in a release step separate from compilation, using platform and OTA keys ICON holds. `ro.build.tags` reads `release-keys` as a consequence. The tag alone is neither necessary nor sufficient: on 0909 it reads `dev-keys` while every certificate is ICON's | CVTE (pipeline), ICON (keys) |
| G2 | STOP-SHIP Certificate chain | `otacert`, `platform.x509.pem` and the AVB image key all resolve to the ICON certificate; none matches an AOSP test key. **Closed on 0909** (SHA-256 `61:7C:CC:...:1B:BF`, O = Icon Health and Fitness). Repeat on any re-signed artifact | ICON |
| G3 | STOP-SHIP Key custody | ICON holds or escrows root, img and DA private keys in an HSM or restricted escrow; keys removed from Basecamp; custody documented; decision on rotation recorded | ICON |
| G4 | STOP-SHIP Fuse hash | ICON independently regenerates `sbc_pub_key_hash` from the public key and matches it to read-back from a fused unit | ICON |
| G5 | STOP-SHIP Leak response | Tabletop for signing-key leak after MP; limits accepted in writing because OTP cannot be re-keyed | ICON security |
| G6 | STOP-SHIP ODM signing process | Who signs, with which key, under what approval, how a rogue ODM build is detected. **r1.13: a validly signed secure-boot-disable preloader exists and boots on a fused unit (Source I). Inventory every copy, treat it as key material under G3, and never sign a permissive preloader with the production root key again** | CVTE, Malata, ICON |
| G7 | STOP-SHIP Fuse map | Read back from an MP-process unit and from the burned first articles: only SBC set. DAA, JTAG-disable, PTSB **and `Disable_Rom_Cmd` / `brom_magic_cmd_mode_permanent_dis`** unblown. Cross-check against `input.xml` and the GFH config used to build `efuse_iFitG520.img`. A set `Disable_Rom_Cmd` bit removes every USB recovery path and blocks fusing outright | CVTE, ICON |
| E2 (rescoped) | Characterization | Corrupt `preloader_a` on a fused unit and on an open unit. Record whether BROM tries the second copy on eMMC. Source F documents second-copy fallback for NAND only, so a fail here is information, not a defect | Test lead, MediaTek written answer |
| G8 | STOP-SHIP Host-side only | Written CVTE and MediaTek confirmation that no runtime, bootloader or TEE path can program SBC, DAA, JTAG or PTSB | CVTE, MediaTek |
| G9 | STOP-SHIP Userspace write attempt | On a non-fused sacrificial unit, every attempt (factory app, init service, adb, privileged app, fastboot, recovery) fails; fuse state unchanged | Test lead |
| G10 | STOP-SHIP Build audit | No efuse images, write scripts, DA binaries, private keys or factory-test fuse check in the shipping user build | CVTE, audited by ICON |
| G11 | STOP-SHIP DA authentication posture | Signed decision on the intended shipping state of the download path (R17). Under no circumstances is the DAA fuse blown in the same pass as SBC | ICON |
| E1 | STOP-SHIP OTA partition scope | Written CVTE confirmation that preloader, boot0, DA, TEE and SCP/DSP are never in an OTA payload, and the release pipeline enforces the exclusion. **r1.13: verified two ways, by the `payload.bin` partition list (S2) and by `AB_OTA_PARTITIONS` in the board configuration, which controls whether the OTA builder can emit a preloader image at all. Vendor-freeze BSPs normally exclude it; confirm, do not assume** | CVTE |
| E5 | STOP-SHIP BROM recovery | J26080143-0A00076 and one freshly bricked fused unit recover via forced download and boot a signed build | Test lead, CVTE |
| C, D | STOP-SHIP Zero unrecoverable | Groups C and D complete on fused units including the 200-cycle soak with zero unrecoverable units | Test lead |
| M3–M8 | GATE Configuration | Merge mechanism identified; verity error mode behavioral (M5); slot metadata survives interruption; factory reset refused during merge | Test lead |
| N1, N2, N10 | GATE Prerequisites | Boot-control HAL and snapshot suites conform; fused userdebug build signed with release keys is available so fused-vs-open comparison is executable | CVTE, test lead |
| N3 | STOP-SHIP Attestation | Key attestation on a fused, locked, release-signed unit reports verified and locked against the burned hash | Test lead |
| N11 | STOP-SHIP GSI window | Written confirmation nobody downstream relies on generic-system-image evidence, which ends permanently at fusing | ICON |
| **A0 (new)** | Baseline | Read `MTK_SEC_BOOT` and `MTK_SEC_USBDL` from the 0909 preloader project configuration and `sboot_state` from the preloader console. Then on an open 0909 unit flash a wrong-key LK and a wrong-key `vbmeta`; record halt, warning or boot. Result settles Section 1.1 conflict 9 | CVTE (config), test lead (behavior) |
| **A0-b (new)** | STOP-SHIP for open units under Option A | Any unit shipped unfused must carry a preloader built with `ATTR_SBOOT_ENABLE`, verified by A0 on the shipping build. An unfused unit built with `ONLY_ENABLE_ON_SCHIP` has no boot-chain signature enforcement at all | CVTE, ICON |
| **K0 (new)** | STOP-SHIP Key freeze | Root, image and DA keys are frozen before the first unit ships under either option. Rotation after shipment requires a preloader update, which E1 excludes from OTA. Recorded as a signed decision alongside G3 | ICON |

### Tier 1. CVTE production-line authorization

| ID | Gate | Pass criterion |
|---|---|---|
| L1 | Ten open sacrificial units through the SOP as written; per-serial console trace, chip ID, random ID, DA authentication state archived | All reach completion message |
| L2 GATE | Interrupt fuse write at the 12 V step and mid-transfer, five units each | Each unit is unfused-and-rerunnable or fused-and-flashable; none unfused-but-passed, none partial |
| L3 GATE | Attempt to flash production firmware to a unit whose fuse write failed or never ran | Station refuses and quarantines; ordering enforced by tooling |
| L4 GATE | DA authentication state recorded on every unit; shipping posture decision on file | Matches G11 |
| L5 GATE | Fuse image is the ICON-approved artifact, hash-matched to the G4 key; authoritative build label for fuse image and firmware resolved in writing | Hash match per serial |
| L6 | Re-run fuse write on an already-fused unit | Idempotent or cleanly refused; never a changed hash |
| L7 | Station pinned: flashing tool version, DA, USB drivers, image package | Versions frozen and change-controlled |
| L8 | Time-and-motion including driver-install fallback | Cycle time known; no line pressure toward shortcuts |
| I1 | ICON witnesses a live scripted run | No manual key entry; step cannot be skipped |
| I2 | Advance an unfused unit through factory test | Hard stop |
| I3 | Per-serial fuse write and read-back exported | Auditable by ICON |
| I4 | Power loss or cable pull at the station mid-write | Detected by read-back; quarantined |
| I5 | Yield and scrap over a 500-unit run | Scrap rate accepted in writing before MP release |
| I6 (new r1.4) | Factory test has an unfused mode for the next batch: reads and logs eFuse state per serial, does not require `sbc_en`. The fused-required mode is re-enabled only by the written fusing authorization | Every unfused MP unit carries a factory-test record proving it is unfused; the two modes cannot be selected by an operator |
| Note | CVTE's 12 Sep message describes the line tool: worker opens the tool, selects `flash.xml`, the tool writes `efuse.img`, powers on, enters factory test, and stores a log per run; `DA_BR.bin` and firmware are signed at compile time and firmware generation is gated on a hash match against `efuse_iFitG520.img`. This is the evidence base for L1, L3, I1 and I3, to be witnessed rather than accepted on description. The earlier SOP was an R&D guide, not the line procedure | |
| H1 GATE | Depot re-flash of a fused unit with signed DA and signed build at CVTE and at the US service site, using a **full-image** profile and not only the boot-chain profile (R19) | Succeeds at both; time and cost recorded |
| H2–H5 | Recovery/fastbootd reachable and sideload works; factory reset from corrupt userdata recovers; signed-DA custody documented; field-service decision tree validated on real failed units | All pass |

### Tier 2. Malata production-line authorization

Malata has no fuse-station history on this program. Tier 2 is a transfer, not a re-derivation.

| Requirement | Pass criterion |
|---|---|
| Transfer package from CVTE | Same fuse image (hash verified by ICON), same pinned tool, DA, driver and package versions (L7), same scripted station and interlock, same factory-test gate |
| No key material transferred outside controlled channels | Signed DA and any signing artifacts delivered per H4; nothing via project tools or email |
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
| F1 on 0909 | Signed older build flashes and boots on a fused unit: the fleet escape hatch is proven on the shipping build |

Until Tier 3 passes, fused units in the field receive no OTA. This is the control that makes Option B tolerable and it costs nothing under Option A.

---

## 5. Consolidated test plan

Test content is Plan B groups A–N with Plan A's glitch matrix mapped in. Only additions and changes to Plan B r0.4 are listed here; unchanged cases are referenced by ID.

### 5.1 Sample matrix

| Group | Qty | Configuration | Use |
|---|---|---|---|
| OPEN-1..5 | 5 | Not fused, 0909 | Control; every destructive case rehearsed here first; 1,000-iteration automated glitch matrix; A0 baseline |
| CLOSED-1..2 | 2 | Fused | Sacrificial: preloader and boot-chain negative tests (E2–E4, E6). Assume total loss |
| CLOSED-3..4 | 2 | Fused | C group ×5, D soak, M5 verity, depot rehearsal |
| CLOSED-5 | 1 | Fused | Golden reference; never negative-tested; fuse read-back and performance baseline |
| CLOSED-6..7 (added) | 2 | Fused | Spares for the 200-cycle soak and for the fresh brick required by E5 |
| BRICK-1 | 1 | Fused, unbootable | J26080143-0A00076, E5 acceptance vehicle |
| USERDEBUG-F (added) | 1 | Fused, userdebug signed with release keys | Required by N10 for VTS on a fused unit; is itself a key-custody request |
| COHORT (r1.3, firmware confirmed r1.8) | 100 total, 7 of which are CLOSED-1..7 above | Fused by CVTE on 30 July; on VKC1_20260814 user build; 0814→0909 OTA package available | Section 3.3: 15 to 20 ICON-controlled field units, roughly 70 to 75 customer units after preconditions P1 to P6 |
| CONTROL (r1.3) | ≥ customer cohort size, preferably 10× | Unfused MP units, `ATTR_SBOOT_ENABLE` preloader | Same OTA transitions and telemetry as the cohort; the comparison population for X2 |

### 5.2 Additions and changes to Plan B r0.4

| ID | Change | Reason |
|---|---|---|
| A0 (new) | Read preloader security flags and `sboot_state`; wrong-key LK and wrong-key `vbmeta` on an open 0909 unit | Source E shows enforcement depends on the build flag. Settles whether the brief's premise holds and whether open lot 1 units under Option A enforce anything |
| A0-b, K0 (new) | Open units must be `ATTR_SBOOT_ENABLE`; keys frozen before first shipment | Source E section 5.2 brick mode (LK re-keyed without preloader) is unrecoverable by OTA on Cesium in either configuration |
| E2, E3 | Rescoped to characterization. Add the open-unit control: corrupt `preloader_a` on an OPEN unit and record whether BROM download mode enumerates and whether the second copy is tried | Source F documents second-copy fallback for NAND only; Cesium is eMMC. Source E predicts a soft brick on open units and a halt on fused units. The open case proves the preloader mode is new with fusing rather than pre-existing |
| E5 | Add: run the forced-download button sequence first on CLOSED-5 (healthy fused unit) and confirm BROM enumerates before trying it on BRICK-1 | Separates "the bricked unit is unreachable" from "BROM command mode is fused off on every unit" (conflict 11) |
| G7 | Add `Disable_Rom_Cmd`, `jtag_en`, `debug_en` to the read-back and to the `input.xml` audit | Source F section 7 and 5.4 |
| A7 (new) | OTA client behavior with the wall clock at build time (no RTC): TLS validation of the OTA endpoint, package timestamp checks, before NTP sync | Source D shows every cold boot starts at build time. An OTA that fails or a certificate rejected as not-yet-valid is a field-visible failure mode independent of fusing but exposed by any OTA plan |
| N6 emphasis | Health HAL on a battery-less unit reports a sane state; `update_engine` minimum-battery policy verified | Tool reports `battery_voltage 0`; an update client that refuses to start, or starts when it should not, is plausible |
| D8 | Brown-out via programmable DC source sweep, not only clean cut | A sagging console supply is more likely than an instant drop |
| E5 | Add: document the exact button, hold timing, tool version, and whether it is reachable without opening the enclosure | Defines hard versus soft brick for this product (Section 4.3 of Plan B) |
| F1 | Must be run on the exact 0909 artifact that ships, and repeated if it is re-signed | Fleet escape hatch must be proven on the shipping artifact |
| J4 | Add fuse state to fleet telemetry | Mixed fleet under Option A; OTA freeze under Option B; depot routing |
| K1 | Pilot sites are ICON-controlled (offices, employee homes, test gyms), not customers | Zero fused customer units until soak completes |
| Glitch matrix | PWR-01..04 and USR-01 run at 1,000 iterations on open units; 200 randomized on fused; AVB-01 rescoped to F2 | Reconciles Source A and B criteria; anti-rollback unavailable |
| Re-test set | G2, G4, N3, B1, B2, C3, C5, D2, D4, F1, M5 repeated on 0909 only if it is re-signed (G1 release step or K0 key decision) | Any re-sign invalidates hash-dependent results; no new build is expected |

### 5.3 Instrumentation and records

Per Plan B 4.2, plus: per-serial fuse state in the backend, programmable DC source logs correlated to `update_engine` phase, and the exact SP Flash Tool, DA and driver versions frozen at L7 recorded in every test artifact.

---

## 6. Production plan

### 6.1 Line sequence (both ODMs)

1. Board in BROM/preloader download mode over mini-USB, 12 V applied only after `write-efuse` is issued (SOP order).
2. Station script writes `efuse_iFitG520.img`; `CMD:WRITE-EFUSE command execute successed` logged against serial.
3. Read-back: `sbc_en` set, `sbc_pub_key_hash` equals the ICON-approved hash; DAA, JTAG, PTSB unblown. Any other outcome quarantines the unit; the station will not proceed.
4. Signed production firmware flashed; `Download Ok` logged against serial.
5. Factory-test application hard-gates on fuse status. A unit with the wrong state cannot progress.
6. Per-serial record exported to ICON: serial, station, fuse read-back, fingerprint, slot suffix, factory-test pass.
7. Under Option A, fused and unfused units carry distinguishable labeling and the backend records fuse state per serial. Depot and RMA route by that field.

### 6.2 Depot and RMA

- Two proven sites before the first fused lot (H1): one at the ODM, one in the US.
- Full-image recovery profile validated, not only the boot-chain profile in the SOP (R19).
- Signed DA custody documented and distributed only through controlled channels (H4).
- Spare-board inventory must be fuse-state matched to the units it repairs.
- Field-service decision tree published: symptom, recovery action, escalation (H5).

### 6.3 Financial model (r1.6)

**Program assumptions.** 100,000 tablets in the field. $170 per tablet. Fleet value at risk $17.0M. Placeholders, to be replaced when known: depot recovery including two-way shipping $50 per unit; field replacement logistics $50 on top of the tablet; boot0 storage corruption 0.05 percent per year; fuse-station scrap 0.1 percent (the 100-unit trial had zero; I5 measures it over 500).

Fusing does not change the OTA failure probability. It changes the recovery cost per incident, adds one brick mode, and adds one unbounded tail. Term by term:

| Exposure term | Software RoT (unfused) | Hardware RoT (fused) | Delta from fusing |
|---|---|---|---|
| A/B OTA failure: payload rejected or slot falls back | Recovers in place. $0 | Same | **$0** |
| Bad OTA reaching a ring before automatic halt: 0.1 / 1 / 10 percent | 100 / 1,000 / 10,000 units affected. If depot-recoverable: $5k / $50k / $500k. If not: $22k / $220k / $2.2M | Same unit counts | $0 if recoverable; otherwise see next row |
| Boot-chain brick (preloader, or vbmeta chain failure with no fallback) | Soft brick. USB re-flash at depot, about $50 | Hard brick unless E5 works. Replacement $170 plus $50 logistics | **About $170 more per incident.** Occurs only if OTA writes the preloader (excluded by E1) or storage corrupts boot0 |
| Storage failure in boot0 at 0.05 percent per year | 50 units, about $2,500 per year | 50 units, about $11,000 per year | About $8,500 per year |
| Systematic key or fuse-image error (wrong hash, key mismatch) | Not applicable: re-flash | **Revised r1.13.** A wrong hash cannot pass the factory boot test: the unit does not boot after the burn and never leaves the station. Exposure is the units fused between the error and detection, a station batch of tens, about **$3,000 to $10,000**, not the fleet. The 100-unit trial booting 100 of 100 is itself this test passed | Bounded by the factory boot test, not by cohort size |
| Leaked root private key | Re-sign and re-flash preloaders at depot (impractical at fleet scale, but possible) | Cannot be rotated on fused units. Security incident, not a brick: units keep booting | **Fleet-wide security exposure, zero RMA cost.** This is the true unbounded term and it is controlled by G3, G5, G6 custody, not by testing |
| Depot mis-flash of a preloader (conflict 12) | Recoverable by re-flash | Hard brick; unit scrapped | One tablet per depot error. Controlled by a depot profile that excludes boot0 (R19) |
| Fuse station scrap at 0.1 percent | $0 | 100 units per 100k built, $17,000 | $17,000 per 100k |
| Depot tooling: signed DA custody, pinned tool, two sites | Existing depot | One-off setup, low tens of thousands | Fixed, small |
| Key custody: HSM or escrow, release-signing step | Required anyway for G1 | Same | $0 delta |
| Line cycle time for the fuse step | $0 | L8 measures it; CVTE's scripted tool makes it a single operator action | Small per unit |

**Reading the table.**

- The largest term, a bad OTA reaching a large ring, is the same on both configurations and is bounded only by staged rollout (J2) and the kill switch (J3). Neither the fuse nor the cohort changes it. This is where iFIT's stated fear of "unforeseen OTA issues" actually lives, and Group J is the control.
- Fusing adds roughly one tablet's cost per boot-chain brick. With the preloader excluded from OTA, boot-chain bricks come only from storage failure and are rare. Over a year on 100k units this is in the low tens of thousands of dollars, provided E5 works.
- **Revised r1.13.** Because most Cesium tablets cannot be disassembled for flashing in the field, a non-booting tablet is a field replacement in both configurations. Fusing does not change the field RMA count. It changes depot outcome: a fused unit with a bad preloader is scrap rather than refurbished. The added cost is the refurbishment value of a tablet per boot0 failure, roughly $6,000 per year at the 0.05 percent placeholder, $60,000 at ten times that. If BootROM recovery (E5 or the eMMC test point) is demonstrated, the delta is zero.
- The systematic fuse-error tail is bounded by the factory boot test at a station batch, not the fleet. The fleet-wide tail that remains is a leaked root key, which is a security exposure with no RMA cost and is controlled by custody, not testing.
- E5 and the ROM command bit remain stop-ship for a different reason than "unbounded RMA": without a demonstrated recovery path, every depot preloader error and every boot0 failure is permanent, and the program has no proven way to rework any fused unit whose boot chain is damaged.

**Not quantified here.** The security value of hardware RoT for a kiosk console (physical re-flash, OS replacement, content protection, EN 18031 evidence). The true cost of a field replacement on an installed console, which likely exceeds the $50 placeholder. The MP OTA cadence, which sets how many times per year the ring cap is tested.

**Unsigned boot is not a program option.** All testing has run on software root of trust and the 2 October MP date does not permit a configuration change. The unsigned column in Section 2.1 is a reference from Source E only.

---

## 7. Background assumptions that are missing or unstated

These are needed either to run the plan or to make the Option A / B decision. None of them is answered in the three sources.

**Commercial and compliance**

1. **Partly closed r1.6**: 100,000 tablets in the field at $170 per tablet. Still needed: the true cost of a field replacement on an installed console (service call, shipping, swap), the depot recovery cost per unit, warranty terms, and the planned OTA cadence. Section 6.3 uses $50 placeholders for the first two.
2. Whether Cesium ships into the EU and whether the EN 18031 assessment accepts a software root of trust. Xenon passed NIST 8259 with software RoT. If the compliance body requires hardware RoT, Option A's "permanently open lot 1" has a compliance cost, not only a security-posture cost.
3. The threat model the fuse is meant to close. For a kiosk fitness console, physical-access OS replacement, content and DRM, and brand protection are different threats. Remote threats are already covered by signed OTA on the open configuration. This decides whether shipping any unit unfused is acceptable.
4. Who signs the fuse authorization for CVTE and for Malata, and whether the MP line can start unfused and switch to fused mid-lot. If it can, the "three weeks" deadline applies to the line start and not to the fusing decision, which relieves the schedule considerably.

**Keys and artifacts**

5. Whether the private keys posted to Basecamp are the production keys, whether ICON has an HSM or escrow available now, and whether the ODMs will accept a key rotation and `efuse_iFitG520.img` regeneration inside the schedule.
6. Whether a fused userdebug build signed with release keys will be produced (N10). Without it, VTS on a fused unit and the fused-versus-open comparison cannot run.
7. Whether Cesium licenses Google Mobile Services. This determines whether GTS applies and which suites are available (Plan B Group N).
8. Which build label is authoritative for the fuse image and firmware (VKC1_20260727 versus 20260729 ambiguity) and who signs off the pairing (L5).

**Platform behavior**

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
19. Which preloader security flag the 0909 build carries (`ATTR_SBOOT_ENABLE` versus `ATTR_SBOOT_ONLY_ENABLE_ON_SCHIP`), and whether `MTK_SEC_USBDL` is set. Everything the brief assumes about "software root of trust already enforcing signatures" rests on this one makefile line, and the Basecamp record is consistent with either answer at different dates.
20. **Partly answered 12 Sep.** CVTE's description of compile-time signing with a hash gate against `efuse_iFitG520.img` "and the private key" places the MediaTek root key on CVTE's build system, and the `dev-keys` tag places the Android platform keys there too. The remaining question is whether ICON holds independent copies of each, and whether both key families move into the separate release-signing step requested in item 12 of the consolidated ask. Whether the ICON platform keys that sign the Android OTA and the MediaTek boot-chain keys (`root_prvk.pem`, `img_prvk.pem`, `da_prvk.pem`, `epp_prvk.pem`) are managed as one custody problem or two. Source F section 5 and 6 show the root public key is compiled into the preloader, the DA and LK, so a root rotation rebuilds all three; G3 must name a holder for each key, and K0 freezes all of them.
21. What `efuse_iFitG520.img` actually encodes. Source F section 7 lists `Enable_SBC`, `Enable_DAA` and `Disable_Rom_Cmd` as the three `input.xml` switches, and the preloader GFH config carries `brom_magic_cmd_mode_permanent_dis`, `jtag_en` and `debug_en`. No source in this set states the values CVTE used. The plan has been assuming SBC only; that is unverified until the XML and a read-back are on file.
22. Whether BROM on MT8371 with eMMC ever falls back to the second preloader copy. Source F documents the fallback for NAND. If eMMC has none, the product has no preloader redundancy in either configuration and `preloader_b` is inert.
23. The state of the 100 fused units: which firmware they carry, whether their serials and per-serial fuse read-backs from the factory-test check are already in ICON's hands, whether any have already been shipped or committed to customers, and whether they run the production OTA client and telemetry agent. P1 to P6 assume they are still at CVTE or ICON.
24. Whether "sufficient test data" has an agreed definition. Section 3.3 proposes X1 to X7; without a signed definition the cohort period has no end and every MP lot ships unfused by default.
25. Whether the OTA backend can target rings by fuse state and can hold a cohort-first ring ahead of the control group. Without that, the cohort cannot be made the first ring, and the control comparison cannot be run on the same transitions.
26. **Added r1.12, closed 16 Sep.** The console vendor captures the tablet serial at integration, so the tablet-to-console mapping exists and P5 (backend records with fuse state per serial) is achievable; what remains is confirming the mapping reaches the OTA backend and the depot. CVTE's lab can reach the iFIT OTA server, so the customer cohort units take the 0814→0909 update by OTA at CVTE, not by depot flash; the fallback is withdrawn. Note the OTA runs in CVTE's lab, not on the production floor, so the 70 to 75 units move lab-side for the update and return to the dock hold.

---

## 8. Open questions to CVTE, Malata and MediaTek

Plan B section 7 questions 1–16 are carried forward unchanged and should be sent as one letter on Day 1, quoting both chip designators (MT8371 / Genio 520 and MT8189 as the tool reports it). Add:

17. Can the MP line run unfused and switch to fused mid-lot without re-qualification, and what changes on the station when it does?
18. Will CVTE and Malata accept a key rotation and a regenerated fuse image before their first fused lot, and what is the lead time?
19. What is the per-unit depot cost and turnaround for a fused unit at each ODM's service path, and does either require an additional auth file or certificate for secure download?
20. To CVTE: provide the `input.xml` and preloader GFH configuration used to generate `efuse_iFitG520.img`, with the values of `Enable_SBC`, `Enable_DAA`, `Disable_Rom_Cmd`, `brom_magic_cmd_mode_permanent_dis`, `jtag_en` and `debug_en`, and a read-back from a first-article unit showing the same.
21. To MediaTek: does BROM on MT8371 attempt the second preloader copy (eMMC boot1) when boot0 fails to load or fails authentication? The Secure Boot Developer Guide V1.1 section 3.1 documents this for NAND only.
22. To CVTE: which `MTK_SEC_BOOT` and `MTK_SEC_USBDL` values are set in the VKC1_20260909 preloader project makefile?

**Consolidated ask to CVTE, 12 September 2026**, accompanying ICON's decision not to fuse the next batch. Numbered as sent; answers pending.

| Sent item | Content | Plan reference |
|---|---|---|
| 1 | Healthy fused unit: enter BROM download mode by button-and-power sequence; show USB enumeration and SP Flash Tool connection; do not flash | P2, C2, conflict 11 |
| 2 | J26080143-0A00076: same entry, flash signed 0909 with signed `DA_BR.bin`, boot to Android, fuse read-back unchanged | E5 |
| 3 | Written procedure: button, hold time, power timing, tool and driver versions | E5, H5 |
| 4 | `input.xml` and GFH config for `efuse_iFitG520.img` with `Enable_SBC`, `Enable_DAA`, `Disable_Rom_Cmd`, `brom_magic_cmd_mode_permanent_dis`, `jtag_en`, `debug_en`; read-back logs for all 100 | P1, G7, question 20 |
| 5 | Root public key for independent hash regeneration | G4, C4 |
| 6 | Unfused batch preloader flags: confirm `ATTR_SBOOT_ENABLE` / `ATTR_SUSBDL_ENABLE`, or state if `ONLY_ENABLE_ON_SCHIP` | A0, A0-b, question 22 |
| 7 | Factory test accepts unfused units and still logs eFuse state per serial | I6 |
| 8 | Same root, image, DA and platform keys for cohort and unfused batch | P6, C8 |
| 9 | Signed `DA_BR.bin`, signed 0909, pinned tool and driver versions, depot procedure with full-image profile | H1, H4, R19, C5 |
| 10 | Firmware currently on the 100; confirm 0909 OTA applies | P6, K2, C6 |
| 11 | Release seven of the 100 to ICON for destructive testing | Sample matrix, C7 |
| 12 | Build produced as `release-keys` through a signing step separate from compilation; custody discussed separately | G1 |

**Answers received 14 Sep (Source H)**: items 4, 5, 8, 9, 10 answered with artifacts; item 6 half-answered (`MTK_SEC_USBDL` only); item 7 answered in principle; items 1 to 3 answered as an instruction, not a demonstration, and the instruction failed at ICON; item 11 is a schedule objection, answered in Section 3.4; item 12 deferred to the dev-keys analysis. Status per item is in Section 3.4.

**New asks to CVTE and MediaTek (15 Sep):**

13. To CVTE: the `MTK_SEC_BOOT` value for 0909 (item 6 answered only `MTK_SEC_USBDL`), and the LK lock state shipped on unfused units (`ro.boot.flash.locked`, fastboot unlock policy).
14. To CVTE: for the photographed on-board download switch, is there any external key sequence on the assembled console that reaches the same signal, or does forced download always require opening the enclosure? This defines hard versus soft brick for a field unit (assumption 11).
15. To CVTE and MediaTek: on a fused MT8371 with `SBC_EN` set and BROM command mode enabled, when the preloader fails authentication does BROM enter USB download mode and enumerate as `0E8D:0003`? For how long, and is the download key required? ICON observed no enumeration in 120 seconds on a unit with a deliberately bad bootloader signature.
16. To CVTE: which stage did MediaTek's "forced flashing" instruction target, BROM or preloader? The download key is polled by the preloader; if the preloader is the corrupted stage, the instruction cannot apply.
17. To CVTE: confirm the factory-test configuration profile for the unfused batch is version-controlled and not operator-selectable, and that it logs eFuse state per serial (I6).
18. To CVTE, in reply to item 11: production is not waiting on test results. The MP batch ships unfused per the 12 Sep decision. Only customer release of the 100 fused units waits, on the two-day set in Section 3.4.

**New asks (16 Sep, r1.13):**

24. To CVTE: the board-level procedure to force BootROM download mode when the preloader fails authentication and no USB appears. Specifically, the eMMC test point (data or clock line) to short at power-on so BootROM sees no preloader rather than a bad one, its location on C.G520.702, and whether this is the fixture method CVTE would use for a returned unit.
25. To CVTE: which stage performs the "preloader-level check of the firmware signature against the eFuse key before flashing" described in August. SP Flash Tool wrote a preloader with a corrupted RSA signature to boot0 of a fused unit and reported success (Source I).
26. To CVTE: inventory of every signed secure-boot-disable preloader binary for iFitG520, who holds copies, and confirmation that no further permissive preloader will be signed with the production root key.
27. To CVTE: the `AB_OTA_PARTITIONS` list from the 0909 board configuration, and confirmation of whether the Cesium Android 15 BSP is a vendor-freeze release.
28. To CVTE: whether `OTP_FRAMEWORK_v2` is enabled in the Cesium LK, and the current values of the AVB and Recovery OTP group counters on a fused unit (expected 0). Harmless today; decides Recovery-slot behavior if the AVB rollback index is ever raised (Section 2.5).

**Carried from the dev-keys analysis, not a blocker:**

28. Confirm the 39 APKs on 0909 not signed with the ICON platform certificate are all expected third-party or vendor apps, and none is an ICON component that should carry the platform certificate but does not.

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

## 10. Revision history

Newest first. Each entry records what changed and the evidence that drove it.

**Changes in revision 1.14 (16 September).** Editorial and one clarification. Revision history moved from the front of the document to this section. Color badges added for STOP-SHIP, GATE, ACTION and CLOSED items and for the four confidence levels, with a legend after the header table. Section 2.5 added: anti-rollback clarified as two layers (MediaTek bootloader ARB across Secure and Non-Secure OTP groups, and AVB 2.0 rollback index in `vbmeta` checked by LK against the AVB OTP group), how they interact with A/B slot fallback, and Cesium's state in each (Level 1 disabled, Level 2 present with index 0 and therefore inert). Section 2.4 and test plan S5 unit 4b and S7 from the previous push are recorded here as part of 1.13.

**Changes in revision 1.13 (16 September).** Source I, Shane Andrus's G520 eFuse Burn Log, ingested. It establishes that the bricked unit is the first article J26080143-0A00076, fused by ICON on 8 September (userdebug VKC1_20260907, bootloader unlocked, orange), not a cohort unit; that the corruption was 32 flipped bytes inside the preloader's RSA signature with the code intact, written to boot0 only; and that every recovery attempt including CVTE's download-key instruction produced no USB enumeration while a control unit enumerates on the same setup. Section 2.3 added: the brick is a pure demonstration of the one failure mode fusing adds, but a signature-only corruption has no natural field cause, and since most Cesium tablets cannot be disassembled for flashing, fusing does not change the field RMA count, only depot refurbishability. Section 6.3 revised accordingly: the systematic-error tail is bounded by the factory boot test, not the fleet. Two new findings: SP Flash Tool wrote a mis-signed preloader to a fused unit without refusal (conflict 12, depot hazard), and a validly signed secure-boot-disable preloader exists and boots on a fused unit (G6 extended). Vendor-freeze background on preloader OTA scope recorded; `AB_OTA_PARTITIONS` check added to S2 and E1. Next recovery step: eMMC test point (ask 24).

**Changes in revision 1.12 (16 September).** Manufacturing flow corrected: production tablets go ODM → console vendor → finished-goods vendor → warehouse or store, never to Logan, and are not powered until a customer sets them up. Three changes follow. The ring and test units are an exception shipment ICON must arrange. The 70 to 75 customer cohort units receive the 0814→0909 OTA at CVTE, logged per serial, before entering the console flow, so customers receive 0909 and the cohort's first field OTA coincides with the control group's; the "do not reflash" rule now applies to the ring and test units only. The customer-release hold point is CVTE's outbound dock, and the console vendor must record tablet serial against console serial or fuse-state targeting and depot routing are impossible inside a finished console. Assumption 26 added.

**Changes in revision 1.11 (16 September).** Correction of unit geography. The 100 fused units are at CVTE; ICON holds the bricked unit and at most two others. Section 3.4 now assigns each of S1 to S6 an executor and location: S1, S2 at ICON; S3, S4 and S6 at CVTE with video and logs as evidence; S5 at ICON after the ring units ship. CVTE is asked to ship the 15 to 20 ring units and the 7 test units now, on 0814. Elapsed time to the ring release is set by transit, about one week, not by test effort. The standalone test plan header is corrected to match.

**Changes in revision 1.10 (16 September).** CVTE (Simon Huang) supplied the `efuse_iFitG520.img` build log of 27 July 2026: `EFUSE_Enable_SBC = 1`, `EFUSE_Enable_DAA = 0`, `EFUSE_Enable_SLA = 0`, **`EFUSE_Disable_BROM_CMD = 0`**, `EFUSE_Disable_DBGPORT_LOCK = 0`, `EFUSE_USB_download_type = 0`; `brom_magic_cmd_mode_permanent_dis` is not present in the project; configuration is MediaTek default. This closes the S1 ROM-command-disable question by build evidence (the read-back leg remains with ICON) and eliminates conflict 11's first hypothesis. The no-enumeration brick is therefore BootROM behavior on a failed preloader authentication, or an entry-procedure or hardware-path issue, and MediaTek's answer (ask 15, raised by CVTE) decides which. CVTE also confirmed Simon's engineering analysis: download-key detection and the flashing USB handshake both run inside the preloader, so a preloader that fails BROM authentication leaves no preloader-level recovery; CVTE will reproduce ICON's brick on its own fused unit once Shane supplies the method, and attempt BROM recovery per MediaTek's answer. The active decision branch is "S3 fail with ROM command disable unset": ICON ring may be released once S2, S4, S5, S6 and the paper items pass; customer release waits for MediaTek. Confidence level: **Low** (unchanged). The 27 July build-log timestamp also resolves the L5 label question: the fuse image belongs to the 0727 build set.

**Changes in revision 1.9 (15 September).** Section 3.5 added: a four-level confidence framework (Not ready, Low, Medium, High) for burning fuses on the production line, with the evidence each level requires and the effect of each S1 to S6 outcome. Defined before test execution so the determination is read from evidence rather than fitted to it. Current level: **Low**. The standalone test plan `Cesium_Cohort_Release_Test_Plan_S1-S6` is issued alongside. Spelling converted to American throughout.

**Changes in revision 1.8 (15 September).** CVTE answered the 12-item ask (Source H) and ICON ran the first fused-unit verification. Results: the hardware root of trust is confirmed on a cohort unit by eFuse read-back, eFuse-region diff against an unfused sister and a passing preloader signature check (G4 closed, G7 closed except the BROM command-disable bit, P1 largely closed). Anti-rollback is confirmed off with AVB rollback index 0 (conflict 1 closed, Group F reduced to F1 and F2). Keys unchanged since 27 July; cohort on the 0814 user build; a 0814-to-0909 OTA package exists (C6, C8 closed). **Forced BROM download failed** on the deliberately bricked unit: no USB enumeration in 120 seconds with the download key held (E5 and P2 open, now the single decisive item). CVTE states `MTK_SEC_USBDL = ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP`; `MTK_SEC_BOOT` still unstated. New Section 3.4 separates what the **cohort shipment** needs (a two-day set, S1 to S6) from what **fused production** needs (the rest of the plan), which is the simplification this revision is for. CVTE's item 11 ("production won't be able to keep up") is answered: production is not waiting on any test; it ships unfused. Open asks 13 to 18 added.

**Changes in revision 1.7.** Record correction: the five-item reply described in revisions 1.4 to 1.6 had not been sent. It is replaced by a single consolidated 12-item ask to CVTE on 12 September (Section 8), which adds the forced-download demonstration, the root public key, depot artifacts, cohort firmware version and release of seven units for testing. Section 3.3 deliverables C1 to C10 now map to the numbered items of that message.

**Changes in revision 1.6.** Financial model in Section 6.3 populated with the program assumptions of 100,000 tablets in the field at $170 per tablet; the hardware-RoT premium is itemized term by term. Section 3.3 gains a CVTE deliverables checklist for releasing the 100-unit cohort, including the forced-download demonstration (P2, E5) that was not among the five items sent on 12 Sep. Section 2.1 records that the unsigned configuration is reference only and not a program option: all testing to date has run on software root of trust and the 2 October MP date does not permit a configuration change. Assumption 1 partly closed.

**Changes in revision 1.5.** Correction: there is no VKC1_20260919 build. VKC1_20260909 is the last OS build and the MP release candidate. The 0919 label was inherited from Source B's header and has been removed throughout. Consequences: the Day 19 "re-test on final build" reserve becomes conditional, triggered only if 0909 is re-signed by the G1 release-signing step or a K0 key decision; the schedule no longer has a build-arrival dependency; and the fused cohort's upgrade from its 30 July firmware to 0909 is its first counted OTA transition under Section 3.3.

**Changes in revision 1.4.** Three inputs from 12 September. (a) The 0909 fingerprint is confirmed as `iFit_Embedded/iFitG520/Cesium:VanillaIceCream/AP3A.240905.015.A2/VKC1_20260909:user/dev-keys`, and a separate analysis with CVTE certificate evidence reclassifies the tag from blocker to build hygiene: the OTA certificate, `platform.x509.pem` and the payload signature all carry the ICON certificate (O = Icon Health and Fitness, CN = ifit.com), not an AOSP test key. G1 is restated accordingly: the gate is a release-signing step separate from compilation with keys ICON holds; the tag is fixed as a side effect. (b) CVTE's message of the same day describes a production-line scripted fuse tool with per-unit logs, a build pipeline that signs `DA_BR.bin` and firmware at compile time and gates firmware generation on a hash match against `efuse_iFitG520.img` and the private key, and a factory test that hard-fails unfused units. This confirms the MediaTek root key and the platform keys are resident on CVTE's build system, and it means the factory test needs an unfused mode for the next batch (new I6). (c) ICON's decision to CVTE: no eFuse programming on the next batch, with a consolidated 12-item ask (Section 8). Source G added.

**Changes in revision 1.3.** Program decision recorded: CVTE has already fused 100 units, and the intended posture is to field those serials as a tracked cohort while the remainder of mass production ships unfused until sufficient data exists. This is Option A with an existing cohort. Option B is withdrawn. New Section 3.3 defines the cohort protocol: release preconditions (fuse-map read-back, fingerprint and key checks, forced-download demonstration on a healthy fused unit), the data the cohort must generate (OTA transitions, not calendar time), the unfused control group, and the exit criteria that authorize fused production at CVTE and then Malata. Sacrificial and golden fused test units are now drawn from the 100. The key-rotation decision is flagged as fleet-splitting. Assumptions 23 to 25 added.

**Changes in revision 1.2.** Source F, the MediaTek MT8391/MT8371 Android 15 Secure Boot Developer Guide V1.1, ingested and used to verify Source E. Flag names, the CERT1/CERT2 chain and the DAA flow in Source E are confirmed verbatim. Two facts from the guide change the plan. First, BROM fallback to the second preloader copy is documented **for NAND only**; Cesium boots from eMMC, which is the likely reason `preloader_b` did not take over on the bricked first article, so E2 is rescoped from a pass/fail to a characterization and R1's mitigation rests on E1 and E5 alone. Second, the eFuse configuration file carries a `Disable_Rom_Cmd` option that MediaTek "highly recommends" and that permanently disables BROM command mode; if it is set in `efuse_iFitG520.img`, forced download (E5) is impossible on every fused unit, which would also explain the no-enumeration brick. G7 now reads back that bit explicitly and a new Day 1 action inspects the fuse XML.

**Changes in revision 1.1.** Source E (software root of trust report) ingested. Section 2 rewritten as a three-way comparison (unsigned, software RoT, hardware RoT). The corrupt-preloader brick mode is now classified as **new with fusing**, because under software RoT the BootROM does not verify the preloader and still offers download mode. Case A0 is sharpened to read the preloader security flag and `sboot_state`. A key-freeze rule is added: any key rotation must complete before the first unit ships under either option, because the preloader is outside OTA scope. Three new source conflicts (7 to 9) and two new missing assumptions (19, 20).

---

*Prepared for internal ICON review. Contains no verbatim reproduction of vendor documentation. Not yet issued to CVTE or Malata.*
