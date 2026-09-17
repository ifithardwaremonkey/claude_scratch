# Cesium Fused Cohort Release Test Plan (S1 to S6)

**Purpose:** decide whether the 100 CVTE-fused Cesium tablets may be released, first to the ICON-controlled ring and then to customers. This plan executes Section 3.4 of the Cesium Hardware Root-of-Trust Authorization Plan r1.15. It does not authorize fusing of production units.

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
| Revision | 1.2, 17 September 2026 (1.1 on 16 September, 1.0 on 15 September). v1.2: S3 rewritten to CVTE's demonstrated 17 Sep procedure; S3b added for the bricked first article |

**Ordering rule.** Run S1 and S2 first; they are desk work and either can stop everything. Run S3 before S4 on the same healthy unit. S5 and S6 can run in parallel with S3 and S4 on different units. S3b runs on the bricked unit only, at ICON, and can run today: it needs no cohort hardware.

**Status 17 Sep.** CVTE has demonstrated S3 on a deliberately bricked fused unit (preloader signed to a key that does not match the burned hash) and recovered it. The procedure below is CVTE's, with the three conditions that differ from ICON's failed 15 Sep attempt marked **(condition)**. Shane's own brick method, requested by CVTE, is in S3b.

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

**Gates:** P2 first half, conflict 11. **Effort:** 1 hour. **Units:** one healthy cohort unit that boots normally. **Status: passed at CVTE on 17 Sep on a bricked unit, which is the stronger case.** ICON runs it on a healthy unit only for the record and to rehearse S3b; if no healthy fused unit is at ICON, skip to S3b.

**Setup checklist**

- [ ] Confirm the unit boots to Android and record `getprop ro.build.fingerprint`, `ro.boot.verifiedbootstate`, `ro.boot.veritymode`.
- [ ] Power off. Open the enclosure. Photograph the board and identify the **Force Flash** tact switch CVTE marked in the 14 Sep and 17 Sep photos (near the `DC_12V_IN` header). Confirm against CVTE's photo that it is Force Flash and not `RESET`.
- [ ] Install MediaTek USB VCOM drivers on the PC. Confirm in Device Manager that no MediaTek device is currently listed.
- [ ] Start SP Flash Tool V6. Load `flash.xml` from the 0909 package. Connection USB, signed `DA_BR.bin` selected. **(condition 1)** Set the scene to **Format all + download**, exactly as CVTE did. For S3 on a healthy unit this scene would erase the unit, so the tester must be ready to cancel at the handshake; if the tool version cannot be cancelled cleanly, run S3 only on a unit that S4 will reflash anyway.
- [ ] **(condition 2)** Click **Download** now, before power, so the tool is actively polling for a BROM device. Confirm the status bar shows it waiting.
- [ ] Start the USB bus monitor with a capture log. Note the time.
- [ ] Connect the mini-USB cable to the PC. 12 V still off.

**Attempt A: BROM window without key (reference only)**

- [ ] Apply 12 V with no button pressed. Watch the bus monitor for 30 seconds. Record any device that appears, with VID:PID and how long it stays. Expected candidates: `0E8D:0003` (BROM), `0E8D:2000` (preloader). Remove 12 V. If the tool starts a download, cancel it.

**Attempt B: Force Flash held before power (CVTE's procedure)**

- [ ] **(condition 3)** Press and hold Force Flash **first**, with 12 V still off. Then apply 12 V while continuing to hold. Keep holding until the tool reports a device (CVTE: "ensure it is low after power-on"). Do not release at a fixed time.
- [ ] Record: devices seen with VID:PID, the tool console from first contact, and whether the tool reports the BROM or the DA stage. Once the tool has connected and identified the device, **cancel** before any partition is written. Remove 12 V.

**Attempt C: repeat of B (repeatability)**

- [ ] Power-cycle and repeat Attempt B once. Two successes out of two are required, because the 15 Sep failure was a single attempt with no repeat.

**Record**

| Attempt | Devices seen (VID:PID) | Time from 12 V to first enumeration | Tool stage reached (BROM / DA / download started) | Console excerpt |
|---|---|---|---|---|
| A: no key | | | | |
| B: Force Flash held before power | | | | |
| C: repeat of B | | | | |

**Pass:** in Attempts B and C, a MediaTek device enumerates and SP Flash Tool reports a connection (BROM handshake or DA loaded). Record which mode by VID:PID; `0E8D:0003` is the BROM entry that E5 needs. The unit must boot normally afterwards.

**Fail:** no MediaTek device enumerates in B or C with all three conditions met. Interpret with S1 (ROM command disable state) and with CVTE's 17 Sep result: since CVTE's unit entered BROM on the same fuse map, a failure at ICON is a procedure or fixture difference (driver, cable, hub, button contact, 12 V rise time) before it is a BROM behavior question. Photograph the setup and send CVTE the console log.

**Note on Attempt A.** If the preloader enumerates briefly even with no key, that is the normal preloader USB window used by the factory SOP and is sufficient for S4. It says nothing about BROM entry when the preloader is bad, which is the E5 question; only a BROM-mode device (`0E8D:0003`) in Attempt B or C answers that.

---

## S3b. BROM recovery of the bricked first article J26080143-0A00076

**Gates:** E5, X3, P2 second half. **Effort:** 1 hour. **Units:** the bricked first article (preloader RSA signature corrupted in boot0 on 16 Sep, boot1 intact, fused 8 Sep, userdebug VKC1_20260907, unlocked). **Runs at ICON today; no cohort hardware needed.**

**Why this should work now.** CVTE's 17 Sep brick and this one are the same BootROM event: BROM rejects the preloader in boot0 against the burned hash, whether the signature is corrupted (this unit) or valid under the wrong key (CVTE's). CVTE recovered theirs. The two differences from the 15 Sep attempt on this unit are the button already low when 12 V is applied and the tool already polling in "Format all + download". One difference between the units is untested: this one was fused first and corrupted afterwards; CVTE's was flashed with mismatched firmware and then fused.

**Checklist**

- [ ] Open the enclosure and locate Force Flash per the S3 photo. Check the switch with a meter: it must pull the line low when pressed and the contact must hold (a worn tact switch that bounces open during the BROM sample is a plausible cause of the 15 Sep result).
- [ ] SP Flash Tool V6, `flash.xml` from `VKC1_20260909.zip`, signed `DA_BR.bin`, connection USB, scene **Format all + download**. Note this erases userdata; nothing on the first article needs preserving. Confirm every image in the scene is the signed 0909 set, since BROM will verify the DA and the new preloader against the burned hash.
- [ ] Click **Download** so the tool is listening. Start the USB bus monitor. Connect the cable. 12 V off.
- [ ] Press and hold Force Flash. Apply 12 V while holding. Keep holding until the tool reports a device or 60 seconds pass. Record the time from 12 V to first enumeration and the VID:PID.
- [ ] Let the download run to "Download Ok". Record the console log in full.
- [ ] Power-cycle. Confirm boot to Android and record `ro.build.fingerprint` (expected VKC1_20260909), `ro.boot.verifiedbootstate`, `ro.boot.veritymode`.
- [ ] `read-efuse`. Compare to the 8 Sep read-back: `sbc_en` on, hash `6da1756f…83730c68`, DAA, SLA, JTAG-disable off. A flash must never alter fuse state.
- [ ] If no enumeration after two attempts: photograph the setup, capture the bus-monitor log, and try once with a different cable and a USB 2.0 port on a different host. Then stop and send CVTE the logs with ask 31; do not proceed to the eMMC test point without CVTE's board guidance (ask 24).

**Record**

| Field | Value |
|---|---|
| Attempt count to first enumeration | |
| VID:PID at first enumeration | |
| Time from 12 V to enumeration | |
| Tool result | |
| Fingerprint after boot | |
| verifiedbootstate / veritymode | |
| read-efuse identical to 8 Sep | |

**Pass:** the unit enumerates, "Download Ok", boots VKC1_20260909 with verified boot green, fuse read-back unchanged. E5 and X3 close; confidence becomes eligible for Medium per the main plan Section 3.5.

**Fail:** no enumeration with all conditions met and two cable/host variations tried. Confidence stays Low. The order-of-events difference (fused-then-corrupted versus mismatched-then-fused) becomes the question for CVTE and MediaTek (ask 31), and the eMMC test point (ask 24) returns as the fallback path.

**Method given to CVTE (their request of 17 Sep).** Delivered the same day as the full G520 eFuse Burn Log PDF. Summary for the record: on a fused unit that boots, take the signed production `preloader.bin`, flip 32 bytes inside the RSA signature block (leave the code and the GFH header untouched), write it to boot0 (`preloader_a`) only with SP Flash Tool "Download only", leave boot1 intact, power-cycle. Record whether the tool accepts the write; on 16 Sep it did, which is conflict 12. Then attempt the same BROM recovery.

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

**Unit 4b (optional, if LK or TEE appear in the S2 partition list): power cut during the LK/TEE write.** `update_engine` writes partitions in manifest order; watch the console for the `lk` or `tee` partition name and remove 12 V while it is being written. Expected: identical to unit 4, the old slot boots because the slot switch has not happened. This is the one write whose failure a fused preloader would refuse rather than crash on, and it is the narrowest window in the whole OTA.

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

## S7 (recommended, after the seven test units arrive). Randomized power-interruption soak on fused units

**Gates:** D7 in cohort scope; answers the power-loss question directly. **Effort:** about one week unattended. **Units:** the seven test units (CLOSED-1..7), or as many as remain healthy after S3/S4.

**Setup.** Programmable 12 V supply under script control; UART console logging on each unit; a repeatable OTA source that can be re-armed (the 0814→0909 package applied to a unit that is then flashed back to 0814 by the S4 depot path, or two signed builds that can ping-pong between slots).

**Checklist**

- [ ] Script: start OTA, wait a uniformly random interval across the full download-plus-install-plus-first-boot window, cut 12 V for 5 seconds, restore, wait for boot, record outcome and the OTA phase at the cut from the console.
- [ ] Run 200 cycles spread across the units. Record per cycle: phase at cut, slot before and after, boot attempts, final fingerprint, recoverable yes/no.
- [ ] Any cycle that does not end in a booting unit: stop that unit, preserve console log, attempt S4 recovery, root-cause before continuing.

**Pass:** zero unrecoverable units over 200 cycles. Failure distribution by phase reported.

**Fail:** any unrecoverable unit. Confidence drops to Not ready until root-caused.

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
| Pass | Pass | **Fail** | Pass | Pass | Pass | Done | Release ICON ring; hold customers for MediaTek's answer to ask 15. Exposure meanwhile is boot0 storage failure only, since S2 shows OTA cannot write the preloader. **Not the active branch from 17 Sep: S3 passed at CVTE** |
| any | any | Pass (CVTE) | any | any | any | any | S3b result does not change the cohort release. S3b pass closes E5 and X3 and moves confidence toward Medium (fused production); S3b fail keeps confidence Low and reopens ask 15 with the order-of-events question |
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
