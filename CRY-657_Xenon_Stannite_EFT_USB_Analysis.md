# CRY-657: Xenon ↔ Stannite USB link loss under EFT — bugreport analysis

Analysis date: 2026-10-01. Analyst input: the pre-debounce bugreport bundle `CVTE-CVTEMediatekXenon1_06-Wed-05_10.44.zip` (Allen, Jira attachment 242132, recovered from Drive folder `Xenon_EFT_USB_fail-CVTEMediatekXenon1_06-Wed-05_10.44`), plus Jira CRY-657 / BRAIN-402 / BRAIN-814 comment history, the WOLF "USB Disconnect Issue 11/1" Confluence page, and a Cesium bugreport (`bugreport-iFitG520-AP3A.240905.015.A2-2026-09-11-00-07-42`) for the topology comparison.

## 0. Coverage and what could not be analysed

| Attachment | Status |
|---|---|
| 242132 pre-debounce bundle (05-06) | Analysed in full: `dmesg.log`, `logcat.log.txt`, `com.ifit.glassos_service/log.latest.txt`, `device_properties.txt`, and the embedded Android bugreport (`bugreport-Xenon-TP1A.220624.014-2026-05-06-12-45-05`). |
| 242591 post-debounce bundle (05-11, 1.0/1.4 kV) | **Not retrievable.** Jira attachment downloads are blocked by this environment's network policy (host `ifitdev.atlassian.net` denied; `api.atlassian.com` likewise). The file is not in Drive, Slack, or Gmail. The Slack zip Matthew Thomas posted on 05-12 (`2026-05-12@15.51.23.zip`) is from a different tablet (UUID 33295a3d…, glassos 8.46.5) and is unrelated. Still wanted for its `dmesg.log` (see §2d). |
| 242592 Eru "report an issue" log (Tayte, 05-11) | **Analysed in full** (uploaded by Allen on 2026-10-02). Device UUID 55f358e4…, glassos_service **8.47.4.1896** (debounce build), Stannite FW 4.04. Contains `com.ifit.glassos_service/log.latest.txt` (10:12 → 12:33 on 05-11), `adbLogs.txt` (a logcat covering 05-11 10:45 → 12:33 with `UsbHostManager` lines; no kernel buffer), and the Eru, Rivendell, Arda, Mithlond, Gandalf logs. Results in §2d. |
| 242134 Valinor_Forensic_Analysis.pdf | Not retrievable; the Google Doc source of it was read. Its "one-hour kernel/framework clock offset" claim is wrong (see §1 clock note) and its Zylux conclusions are unrelated, as the Valinor team already said. |
| BRAIN-824 / BRAIN-814 Eru logs | Not retrievable from Jira; not in Drive. Classified from ticket text and from the Cesium bugreport that is in Drive. |

Consequence: the "~6 min after the burst stops" recovery that Keyvan reported (05-11 run) is now covered at the Android level by the Eru log (§2d) but still not at the kernel level. The remaining gap is the 05-11 `dmesg.log` inside attachment 242591, which would say which side (host port or brainboard) is driving the loop described in §2d.

### Log-coverage facts that matter for reading the evidence

- `dmesg.log` is the kernel ring buffer and only covers **12:33:56 → 12:45:02** (the last 11 minutes before the bugreport). The entire burst period (11:33 → 12:29) is outside it. `/proc/last_kmsg` does not exist on this build.
- `logcat.log.txt` has three buffers: *system* 09:49:13 → 11:46:37, *crash* 11:46:38 → 12:36:43, *main* 12:36:43 → 12:45:01. `UsbHostManager` lines therefore exist only for 11:33 → 11:59.
- `com.ifit.glassos_service/log.latest.txt` is the only continuous record of the whole test and is used as the primary USB event timeline. It is a concatenation of rotated files: lines 1–3981 are stamped with the pre-NTP clock (09:49–09:53, offset −1 h 39 m 54 s from real time; the "09:53 burst" is the 11:33 burst), lines 3982–4503 are a flushed "delayed log" block from an older boot (21:27), and the real-clock content starts at line 5593 (11:30:54). Only the 11:xx/12:xx block is used below.
- Clock alignment: kernel bracket timestamps match logcat and glassos (12:43:43 kernel re-enable ↔ 12:43:44.587 `UsbAlsaManager` removal ↔ 12:43:44.600 glassos detach; dmesg ends 12:45:02, bugreport taken 12:45:05). No inter-log offset needs to be applied. Absolute wall time is suspect (the device's zone looks like UTC−4), so correlate with the lab's test record by relative offsets.
- Device: `CVTEMediatekXenon1`, OS `VKX1_20241014` (Android 13, MT8188 / Genio 700), glassos_service **8.37.2** (no debounce), SELinux permissive (`permissive=1` on every avc line).

## 1. Bus topology of the Stannite port (answers H2)

```
Genio 700 (MT8188)
 ├─ 11200000.xhci1 / 11201000.usb1   host-only xHCI  ── bus 1 (USB2 root hub) ── root port 1 ── [USB-C receptacle] ── Stannite  (usb 1-1, full-speed)
 │                                                     └─ bus 2 (USB3 root hub, unused)
 ├─ 112a0000.xhci2 / 112a1000.usb2   host-only xHCI  ── bus 3 / bus 4 (nothing enumerated)
 └─ 112b0000.xhci  / 112b1000.usb    mtu3 dual-role (OTG) + TCPC MT6375 / rt_pd_manager ── bus 5 / bus 6 ── ADB / charging port
```

Evidence:

```
[Wed May  6 12:43:43 2026] usb usb1-port1: disabled by hub (EMI?), re-enabling...
[Wed May  6 12:43:43 2026] usb 1-1: USB disconnect, device number 51
[Wed May  6 12:43:44 2026] usb 1-1: new full-speed USB device number 52 using xhci-mtk-p1
[Wed May  6 12:43:44 2026] usb 1-1: New USB device found, idVendor=213c, idProduct=0006, bcdDevice= 4.04
[Wed May  6 12:43:44 2026] usb 1-1: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[Wed May  6 12:43:44 2026] usb 1-1: Product: LargeX-Stannite
[Wed May  6 12:43:44 2026] usb 1-1: Manufacturer: IFIT
```

- Path `1-1` = root port 1 of bus 1. A hub would give `1-1.x` and the hub itself would enumerate first; neither appears anywhere in dmesg, logcat (`/dev/bus/usb/001/NNN` only, always the Stannite) or glassos. **There is no hub on the Stannite path on Xenon.** Hub checklist applied to this bugreport: no hub-class device (`mClass=9`) ever enumerated; no VIA vendor ID (0x2109) anywhere in dmesg, logcat or the bugreport; all 1,820 device-node references across logcat and glassos are on bus 001 with undotted paths; and the one port event captured is logged against the **root hub** (`usb usb1-port1: disabled by hub (EMI?)`), not against a `hub 1-1:1.0: port N` downstream port. So on Xenon the SoC PHY is the one tripping. (Note the Cesium design is different, see §6.)
- SoC identification: `ro.board.platform=mt8188`, `ro.hardware=mt8390`, `init.mt8188.usb.rc`, i.e. the Genio 700 (MT8390/MT8188 family) that the 2024 BRAIN-402 PHY fix was made on.
- Bus 1 is served by `xhci-mtk-p1`, a host-only `xhci_mtk_hcd` instance. The dual-role controller `112b1000.usb` is a different block: at 12:43:37 it switched host→device→none (`ssusb_mode_sw_work_v2`, buses 5 and 6 deregistered) when a cable was plugged for ADB, and the Stannite on bus 1 was unaffected. By elimination bus 1 belongs to `11200000.xhci1` (CVTE should confirm with `readlink /sys/bus/usb/devices/usb1`).
- Type-C: the only TCPC/PD drivers loaded (`tcpc_mt6375`, `tcpc_class`, `rt_pd_manager`, `tcpci_late_sync`, `extcon_mtk_usb`) belong to the dual-role port. No `tcpc`/`typec`/`pd` message touches bus 1. Whatever sits behind the Stannite USB-C receptacle is not a Type-C port controller the kernel knows about.
- The Stannite is a **full-speed** composite device: config "FS Configuration", 100 mA; IF0 vendor-specific (class 255) with interrupt endpoints 0x83 IN / 0x03 OUT, 64 B (FitPro2); IF1 audio control; IF2 audio streaming (isochronous 0x01 OUT 196 B + feedback 0x82). A full-speed USB 2.0 link through a Type-C receptacle needs no orientation mux (D+/D− are present on both A6/A7 and B6/B7), so Allen's "switch" is either a transparent analog switch or does not exist on the data pair. Either way the **Genio 700 U2 PHY instance behind xhci1 owns disconnect detection, squelch and bus-error handling for this port**. The 2024 BRAIN-402 tuning (VKX1MP16_20240403, Vterm 780→800 mV, "Modify USB driver parameters to optimize EFT disconnection issues") can reach this port *if* CVTE applied it to that PHY instance and not only to the instance behind the USB-2 JST connector. One caveat to raise with CVTE: the HS disconnect-envelope threshold only matters on high-speed links; Stannite runs full-speed, so ask which register was changed and whether it also affects FS squelch / disconnect debounce.
- Bonus finding: `dumpsys usb` crashes on this device (`UsbDescriptorParser … ByteStream IllegalArgumentException` while dumping the Stannite connection record; also `UsbACInterface: Unknown Audio Class Interface subtype:0xa`). The USB port-manager section is therefore missing from every Xenon bugreport. This is an AOSP/CVTE bug worth a separate ticket because it hides exactly the information this investigation needed.

## 2. Timeline, pre-debounce run (05-06, glassos 8.37.2)

All times are device time; 11:33 is the first disconnect of a brainboard that had been stable since boot (~11:29) as device number 2.

### 2a. Burst windows seen by Android (glassos SDUSB broadcasts, cross-checked against `UsbHostManager` where logcat covers)

| Window | Attach/detach cycles | Notes |
|---|---|---|
| 11:33:04 → 11:33:18 | 10 | First burst; glassos reconnects at 11:33:18, FitPro2 initialised 11:33:20 |
| 11:38:20 → 11:38:22 | 3 | followed by 1 Hz failed enumerations until 11:38:47; stable at 11:38:48 |
| 11:39:47 → 11:39:50 | 3 | then failed enumerations 11:39:50 → 11:43:01 (≈190 s) |
| 11:43:01 → 11:43:13 | 20 | then failed enumerations → 11:46:23 (≈190 s) |
| 11:46:23 → 11:47:01 | 33 | then failed enumerations → 11:50:14 (≈190 s) |
| 11:50:14 → 11:50:17 | 4 | then failed enumerations → 11:53:29 (≈190 s) |
| 11:53:29 → 11:53:32 | 3 | then failed enumerations → 11:54:15 |
| 11:54:15, 11:56:20, 11:58:26, 12:00:32, 12:02:38 | 1 each | isolated single flaps, **period 125.7 s** |
| 12:06:33 → 12:06:35 | 3 | then failed enumerations → 12:09:45 (≈190 s) |
| 12:09:45 → 12:09:48 | 3 | → 12:12:58 (≈190 s) |
| 12:12:58 → 12:13:03 | 6 | → 12:16:14 (≈190 s) |
| 12:16:14 → 12:16:46 | 50 | → 12:19:57 (≈190 s) |
| 12:19:57 → 12:20:48 | 45 | |
| 12:22:53, 12:24:59, 12:27:05, 12:29:10 | 1 each | isolated single flaps, **period 125.7 s** |
| 12:43:44 | 1 | the "disabled by hub (EMI?)" re-enable, see 2c |

Totals over the test: **191 successful enumerations** (190 detaches) seen by Android; **1,139 failed kernel enumeration attempts** logged by `UsbHostManager` as `Removed device at /dev/bus/usb/001/NNN was already gone` between 11:33 and 11:59 alone, at exactly one per second with the device number advancing by one each time (e.g. 11:40:00 → 059, 11:40:01 → 060 …). Device-number wrap analysis of the glassos log shows the same 1 Hz loop continued in every ≈190 s window through 12:19:57, so the whole test produced roughly 1,800 failed enumerations. The "396 OS-level detaches" counted by the Valinor team is the 11:33–11:59 subset of successful-then-dropped enumerations plus a part of the failed ones.

Interpretation of the two patterns (revised after the 05-11 analysis in §2d):

- The **windows of 1 Hz "already gone" events** are not failed enumerations. A `/dev/bus/usb/001/NNN` node only exists after usbcore has completed enumeration (reset, SET_ADDRESS, device and configuration descriptors, strings), so each event is a *complete, successful* kernel enumeration after which the device disappeared within a few tens of milliseconds, before `UsbHostManager` could open the node. The cycle period is **1.002–1.003 s** (497 + 489 of 1,063 intervals in 11:40–11:58 are exactly 1002 or 1003 ms), far too regular for random burst hits. The link is therefore being torn down and rebuilt by something deterministic for as long as the loop lasts; the EFT burst is what *starts* it.
- The **short attach/detach clusters** (link alive 110–400 ms, then dropped) are enumerations that survived long enough for Android to see them; they bunch at the start and end of burst applications.
- The **≈125.5 s isolated single flaps** are not a timer. Each one is the enumeration that occurs **exactly every 126th cycle of the 1 Hz loop**, and it always carries the **same USB device number** within a series (045 at 11:54:15, 11:56:20, 11:58:26, 12:00:32, 12:02:38; 051 at 12:22:53, 12:24:59, 12:27:05, 12:29:10), i.e. once per wrap of the 126-value device-number space. Every recovery in both runs happened on one of these cycles (12:02:38 and 12:29:10 here; 11:00:11 and 11:25:20 on 05-11). Whatever lets that one cycle live longer is also what ends the loop. This is the fingerprint to match against the host xHCI/PHY and against Stannite firmware (§2d).

### 2b. Whether the brainboard enumerated with valid descriptors (answers H4)

Every one of the 191 successful enumerations reported `vidpid 213c:0006 mfg/product/ver/serial IFIT/LargeX-Stannite/4.04/null`, class 239/2/1, identical interface and endpoint set. **`productId 6` is the Stannite's real PID (0x0006, "LargeX-Stannite")**, not a corrupted descriptor; `mVendorId=8508` is 0x213C (ICON). This also settles two documentation points: the Stannite control interface is **vendor-class 255 with interrupt endpoints**, the same shape as the Quartz reference descriptor (`213c:0003 "iFIT-LargeX" v3.03`, see §6), not a CDC/USB-serial interface; and glassos 8.37.2's `FIT_PRO_2_STANNITE` handler **does** accept PID 6 (28 of 28 permission grants in this log were handled by it and connected). The "invalid productId 6 / UNKNOWN" wording from VAL-8863 almost certainly refers to the same parallel `UNKNOWN` handler described next. The "UNKNOWN" in glassos logs is the label of a second device-type handler inside glassos that runs in parallel with the `FIT_PRO_2_STANNITE` handler on every permission grant and always logs `Working with device : UNKNOWN … invalid vendorId 8508 … Giving up on claiming USB connection`; the Stannite handler succeeds 1–5 ms later. Those lines (and `Device detached is not from our vendor ZYLUX`) are noise, not failures. The CLI-396 observation "re-enumerated as productId 6 / UNKNOWN" is therefore normal behaviour.

### 2c. Recovery after each window and after the test (answers H3)

| Window end (last failed/short attach) | Stable attach | glassos connected | FitPro2 initialised | Kernel→app delay |
|---|---|---|---|---|
| 11:33:18 | 11:33:18.04 (dev 019) | 11:33:18.08 | 11:33:20.9 | 2.9 s |
| 11:38:47 | 11:38:47.96 (dev 047) | 11:38:48.01 | 11:38:51.4 | 3.4 s |
| 12:02:38 | 12:02:38.57 (dev 045) | 12:02:38.60 | 12:02:46.3 | 7.7 s |
| 12:29:10 | 12:29:10.62 (dev 051) | 12:29:10.66 | 12:29:12.9 | 2.3 s |
| 12:43:43 | 12:43:45.02 (dev 052) | 12:43:45.05 | 12:43:48.2 | 3.1 s |

- Whenever the bus went quiet, usbcore enumerated the Stannite within ~1 s and glassos (even without debounce) was talking within 3–8 s. **There is no minutes-long backoff in Linux usbcore or in glassos** in this run. (One exception not caused by EFT: `com.ifit.eru` force-stopped and restarted glassos_service at 11:58:31 — an app update — so nothing could connect between 11:58:26 and 12:02:38.)
- The last test flap was 12:29:10; the workout then ran normally and ended at 12:32:14 (PAUSED → RESULTS → IDLE, all ACKed). From 12:32:14 to 12:43:44 glassos logged no FitPro2 traffic at all (console idle; FitPro2 heartbeats on this build are event-driven, and the 1/min "Console Basic Info" poll stops with the workout), so **liveness during that 11.5-minute gap is undetermined**.
- At 12:43:43 the kernel found root port 1 **disabled while still showing a connection** (`usb usb1-port1: disabled by hub (EMI?), re-enabling...`), tore down device 51 and re-enumerated device 52, and audio and FitPro2 came back together within 2 s. This is the only kernel USB event in the 11-minute dmesg window; there is nothing in the gap before it. Six seconds earlier (12:43:37) somebody plugged a cable into the OTG port (ADB) to pull the bugreport. If that cable was plugged because the console looked dead, then the port had been sitting in the disabled state and was only serviced when the system was kicked.

The 05-11 Eru log (§2d) shows that during Keyvan's "~6 minutes after the burst stops" the link was **not quiet**: the 1 Hz enumerate-and-drop loop ran continuously until the moment of recovery. The 12:32→12:43 hold in this run is the one case where Android logs do not cover the gap, so it is left as "undetermined, probably the same loop" (the 12:43:43 kernel line is consistent with the loop's final cycle: port error, re-enumerate, hold).

### 2d. Post-debounce run (05-11, glassos 8.47.4.1896, 1.0 and 1.4 kV) — from attachment 242592

Device time; glassos and `adbLogs.txt` agree to the millisecond. Console booted ~10:39 (FitPro2 initialised 10:39:01), Stannite stable as device 002 until the first burst.

| Phase | Time | What the logs show |
|---|---|---|
| Test 1 start | 10:41:49.600 | device 002 detached; 16 short attach/detach cycles in 11 s; glassos debounce armed and cancelled on each |
| Burst clusters | 10:45:12–10:45:52 (66), 10:48:26–10:48:56 (48), 10:50:36 (3), 10:51:21–10:51:44 (37), 10:55:47–10:56:01 (6), 10:58:06 (1) | each cluster = enumerations that survived 20–400 ms |
| Between and after clusters | 10:45 → 11:00:11 **continuously** | `UsbHostManager` "already gone" at **60 per minute every minute** (10:46, 10:47, 10:49, 10:52, 10:53, 10:54, 10:57, 10:59 all = 60); 1 Hz loop never pauses |
| Survivors | 10:56:01 (dev 033, 385 ms), 10:58:06 (dev 033, 383 ms), 11:00:11 (dev 033, **held**) | 124 "already gone" between each; same device number each time |
| **Recovery 1** | 11:00:11.011 attach → 11:00:12.513 debounce elapsed → 11:00:12.523 connected → 11:00:14.091 FitPro2 initialised | glassos connected **1.5 s + 10 ms** after the first attach that survived; Matthew's "178 cycles" |
| Test 2 start | 11:02:26.774 | device 033 detached after 136 s of stable operation |
| Burst clusters | 11:05:40 (4), 11:08:54–11:09:05 (11), 11:12:18–11:12:32 (23), 11:15:47–11:16:04 (28), 11:16:58 (1), 11:19:04 (1), 11:21:09 (1), 11:23:15 (1) | |
| Between and after clusters | 11:02 → 11:25:20 **continuously** | "already gone" 59–60 per minute every minute (11:17, 11:18, 11:20, 11:22, 11:24 all ≈60) |
| Survivors | 11:16:58 (dev 039, 385 ms), 11:19:04 (039, 20 ms), 11:21:09 (039, 174 ms), 11:23:15 (039, 17 ms), 11:25:20 (039, **held**) | 125 "already gone" between each; period 125.3–125.5 s |
| **Recovery 2** | 11:25:20.461 attach → 11:25:21.969 connected → 11:25:23.555 FitPro2 initialised | Matthew's "74 cycles"; glassos again connected 1.5 s after the first surviving attach |
| Post-test | 11:44:36 glassos restarted (app version log) and reconnected to 039 at 11:44:36.973 | unrelated to EFT |

Totals for 05-11: 189 successful-then-dropped enumerations seen by Android, **2,108 "already gone" cycles**, every one of the 189 attaches with the identical valid Stannite descriptor (`213c:0006 LargeX-Stannite 4.04`), 188 `UsbAlsaManager` audio removals (audio tracks the link exactly), no `AudioPolicyManager` strategy loop.

What this establishes:

1. **The debounce build behaves correctly.** It armed on all 252 attaches, cancelled on the 248 that died within 1.5 s, and connected within 10 ms of the timer on the 4 that lived. There is nothing for glassos to do differently: no attach survives 1.5 s until the loop ends, and when it ends the first surviving attach is used.
2. **The "~6 minutes after the test finished" is an active host↔device loop, not a dead link and not a backoff.** Between the last burst cluster and recovery (10:51:44 → 11:00:11 = 8.5 min; 11:16:04 → 11:25:20 = 9.3 min, of which Keyvan judged the last ~6 min to be post-test), the kernel enumerated the Stannite successfully once every **1.0025 s** and lost it again within tens of milliseconds, 500+ times in a row. Linux usbcore has no such timer; a free-running 1.0025 s cycle is a device boot/re-attach time or a host port error/reset cycle.
3. **The loop ends only on the once-per-126-cycles event**, which always lands on the same device number (033 in the first series, 039 in the second; 045 and 051 on 05-06). The 1 Hz loop and the 126-cycle event are the same mechanism viewed twice, and both recoveries in both runs happened on it.
4. **Which side is looping cannot be decided from Android logs.** Two candidates, with the signature each would leave in the missing 05-11 `dmesg`:
    - **Host port / PHY error cycle (CVTE).** Each cycle would log `usb usb1-port1: disabled by hub (EMI?), re-enabling...` or a port reset/`-71` error followed by `usb 1-1: USB disconnect` and `new full-speed USB device`. The one kernel recovery captured (05-06 12:43:43) has exactly this shape, so this is currently the better-supported candidate. The 126-cycle event would then be something in the host that releases the port once per device-number wrap.
    - **Stannite USB re-attach loop (brainboard FW).** Each cycle would log a plain `usb 1-1: USB disconnect, device number N` with no port error before it (the device dropped its pull-up), then `new full-speed USB device number N+1`. The 126-cycle event would then be a deeper reset in the Stannite (watchdog or MCU reboot) that eventually clears the fault. The fact that the brainboard answers every enumeration with a perfect descriptor and then leaves within ~50 ms fits a firmware that resets its USB stack right after configuration; the fact that the cycle is 1.0025 s and ends after a fixed count of cycles fits a watchdog. Ask the Stannite team whether FW 4.04 has a ~1 s USB re-enumeration path and a ~2 min watchdog/reboot.
   A USB analyzer or a scope on D+/VBUS at the Stannite connector during one minute of the loop would settle it without any log.

Why the two runs looked different: on 05-06 the loop stopped within seconds of each burst application ending; on 05-11 (1.0 and 1.4 kV) it kept running 8–9 minutes after the last cluster. Higher level → the looping party stays in its fault state longer; nothing in the tablet software changed how it recovers.

### 2e. Audio behaviour in this run

Every detach was accompanied by `UsbAlsaManager: USB Audio Device Removed: … USB-Audio - LargeX-Stannite` and every attach by the ALSA card re-add and `AudioFlinger openOutput … AUDIO_DEVICE_OUT_USB_HEADSET`. `AudioPolicyManagerCustomImpl setOutputDevices` lines are ordinary route switches (device 0x4000000 ↔ speaker); there is no `no device found for strategy` retry loop. Audio loss in CRY-657 is purely **USB-link class**: audio and FitPro2 share the same enumeration, so they die and recover at the same instant. Nothing software can do while the kernel cannot keep the device enumerated.

## 3. Verdicts on the hypotheses

| | Verdict | Evidence |
|---|---|---|
| H1 Host-side false disconnect / port error on the Genio side | **Supported as the better of two candidates, not proven** | The single kernel-level recovery captured (05-06 12:43:43) is a root-port "disabled by hub (EMI?)" (port error with device still present), which is the host-side signature; audio (kernel UAC, no Valinor involvement) and FitPro2 die and recover at the same ms; descriptors always valid; phone and laptop on the same fixture pass. Against it: the loop's 1.0025 s period and fixed cycle count look more like a device watchdog than anything in xHCI/usbcore. Refinement either way: the link is **full-speed**, so the HS disconnect-envelope (Vterm) parameter is not obviously the relevant knob; the fix is error tolerance and port recovery on whichever side is looping, not app logic. |
| H2 Topology: hub vs mux decides whether PHY tuning can reach it | **Xenon: refuted for "hub", direct root port confirmed. Cesium: hub confirmed (see §6), so H2 holds there** | Xenon: `usb 1-1` on `xhci-mtk-p1`, no hub device ever enumerated, port event logged against the root hub, no Type-C/TCPC on that path. Disconnect detection is owned by the Genio 700 U2 PHY behind xhci1, so PHY tuning *can* reach it; the open question is whether the 2024 tuning was applied to that PHY instance (CVTE to confirm) and whether the changed register affects a full-speed link. Cesium: brainboard at `6-1.3` behind a hub at `6-1` (VL122 per the block diagram); the hub's downstream PHY owns disconnect detection and SoC tuning cannot reach it. |
| H3 The ~6 min hold is not Linux usbcore | **Supported, and the hold is now characterised** | It is not a backoff and not silence: the kernel enumerated the Stannite successfully once every 1.0025 s and lost it within tens of ms, 2,108 times on 05-11, until a once-per-126-cycles event let one enumeration hold (§2d). glassos connected 1.5 s after that attach both times. Root cause is on the host port/PHY or in Stannite firmware; the Android logs cannot say which (discriminators in §2d, item 4). |
| H4 Device-side corruption | **Refuted for descriptor corruption; a device-side reset loop is back on the table** | 380/380 enumerations across both runs carried the identical valid descriptor (PID 0x0006 "LargeX-Stannite" 4.04), so the Stannite MCU never answered badly. But a brainboard that enumerates perfectly and drops its pull-up ~50 ms later, every 1.0025 s, with a deeper reset every ~126 s, is one of the two consistent explanations for the loop. Needs the dmesg signature or a bus capture. |

## 4. Recommended owner for the recovery delay and the specific asks

**Owner: CVTE / OS (kernel + PHY) and the Stannite firmware team jointly, until one kernel log or bus capture of the loop picks the side.** The decisive measurement is cheap: one minute of `dmesg` (or a USB analyzer / scope on D+ and VBUS at the Stannite connector) while the 1 Hz loop is running after a burst. If each cycle begins with `usb usb1-port1: disabled by hub (EMI?)` or a port-reset error, it is CVTE's; if each cycle is a plain `USB disconnect` with the device dropping its pull-up, it is Stannite firmware's. Until then, both threads run in parallel.

Specific requests for the Stannite firmware team:

1. Does FW 4.04 have any path that re-enumerates USB about once per second (USB peripheral reset on error, brown-out handler, audio codec fault handler that resets the USB stack), and a watchdog or MCU reboot with a period near 2 minutes (126 cycles × 1.0025 s)? Those two numbers are the fingerprint in both runs.
2. Add a UART/debug trace of USB state (attach, configured, reset, watchdog) and capture it during one EFT application; correlate with the tablet's `UsbHostManager` log.
3. Confirm whether the brainboard's USB pull-up / PHY is held through its own reset, or released (a released pull-up is what the host sees as a disconnect).

Specific requests for CVTE:

1. Confirm the controller/PHY instance behind the Stannite USB-C receptacle (`readlink /sys/bus/usb/devices/usb1`, which `mtk-tphy` instance it uses) and confirm whether the VKX1MP16_20240403 EFT change (Vterm/discth) was applied to that instance. If it was only applied to the JST port's PHY, apply it here too. State which register changed and whether it affects full-speed links (Stannite is FS).
2. Explain the 1.0025 s enumerate-and-drop cycle from the host side: capture `dmesg` during the loop and report whether each cycle starts with a port error (`disabled by hub (EMI?)`, port reset, `-71`/`-32`), and whether anything in `xhci-mtk` (port-status-change handling, the MTK bandwidth scheduler for this device's three 1 ms periodic endpoints, the `drop_ep_quirk` path seen in dmesg) can re-trigger once per device-number wrap. Add `dev_info` logging of port status on every hub event for this port in the next engineering build.
3. Provide an OS-side recovery path for a looping or present-but-dead link: either kernel-side (power-cycle `usb1-port1` after N consecutive enumerations that die within 1 s) or an exposed hook (`/sys/bus/usb/devices/usb1/1-0:1.0/usb1-port1/disable` toggle, or port power via `usb1-port1/…`) that Eru (uid 1000, SELinux permissive on this build) can call when glassos or Eru detects the loop (N device-node create/remove pairs with no surviving attach). Android's `UsbManager.resetUsbPort()` only covers Type-C ports managed by the USB HAL and does not apply to this root port. A VBUS power-cycle also resets the brainboard's USB side, so this hook helps whichever party is looping.
4. Fix the `dumpsys usb` crash on Stannite descriptors (`UsbDescriptorParser` IllegalArgumentException; "Unknown Audio Class Interface subtype:0xa") so port-manager state appears in bugreports.

Hardware (Keyvan/Alan): the later pass "with a better USB-C cable" (Allen's 06-08 note) and the historic ferrite fixes point to shield/common-mode coupling into the pair; worth documenting cable shield termination at both ends and whether the receptacle shell is bonded to chassis.

Brainboard FW: no action indicated by these logs, but please confirm or deny a ~126 s periodic USB reset/re-attach in Stannite FW 4.04 under EFT.

**Cesium-specific (brainboard behind the VL122 hub, §6).** Because the hub's downstream PHY, not the MT8371, owns disconnect detection on the brainboard link, the Xenon-style PHY request does not apply. Instead:

- (a) Run a direct-vs-hub A/B EFT test on Cesium with the same brainboard: harness on the VL122 downstream port (current build) versus the direct USB2 pair at V34/V35 ("USB2 Port 2" on the schematic), if that connector can be populated on a test board. Same generator program, same cable, capture `dmesg` for both.
- (b) Open a VIA/CVTE inquiry on VL122 downstream-port behaviour under IEC 61000-4-4: disconnect-detection threshold and debounce on downstream ports, whether downstream port errors can latch the port disabled, and whether the hub's own upstream link resets under burst (a hub reset takes every downstream device with it and would by itself explain a long recovery).
- (c) Assess on each board whether the brainboard harness can be moved to a SoC root port (Cesium: V34/V35; Xenon: already a root port) so that disconnect handling is in CVTE's PHY tuning domain rather than the hub vendor's.

glassos: the 1.5 s debounce (PR #484) is the right behaviour and the 05-11 log proves it does exactly what it should (252 arms, 248 cancels, 4 connects within 10 ms of the timer). Nothing in these logs argues for more app-side retry logic. One cheap addition would help the OS team and CRY-784: count device-node create/remove pairs that never produce an attach (Eru already receives the broadcasts; `UsbHostManager`'s "already gone" is the OS-side view) and log "USB loop detected" after, say, 10 consecutive cycles, so the condition is visible in Eru reports and can later trigger the OS recovery hook from CVTE item 3. CRY-784 (declare link dead, flush pending stop, request OS recovery) remains the right follow-up and should consume that hook rather than retry on its own.

## 5. Audio-loss classification of the BRAIN tickets

Three classes: **A** USB-link (ALSA device removed with the detach), **B** OS routing (device enumerated, `AudioPolicyManager` loop / routed to missing device), **C** amplifier / audio-board hardware (device present and routed, no sound).

| Ticket | Log available here | Class | Basis |
|---|---|---|---|
| CRY-657 (Xenon + Stannite, EFT) | yes (05-06 bundle) | **A** | `UsbAlsaManager Removed/Added` on every one of 190 cycles; no routing loop; recovers with FitPro2. |
| BRAIN-824 (Stannite FW 0.20 audio fault pin, ±5/±8 kV) | no (Jira blocked) | **C**, self-recovering | Ticket root cause is a brainboard FW fault-pin configuration; fixed in FW 0.20; no USB detach reported. Expect the Eru log to show no `USB_DEVICE_DETACHED`. |
| BRAIN-828 / 832 / 833 (Quartz amp, ±8 kV, no self-recovery) | no attachments on tickets | **C**, latching | Quartz-board amplifier stops; HW decision no Quartz change; speaker-grill redesign. |
| BRAIN-814 (Cesium ETNT17125, Quartz/X30) | no Eru log reachable; Cesium 09-11 bugreport read | **C** with a B-class symptom; **not** a USB enumeration failure | The ticket's own final root cause is an intermittent CLK/CS/MOSI connection in the 16-pin Molex between the X30 audio board and the Quartz-485 board; jumpering it and re-running ESD passed. The earlier "FIT_PRO_2_AUDIO fails to enumerate" finding is expected on that hardware: the LargeX/Quartz-family brainboard presents **no USB audio interface** (Cesium bugreport: `vidpid 213c:0003 iFIT/iFIT-LargeX/3.03 hasAudio/HID/Storage: false/false/false`), audio goes over the X30 SPI path. The MTK `strategy 9` routing loop was software reacting to a muted amp path. Class B compliant per Zach. |
| BRAIN-851 (Cesium + Stannite PVT, display flicker) | no | not audio | — |
| BRAIN-830 (Cesium + Stannite, belt slowed) | no | not audio; motor-controller FW (Eway V43) | — |

Correction to the hand-off brief: BRAIN-814 should not be treated as a precedent for a Cesium-specific USB enumeration weakness.

## 6. Does Cesium share the Xenon port design?

No, and the difference is the one that matters. From the Cesium bugreport (iFitG520, VKC1_20260909, Android 15, MT8371 = Genio 520, kernel 6.1) plus the sysfs listing taken on a Cesium unit on 2026-10-02 (addendum):

- Five USB controllers: `11201000.usb0` (dual-role, MTP/ADB, Type-C with `tcpc_mt6375` + `tcpc_rt1711h` + `tcpc_husb238` PD, `usb_dp_selector`), and host-only `11210000.usb1`, `11220000.usb2`, `11260000.usb3`, `11270000.usb4`; driver `xhci_mtk_hcd_v2`. sysfs shows buses `usb1 usb2 usb3 usb6 usb7`.
- **The brainboard is behind a hub.** sysfs shows `6-1` (a hub, the VL122 per the block diagram) and `6-1.3` (the brainboard on the hub's downstream port 3). The 09-11 bugreport is consistent with this: the brainboard is `/dev/bus/usb/006/003`, i.e. device number 3 on bus 6, with device 2 being the hub. It is **not** on a SoC root port. The schematic's direct USB2 pair at V34/V35 ("USB2 Port 2") is either another connector or unpopulated on this build.
- Consequence: on Cesium the **hub's downstream PHY owns disconnect detection** for the brainboard link. MT8371 PHY tuning cannot reach it, and the 2024 BRAIN-402 fix (Genio 700 / MT8390 on Xenon) does not transfer in any form. Any EFT work on Cesium goes through VIA/CVTE for the VL122, or through re-routing the harness to a root port (§4, Cesium-specific items).
- The brainboard attached when that Cesium data was taken was a **Quartz**, not a Stannite: `213c:0003 "iFIT-LargeX" v3.03`, one vendor-class (255) interface, two 64-byte interrupt endpoints at 1 ms, no CDC, no USB audio interface (`hasAudio=false`). Treat that as the Quartz reference descriptor. The Stannite descriptor verified on Xenon in this report is `213c:0006 "LargeX-Stannite" v4.04` with the same vendor-class control interface plus UAC audio interfaces (§1). A Stannite-on-Cesium bugreport has not been seen yet.
- Android's `UsbPortManager` shows a single Type-C `port0` (dual, `connected=false`), which is the OTG/charger port, not the brainboard path.
- Cesium also holds a permanent `ssusb.wakelock` and never suspends, which would mask the runtime-PM variant of hypothesis 1 if it exists there; but with a hub in the path, a hub upstream reset is an additional candidate for a long recovery that does not exist on Xenon.

## 7. Open questions, answered as far as the data allows

- **Hub or mux, and does the 2024 tuning apply?** Xenon: direct root port on a host-only Genio 700 xHCI (`usb 1-1`, no hub, no TCPC). The tuning applies to this port only if CVTE applied it to that PHY instance; they must confirm, and confirm the register affects a full-speed link. Cesium: brainboard behind the VL122 hub (`6-1.3`), so SoC tuning cannot reach it at all.
- **What holds the link down for ~6 minutes?** An active loop, not a dead link: the kernel enumerates the Stannite successfully every 1.0025 s and loses it within tens of ms, 2,108 times on 05-11, until a once-per-126-cycles event lets an enumeration hold; glassos then connects 1.5 s later. Not usbcore, not glassos. Whether the host port/PHY or the Stannite firmware is driving the cycle is undecided; the one kernel-level recovery captured (05-06) has the host-side signature, the cycle's regularity has a device-watchdog feel. One `dmesg` capture during the loop, or a scope on D+/VBUS, decides it (§2d item 4).
- **Does Cesium share the port design?** No (§6): Xenon is a root port, Cesium is a hub downstream port. BRAIN-814 is an X30 connector problem, not a Cesium USB weakness.
- **Which audio tickets are which class?** §5: CRY-657 = USB link; BRAIN-824 = brainboard FW/amp mute (self-recovering); BRAIN-828/832/833 = amplifier hardware (latching); BRAIN-814 = audio-board connector hardware with an OS-routing symptom.

## 8. Proposed CRY-657 comment (for review, not posted)

> Re "is this still an issue on latest Stannite / Cesium": the 05-06 bugreport shows the failure is on the tablet host side, not in Valinor and not in the Stannite descriptors. On Xenon the Stannite sits directly on root port 1 of a host-only Genio 700 xHCI (`usb 1-1`, full-speed, no hub, no Type-C controller on that path), so the 2024 USB-PHY EFT tuning from BRAIN-402 can reach this port, but only if CVTE applied it to that PHY instance; we need CVTE to confirm which instance was changed. On Cesium the brainboard is behind the VL122 hub (`6-1.3`), so SoC PHY tuning cannot reach it there and the question becomes the hub's downstream-port behaviour under burst (VIA/CVTE) or re-routing the harness to the direct V34/V35 pair. The 05-11 Eru log shows what the "~6 minutes after the test" actually is: the kernel enumerates the Stannite successfully once every 1.0025 s and loses it again within tens of milliseconds, over 2,000 times in a row, until once every ~126 cycles an enumeration holds; the debounce build then connects 1.5 s later, exactly as designed (both recoveries, 11:00:12 and 11:25:22, happened that way). So neither usbcore nor glassos has a backoff; the link is being torn down and rebuilt by a very regular cycle that the burst starts and that persists for minutes at 1.0/1.4 kV. Whether the host port/PHY or the Stannite firmware is driving that cycle is the one open question: the only kernel-level recovery we have (05-06) shows the host-side signature (`usb usb1-port1: disabled by hub (EMI?), re-enabling...`), but the cycle's regularity also fits a device-side USB reset loop with a ~2 min watchdog. Every one of 380 enumerations across both runs carried a valid 213c:0006 "LargeX-Stannite" descriptor (PID 6 is the real Stannite PID), so there is no descriptor corruption. Cesium uses a different SoC (MT8371) and has a hub in the brainboard path, so it needs its own EFT run; BRAIN-814 turned out to be an X30 audio-board connector issue, not a Cesium USB weakness. Proposed next steps: (1) re-run one burst on Xenon with the debounce build and capture `adb shell dmesg` (or a USB analyzer trace) during one minute of the loop, before anything is touched; that single capture assigns the owner. (2) In parallel, ask the Stannite team whether FW 4.04 has a ~1 s USB re-attach path and a ~2 min watchdog, and ask CVTE to explain a 1.0025 s port error/re-enumeration cycle on xhci1 and to provide a port power-cycle hook Eru can call. (3) Open the OS ticket to CVTE for the Xenon PHY-instance confirmation and the `dumpsys usb` crash regardless. (4) On Cesium + Stannite, run an A/B EFT test of the hub path versus the direct V34/V35 pair and raise the VL122 downstream-port question with VIA/CVTE.

## 9. Requests to the test team for the next run

1. Re-upload Jira attachment 242591 (`CVTE-CVTEMediatekXenon1_2026-05-11_09.51.10.zip`) to Drive, or allow `ifitdev.atlassian.net` in this environment's network settings. Its `dmesg.log` is the only existing kernel record of the loop; if it covers 10:45–11:25 it answers host-vs-device without a new test.
2. On the next run, while the link is "dead" and before plugging anything in: `adb shell dmesg > dmesg_loop.txt` over Wi-Fi ADB (the loop is visible as one `new full-speed USB device` per second), plus `ls -l /sys/bus/usb/devices/` and `cat /sys/bus/usb/devices/usb1/1-0:1.0/usb1-port1/state`. If a USB 2.0 analyzer or a scope is available, one minute on D+ and VBUS at the Stannite connector during the loop is conclusive.
3. Record the generator program (levels, polarity, dwell per step) and the exact wall-clock moment the operator judged each test "finished", so the loop's persistence after the last burst can be measured exactly.
4. Ask the Stannite firmware team for a UART trace during one application (§4).

## 10. Hub checklist to apply to every future bugreport (from the 2026-10-02 addendum), with the 05-06 Xenon result

| Check | How | 05-06 Xenon result |
|---|---|---|
| Is there a hub between the SoC and the brainboard? | Look for a hub-class device (`mClass=9` in `UsbHostManager`, `bDeviceClass 09`), a VIA vendor ID (`idVendor=2109`), or a dotted device path (`1-1.2`) versus a direct one (`1-1`) | No hub: path `1-1`, no class-9 device, no 0x2109 anywhere, all 1,820 device-node references on bus 001 |
| Which PHY is tripping during the burst? | Disconnects logged against the hub's downstream port (`hub 1-1:1.0: port N …`) versus the root hub (`usb usb1-port1 …`) | Root hub: `usb usb1-port1: disabled by hub (EMI?), re-enabling...` |
| Does the hub itself reset during the burst? | A `USB disconnect` of the hub device followed by re-enumeration of everything below it | Not applicable on Xenon (no hub); mandatory check for Cesium |
| Hub identity for the vendor inquiry | `idVendor/idProduct/bcdDevice` of the hub | Not applicable on Xenon; on Cesium capture `cat /sys/bus/usb/devices/6-1/{idVendor,idProduct,bcdDevice,product}` |
| Which brainboard was attached? | `vidpid` line: `213c:0003 "iFIT-LargeX"` = Quartz (no audio); `213c:0006 "LargeX-Stannite"` = Stannite (with UAC audio) | Stannite, FW 4.04 (both runs) |
| Is the enumerate-and-drop loop present? | `UsbHostManager: Removed device at /dev/bus/usb/001/NNN was already gone` once per second with NNN incrementing; survivors (`USB device attached`) every ~126 cycles at a fixed NNN | 05-06: 1,139 cycles in the 26 min logcat covers; 05-11: 2,108 cycles, period 1.0025 s, survivors at dev 033 then 039, recoveries on survivor cycles |
| Which side is looping? | In `dmesg`, each cycle starts with `usb usb1-port1: disabled by hub (EMI?)` / port reset / `-71` (host) or with a plain `usb 1-1: USB disconnect` (device dropped pull-up) | Undetermined: no dmesg covers a loop period yet |
