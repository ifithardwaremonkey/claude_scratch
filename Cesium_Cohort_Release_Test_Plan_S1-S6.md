# Cesium Fused Cohort Release Test Plan (S1 to S6)

**Purpose:** decide whether the 100 CVTE-fused Cesium tablets may be released, first to the ICON-controlled ring and then to customers. This plan executes Section 3.4 of the Cesium Hardware Root-of-Trust Authorization Plan r1.8. It does not authorize fusing of production units.

| | |
|---|---|
| Product | Cesium tablet iFitG520, MediaTek MT8371 (tool reports MT8189), board C.G520.702, eMMC, battery-less |
| Units under test | Cohort of 100 fused by CVTE on 30 July 2026, currently on the VKC1_20260814 user build |
| Firmware note (r1.1) | **The ring and test units must arrive in Logan on 0814, not reflashed.** The 0814-to-0909 OTA is the first counted fused OTA transition (X1) and the package CVTE attached exists for it. S5 moves five ring units to 0909 with power interruptions; the rest of the ring takes the same OTA at ICON. The single S3/S4 unit reaches 0909 by depot flash instead, which is the other recovery path being proven. **The 70 to 75 customer cohort units are different**: production tablets flow ODM → console vendor → finished-goods vendor → warehouse or store and are not powered until a customer sets them up, so they must receive the 0814→0909 OTA **at CVTE, logged per serial, before they leave CVTE**, after S5 has passed on the ring. CVTE's lab reaches the iFIT OTA server (confirmed 16 Sep), so this is an OTA in the lab, not a flash. Customers then receive 0909, and the cohort's first field OTA coincides with the unfused control group's |
| Hold point | The customer cohort units are held at CVTE's outbound dock until the release decision below is signed. Once they enter the console vendor's flow they cannot be segregated by serial. The console vendor must record tablet serial against console serial at integration |
| Artifacts required | `input.xml`, `GFH_CONFIG.ini`, `root_pubk.der` (CVTE, 14 Sep); VKC1_20260909.zip containing signed `DA_BR.bin` and signed 0909 image; `VKC1_20260814_20260909.zip` OTA package; SP_Flash_Tool_Selector v1.2444 (use V6) with MediaTek USB VCOM drivers |
| Equipment | Windows PC with the VCOM drivers installed and a USB bus monitor (USBTreeView or equivalent); mini-USB cable; switchable or programmable 12 V supply; UART console lead for the DEBUG header; hand tools to open the enclosure |
| Unit location and executors | **The 100 fused units are at CVTE.** ICON holds the bricked unit and at most two other fused units. S1 and S2: ICON, desk work. S3 and S4: CVTE on a healthy fused unit, following the attempt A/B/C procedure below, with video of the USB bus monitor and tool console; ICON repeats if it has a healthy fused unit. S5: ICON, on the ring units after they ship (about one week transit). S6: CVTE, from the per-serial line logs plus three fresh read-backs. CVTE ships the 15 to 20 ring units and the 7 test units now, on 0814 |
| Owner / Test lead | Allen Middleton / Shane Andrus |
| Revision | 1.1, 16 September 2026 (1.0 on 15 September) |

**Ordering rule.** Run S1 and S2 first; they are desk work and either can stop everything. Run S3 before S4 on the same healthy unit. S5 and S6 can run in parallel with S3 and S4 on different units. Do not start S3 on the bricked unit; use a healthy one.

**Global record per unit.** Serial, board revision, firmware fingerprint before and after, tester, date, tool and driver versions, console log file name, photos where the step says so.

---

## S1. Fuse image contents and independent hash check

**Gates:** P1, G4, G7. **Effort:** 1 hour. **Units:** none (desk work) plus the read-back log from Shane's 15 Sep unit.

**Checklist**

- [ ] Open `input.xml` from CVTE. Record the value of every enable switch present. Expected keys per MediaTek Secure Boot Developer Guide V1.1 section 7: `Enable_SBC`, `Enable_DAA`, `Disable_Rom_Cmd`. Record any additional keys verbatim (for example `Disable_JTAG`, `Enable_SW_JTAG_CON`, `SBC_PUBK_HASH` and its value).
- [ ] Open `GFH_CONFIG.ini`. Record `brom_magic_cmd_mode_permanent_dis`, `jtag_en`, `debug_en`, `sec_level`, and any key containing `dis`, `lock` or `perm`.
- [ ] Compute the SHA-256 of the raw public key in `root_pubk.der` with `openssl dgst -sha256 root_pubk.der`. If the value does not match the read-back, also try the hash of the modulus alone (MediaTek's `pbp.py` derives `SBC_PUBK_HASH` from the key material; the exact input is stated in the eFuse Writer Developer Guide). Record which form matched.
- [ ] Compare the computed hash to `sbc_pub_key_hash` in Shane's 15 Sep `read-efuse` output and to the hash embedded in `input.xml`.
- [ ] File both configuration files, the `read-efuse` log and the computed hash in the test record.

**Record**

| Field | Value |
|---|---|
| `Enable_SBC` | |
| `Enable_DAA` | |
| `Disable_Rom_Cmd` | |
| `brom_magic_cmd_mode_permanent_dis` | |
| `jtag_en` / `debug_en` | |
| Hash computed by ICON | |
| Hash from `read-efuse` | |
| Hash in `input.xml` | |

**Cross-check (received 16 Sep).** CVTE's build log for `efuse_iFitG520.img`, dated 27 July 2026, reports `EFUSE_Enable_SBC = 1`, `EFUSE_Enable_DAA = 0`, `EFUSE_Enable_SLA = 0`, `EFUSE_Disable_BROM_CMD = 0`, `EFUSE_Disable_DBGPORT_LOCK = 0`, `EFUSE_USB_download_type = 0`, and states `brom_magic_cmd_mode_permanent_dis` does not exist in the project. The values read from `input.xml` must agree with this log; a disagreement is itself a finding.

**Pass:** `Enable_SBC` true; `Enable_DAA` false; `Disable_Rom_Cmd` (or `Disable_BROM_CMD`) false and `brom_magic_cmd_mode_permanent_dis` 0 or absent; values agree with CVTE's 27 July build log; ICON-computed hash equals the read-back hash.

**Fail:** any of: `Disable_Rom_Cmd` true or `brom_magic_cmd_mode_permanent_dis` 1 (stop: no cohort unit to customers, fuse image must be regenerated); `Enable_DAA` true (stop: recovery requires an AuthFile that does not exist in the depot chain); hash mismatch (stop: the key CVTE sent is not the key that was burned, escalate before anything else).

---

## S2. OTA payload partition scope

**Gates:** E1. **Effort:** 1 hour. **Units:** none (desk work).

**Checklist**

- [ ] Extract `payload.bin` and `payload_properties.txt` from `VKC1_20260814_20260909.zip`.
- [ ] List the partitions in the payload manifest. Any AOSP payload dumper works (for example `python3 payload_dumper.py --list payload.bin`); the manifest is protobuf at the head of `payload.bin`. If no dumper is available, `strings payload.bin | head -200` shows the partition names in the manifest.
- [ ] Repeat for the full 0909 package from VKC1_20260909.zip if it contains an OTA payload (the factory image set is not an OTA and is out of scope here).
- [ ] Record every partition name. Mark each as A/B slot partition (boot, system, vendor, product, vbmeta and variants, dtbo, lk, tee, scp, spmfw, and so on) or as boot0 / preloader.
- [ ] Ask CVTE for `AB_OTA_PARTITIONS` from the 0909 board configuration (`BoardConfig.mk` / `device.mk`) and record it. If `preloader` is absent from that list the OTA builder cannot emit a preloader image at all, which is the stronger form of the E1 guarantee. Record whether CVTE describes the Android 15 BSP as a vendor-freeze release.

**Record**

| Partition | Present in 0814→0909 payload | Class |
|---|---|---|
| preloader / preloader_a / preloader_b / boot0 | | non-A/B, BROM-verified |
| lk / lk_a / lk_b | | A/B, preloader-verified |
| tee / tee_a / tee_b | | A/B, preloader-verified |
| boot, vbmeta*, dtbo, system*, vendor*, product*, odm*, *_dlkm | | A/B |
| other (list) | | |

**Pass:** no preloader or boot0 partition in any OTA payload. LK, TEE and Android partitions may be present: a bad LK is refused by the fused preloader, which then offers preloader USB download mode, so that failure is depot-recoverable.

**Fail:** preloader or boot0 present in an OTA payload. Stop. This is a release-pipeline change before either the cohort or the unfused MP fleet ships, because a corrupt preloader on a fused unit is the one hard-brick mode and the same package would go to the unfused fleet.

---

## S3. Forced download entry on a healthy fused unit

**Gates:** P2 first half, conflict 11, ask 15. **Effort:** 1 hour. **Units:** one healthy cohort unit that boots normally. **Do not use the bricked unit.**

**Setup checklist**

- [ ] Confirm the unit boots to Android and record `getprop ro.build.fingerprint`, `ro.boot.verifiedbootstate`, `ro.boot.veritymode`.
- [ ] Power off. Open the enclosure. Photograph the board and identify the tact switch CVTE marked in the 14 Sep photo (near the `DC_12V_IN` header). Confirm with CVTE's photo that it is the download switch and not `RESET`.
- [ ] Install MediaTek USB VCOM drivers on the PC. Confirm in Device Manager that no MediaTek device is currently listed.
- [ ] Start SP Flash Tool V6. Load `flash.xml` from the 0909 package. Set connection to USB, select the signed `DA_BR.bin`. Put the tool in **Download** waiting state.
- [ ] Start the USB bus monitor with a capture log. Note the time.
- [ ] Connect the mini-USB cable to the PC. 12 V still off.

**Attempt A: BROM window without key**

- [ ] Apply 12 V with no button pressed. Watch the bus monitor for 30 seconds. Record any device that appears, with VID:PID and how long it stays. Expected candidates: `0E8D:0003` (BROM), `0E8D:2000` (preloader). Remove 12 V.

**Attempt B: download switch held**

- [ ] Hold the download switch. Apply 12 V. Keep holding for 10 seconds, then release. Watch the bus monitor for 60 seconds. Record devices, VID:PID, duration, and whether SP Flash Tool reports a connection. Remove 12 V.

**Attempt C: switch held, tool handshake**

- [ ] Repeat Attempt B with SP Flash Tool already in Download and click Download before applying 12 V, so the tool is actively polling. Record the tool console output. If the tool connects, **stop at the connection**: do not flash. Close the tool cleanly and power off.

**Record**

| Attempt | Devices seen (VID:PID) | Duration visible | SP Flash Tool connected? | Console excerpt |
|---|---|---|---|---|
| A: no key | | | | |
| B: key held | | | | |
| C: key held + tool polling | | | | |

**Pass:** in Attempt B or C, a MediaTek device enumerates and SP Flash Tool reports a connection (DA loaded or "waiting for download" reached). Record which mode (BROM or preloader) by VID:PID. The unit must boot normally afterwards.

**Fail:** no MediaTek device enumerates in any attempt. Interpret with S1: if `Disable_Rom_Cmd` is unset, the failure is procedure, hardware path or BROM behavior, and ask 15 to MediaTek becomes blocking for customer release; if it is set, the failure is explained and the cohort stays internal.

**Note on Attempt A.** If the preloader enumerates briefly even with no key, that is the normal preloader USB window used by the factory SOP and is sufficient for S4. It says nothing about BROM entry when the preloader is bad, which is the E5 question; only a BROM-mode device (`0E8D:0003`) in Attempt B or C answers that.

---

## S4. Depot flash of a healthy fused unit with signed artifacts

**Gates:** H1 in cohort scope. **Effort:** 1 hour. **Units:** the same unit as S3, after it has been confirmed to boot.

**Checklist**

- [ ] Before flashing: `read-efuse` and save the log. Record `sbc_en`, `sbc_pub_key_hash`, `daa_en`, `sla_en`, `jtag_dis`.
- [ ] SP Flash Tool V6, `flash.xml` from VKC1_20260909.zip, signed `DA_BR.bin`, connection USB. Choose the **Firmware Upgrade** profile (the boot-chain profile the SOP documents).
- [ ] Enter download mode by whichever method passed in S3 (or the plain preloader window from Attempt A). Run the download. Record the console log through `Download Ok` or the failure message.
- [ ] Power cycle. Confirm the unit boots to Android. Record fingerprint (`VKC1_20260909`), `ro.boot.verifiedbootstate`, `ro.boot.veritymode`.
- [ ] `read-efuse` again. Compare to the pre-flash log.
- [ ] If a **Download Only** or full-image profile exists in the package, repeat the flash with it and record the partition list it wrote. This is the profile the depot needs for failures outside the boot chain (R19).

**Record**

| Field | Before | After |
|---|---|---|
| Fingerprint | | |
| `sbc_en` / hash | | |
| `daa_en` / `sla_en` / `jtag_dis` | | |
| `verifiedbootstate` / `veritymode` | | |
| Profile used and result | | |

**Pass:** `Download Ok`; boots to 0909; fuse read-back byte-identical before and after; verified boot state green and verity enforcing.

**Fail:** tool refuses the DA (indicates DA authentication is on despite `daa_en` off, escalate); download completes but the unit does not boot (record console, do not retry until the log is reviewed); fuse read-back changed (stop everything; a flash must never alter fuse state).

---

## S5. First cohort OTA transition with power interruption

**Gates:** X1 first transition, D2 and D4 in cohort scope, P6. **Effort:** 1 day. **Units:** five healthy cohort units on VKC1_20260814. Two of the five are the interruption units.

**Setup checklist**

- [ ] Record the fingerprint and active slot (`bootctl get-current-slot` via adb if enabled on the user build, otherwise from the boot console) for all five.
- [ ] Stage `VKC1_20260814_20260909.zip` on the OTA server ring reserved for the cohort, or sideload it via recovery if the backend is not ready. Record which path was used; it must be the same path the MP fleet will use for X2 to be meaningful later.
- [ ] Attach the UART console to the two interruption units. Use the switchable 12 V supply for those two.

**Units 1 to 3: clean update**

- [ ] Trigger the update. Record download start and end, install progress messages, slot switch, reboot.
- [ ] After reboot: fingerprint is 0909, active slot changed, boot-success marker set (`bootctl is-slot-marked-successful` or the console equivalent), `verifiedbootstate` green, `veritymode` enforcing.
- [ ] Power cycle once more and confirm it stays on 0909.

**Unit 4: power cut during payload write**

- [ ] Trigger the update. When install progress is between 40 and 60 percent (console or update log), remove 12 V.
- [ ] Wait 10 seconds. Reapply 12 V. Record which slot boots and the fingerprint. Expected: the old slot, 0814, boots normally.
- [ ] Let the update resume or restart. Record whether it resumes from checkpoint or restarts from zero. Complete the update. Confirm 0909 boots with success marker set.

**Unit 5: power cut during first boot of the new slot**

- [ ] Trigger the update and let it complete to the reboot. On the first boot of the new slot, remove 12 V after the kernel starts and before Android reaches the home screen (roughly when the boot animation appears).
- [ ] Reapply 12 V. Record which slot boots, fingerprint, and the boot-attempt counter from the console. Repeat the cut up to three times if the new slot keeps being selected, so the retry budget is exercised.
- [ ] Final state: either 0909 boots and marks successful, or the bootloader falls back to 0814 after the retry budget. Record which.

**Record**

| Unit | Path (OTA/sideload) | Interruption | Slot before → after | Fingerprint after | Success marker | Boot attempts | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | | none | | | | | |
| 2 | | none | | | | | |
| 3 | | none | | | | | |
| 4 | | 40–60 % write | | | | | |
| 5 | | first boot | | | | | |

**Pass:** all five end on a booting build. Units 1 to 3 on 0909 with success marker set. Unit 4 boots the old slot after the cut and then completes to 0909. Unit 5 ends on 0909 or falls back to 0814 within the retry budget. No unit requires the depot.

**Fail:** any unit that does not boot either slot after power is restored (record everything, attempt S4 recovery on it, and treat it as a cohort stop until root-caused); any unit that boots but reports verified boot state other than green; the update engine refusing to start on a battery-less unit (record the reason; this is the N6 health HAL concern and blocks the transition for the whole cohort).

---

## S6. Fuse read-back sampling

**Gates:** P1 sampling. **Effort:** 1 hour. **Units:** three cohort units chosen at random from serials not used in S3 to S5.

**Checklist**

- [ ] Pick three serials by a method that is recorded (random number against the serial list).
- [ ] For each: preloader-mode USB connection, SP Flash Tool `read-efuse`, save the log against the serial.
- [ ] Compare each to the S1 reference: `sbc_en`, `sbc_pub_key_hash`, `daa_en`, `sla_en`, `jtag_dis`, and the ROM command-disable bit if the tool reports it.
- [ ] Confirm each boots normally afterwards.

**Record**

| Serial | `sbc_en` | Hash matches S1 | `daa_en` | `sla_en` | `jtag_dis` | ROM cmd disable | Boots |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

**Pass:** all three identical to the S1 reference and booting.

**Fail:** any unit with a different hash or a different fuse map. Stop sampling, read back ten more, and treat the cohort as two populations until CVTE's per-serial line logs explain the difference.

---

## Non-test preconditions (paper)

These are not tests but the release decision needs them on file.

- [ ] **P4 key decision.** Written: no rotation for the cohort or MP; residual risk of the Basecamp-distributed private keys accepted; attachments removed from Basecamp; holder named for `root_prvk.pem`, `img_prvk.pem`, `da_prvk.pem`, and the Android platform keys.
- [ ] **P5 backend records.** Every cohort serial recorded in the OTA backend with fuse state = fused, fingerprint, slot, and a depot routing flag that prevents any unsigned flash attempt.
- [ ] **A0-b on one unfused 0909 unit.** `ro.boot.verifiedbootstate=green`, `ro.boot.flash.locked=1`, `fastboot flashing unlock` refused, and a wrong-key `vbmeta` refused at boot. Pass means the unfused MP fleet enforces AVB from LK and ships as built. Fail means the preloader flag change is required before 2 October.

---

## Release decision

| S1 | S2 | S3 | S4 | S5 | S6 | Paper | Decision |
|---|---|---|---|---|---|---|---|
| Pass | Pass | Pass | Pass | Pass | Pass | Done | Release ICON ring now; release customer units from CVTE's dock after they have taken the 0814-to-0909 OTA at CVTE with per-serial logs |
| Pass | Pass | **Fail** | Pass | Pass | Pass | Done | Release ICON ring; hold customers for MediaTek's answer to ask 15. Exposure meanwhile is boot0 storage failure only, since S2 shows OTA cannot write the preloader |
| **Fail: ROM cmd disable set** | any | any | any | any | any | any | No cohort unit to customers. The 100 stay ICON-internal. Fuse image regenerated before any further fusing |
| **Fail: hash mismatch or DAA on** | any | any | any | any | any | any | Stop; escalate to CVTE before any other step |
| any | **Fail** | any | any | any | any | any | Stop; release pipeline must exclude preloader before cohort or MP ships |
| any | any | any | **Fail** | any | any | any | Stop; no depot path for fused units; root-cause before release |
| any | any | any | any | **Fail** | any | any | Stop; the A/B path failed on a fused unit; root-cause with console logs |
| any | any | any | any | any | **Fail** | any | Widen sampling; cohort treated as two populations |

**Sign-off**

| Role | Name | Date | Signature |
|---|---|---|---|
| Test lead | Shane Andrus | | |
| Owner | Allen Middleton | | |
| Approver (release of cohort to ICON ring) | | | |
| Approver (release of cohort to customers) | | | |

*This plan releases the fused cohort only. Authorization to fuse production units follows the full Cesium Hardware Root-of-Trust Authorization Plan, Section 4.*
