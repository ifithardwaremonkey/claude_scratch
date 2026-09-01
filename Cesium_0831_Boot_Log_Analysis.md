# Cesium Tablet (AOSP 15 / MT8371) — 0831 Boot Log Analysis

**Analyst input set:** `1st_boot_0831_cesium.log` (logcat, 13,202 lines), `1st_boot_0831_dmesg.log` (9,461 lines), prior analysis notes ("Analyze logcat, AOSP 15, MT8371 CPU…"), Drive metadata for VKC1 zips.
**Date of capture:** 2026-08-31 ~04:24–04:28 UTC (≈ Aug 30, 10:24 PM MDT).

> **Coverage note:** Only the first-boot logcat + dmesg pair was retrievable in this session. The WiFi-connection logcat/dmesg, the two wifi-adb logcats, the Valinor kiosk logs + bugreport, and the analysis PDF were not accessible (the multi-GB `VKC1_20260831*.zip` files exceed the Drive connector's 10 MB download limit, and `VKC1_20260831_20260831A.zip` turned out to be a **signed OTA update package** — payload.bin + metadata — not logs). Findings from those captures are cross-referenced from the prior analysis notes and are marked *(reported, unverified)*.

---

## 1. Timestamp correlation & clock forensics (chronological)

The two logs use different clock bases, and the wall clock is stepped twice during boot. Reconstructed true sequence:

| Real (UTC) | dmesg shows | logcat shows | Event |
|---|---|---|---|
| 04:24:31 | Aug 31 04:24:31 | — | Kernel boot start (MT8371, Linux 6.1.145-android14). **dmesg timestamps are back-computed** from the *corrected* wall clock, so early kernel lines display 2026 dates even though the wall clock at that moment was 1970/2010. Treat dmesg times as relative-accurate only. |
| 04:24:33 | Aug 31 04:24:33 | — | `mt6397-rtc: read al time = 1970/01/01 00:00:48` → RTC is unset. Kernel then does `setting system clock to 2010-01-01T00:02:47 UTC` (MediaTek default RTC epoch). |
| ~04:24:59 | — | **01-01 00:03:00** | logcat begins — the `01-01 00:03` prefix is 2010-01-01 00:03 UTC, i.e. the 2010 MTK default epoch, **not** a corrupt log. (An earlier capture showed `12-31 18:03` — same instant rendered in UTC-6 local time.) |
| 04:25:00–01 | — | jump **01-01 00:03 → 08-31 04:25** | `PersistentNetworkTimeStore: Setting system clock from build time 1788150300000 because this device has no reliable RTC` (build time = 2026-08-31 04:25:00 UTC exactly). |
| 04:25:01.777 | — | **time steps backwards ~1.8 s** (04:25:01.777 → 04:25:00.001, logcat line 941) | The clock-set lands slightly *behind* the interim clock, so logcat is non-monotonic here. Any naive sort of this file misorders ~600 lines. |
| 04:25:04.300 | — | 04:25:04.300 | `UsageStatsService: Time changed in by 525846107 seconds` — exactly 2010-01-01 00:02:47 → 2026-08-31 04:25:00 (16.66 years). Triggers JobScheduler/UsageStats/alarm recalculation and contributes to the 22 `Slow dispatch/Slow delivery` warnings during boot. |
| 04:27:26 / 04:28:04 | end | end | logcat ends (WiFi scanning, never connected — expected on first boot, no credentials); dmesg continues to 04:28:04 with SPM unable to enter low power. |

**Root cause (clock):** the RTC (MT6359P PMIC RTC) either has no backup power path or is deliberately not trusted — the AOSP framework itself declares *"this device has no reliable RTC"* and substitutes the **build timestamp** as wall time. Every cold boot will therefore start at build time until NTP syncs over WiFi. Consequences: TLS certificate validation can fail/behave oddly pre-NTP, log correlation across devices/boots is impossible, scheduled Valinor jobs and license/entitlement checks see time warps, and each boot logs a half-billion-second time change that churns JobScheduler. **This is the single root cause behind most of the "odd timestamp stuff" across all captures.**

---

## 2. Boot narrative (first boot)

- 04:24:31–04:24:59 — kernel boot. Device-tree noise (`invalid resource` for scp/spmi/thermal NTC1-3,6; `invalid clock index`; audio `etdm read clk ao node error -22`), USB-PD `husb238: Failed to read orientation`.
- 04:24:37–04:24:49 — **camera probe: every sensor candidate fails.** `bf2557` (id reads 0x0/0xffffffff), `sp5508`, `gc05a3` — all `IMGSENSOR_PROBE miss` on every index. No camera sensor was detected on this unit at all.
- 04:25:00–04:25:05 — system_server up; WiFi HAL init logs `Unknown iface name: wlan0` (×4) and `Failed to register radio mode change callback`; WiFi firmware configs `wifi.cfg`, `wifi_sigma.cfg`, `txpowerctrl.cfg` not found on any firmware path; keystore2 `ROLLBACK_RESISTANCE_UNAVAILABLE` on importKey; **6× WindowManager Crash `IllegalStateException: Existing input consumer found: recents_animation_input_consumer`** as Quickstep (launcher3) and the iFIT launcher fight over gesture ownership; 92 `AppOpService: Blocked setUidMode … RuntimeException` during permission sync of preloaded apps.
- 04:25:08–04:25:12 — `com.ifit.eru` starts (uid 1000/system!); `com.android.launcher3` **killed and force-finished** (`change com.android.launcher3`), its TouchInteractionService scheduled for restart.
- 04:25:27 — `com.ifit.eru/.activity.PrivilegedModeActivity` launched (BAL_ALLOW_NON_APP_VISIBLE_WINDOW) — the kiosk/privilege-mode flow.
- 04:25:48 — `com.ifit.eru` (pid 3966) **force-stops `com.ifit.glassos_service`**; `com.ifit.launcher/.MainActivity` killed + force-finished; NotificationManagerService throws `Service not registered` unbinding the rivendell `MediaNotificationListenerService`.
- 04:25:49+ — launcher3 restarts, spamming `framframe` (299) / `Overrides: Bad overriden class NoSuchMethodException TaskbarModelCallbacksFactory` (253) — a vendor-patched launcher3 whose overlay overrides don't match AOSP 15 Quickstep.
- 04:26:13–14 — kernel `binder: transaction credentials failed` (×5) + `JavaBinder: FAILED BINDER TRANSACTION (parcel size = 0)` (×30): com.android.settings sends binder to **frozen** processes (error -74) — cached-app-freezer interaction.
- 04:26:24 — adbd starts, restarts once; earlier `AdbDebuggingManager: IOException: No such file or directory / Connection refused` while the socket wasn't up yet; adbd sits `Waiting for persist.adb.tls_server.enable=1` (wireless debugging off until enabled).
- 04:27:24–04:28:04 — WiFi scan loops (no join); SPM cannot enter mcusys-off due to permanent wakelocks `g520_no_system_suspend`, `disp_crtc0_wakelock`, `ssusb.wakelock`.

---

## 3. Prioritized issue list

Legend: 🔴 **blocker — must resolve before production** · 🟠 **high — fix before PVT exit / investigate** · 🟡 **low — cleanup/monitor**
Ownership: **CVTE** = BSP/kernel/OS/hardware bring-up · **iFIT** = Valinor/kiosk/launcher apps · **Joint** = device build config decided by iFIT, implemented by CVTE.

| # | Sev | Issue | Evidence | Owner |
|---|---|---|---|---|
| 1 | 🔴 | **No reliable RTC** — framework sets wall clock from build time every cold boot; 16.6-year time jump each boot; non-monotonic logcat; breaks TLS/scheduling/log forensics pre-NTP | dmesg 04:24:33 RTC=1970/2010; logcat line 940 `PersistentNetworkTimeStore … no reliable RTC`; `Time changed in by 525846107 seconds` | **CVTE** (RTC backup power / driver / `ro.build` time-source config) |
| 2 | 🔴 | **No camera sensor detected** — all 3 candidate sensors (bf2557 ×2 addresses, sp5508, gc05a3) fail ID read on every slot. If this SKU ships a camera, it is dead on this unit (I2C/power rail/driver table) | dmesg `IMGSENSOR_PROBE miss` for every candidate, ids 0x0/0xffffffff | **CVTE** |
| 3 | 🔴 | **Dual-launcher conflict** — launcher3/Quickstep and com.ifit.launcher both HOME; 6× WindowManager `IllegalStateException recents_animation_input_consumer` crashes; both launchers killed/force-finished during boot; launcher3 restart spams 550+ error lines (`framframe`, `Overrides`) | logcat 04:25:04.8 WM crashes; 04:25:12 launcher3 killed; 04:25:48 ifit.launcher force-finished | **Joint** — CVTE removes/disables launcher3+Quickstep from build; iFIT confirms kiosk HOME takeover sequence |
| 4 | 🔴 | **Missing `txpowerctrl.cfg`** (plus `wifi.cfg`, `wifi_sigma.cfg`) — TX-power control table absent means WiFi transmits at driver defaults; **regulatory/RF-certification risk** (FCC/CE test configs) | dmesg `Direct firmware load for txpowerctrl.cfg failed with error -2` on all firmware paths | **CVTE** |
| 5 | 🟠 | **WiFi HAL init race** — `Unknown iface name: wlan0` ×4, `Failed to register radio mode change callback` at HAL start; WiFi still works later, but flags a bring-up ordering bug that could intermittently fail interface setup | logcat 04:25:01.7 | **CVTE** |
| 6 | 🟠 | **keystore2 `ROLLBACK_RESISTANCE_UNAVAILABLE`** — KeyMint lacks rollback-resistant key support; importKey fails and falls back. Affects key attestation guarantees (DRM/Play Integrity if ever needed) | logcat 04:25:00.5 | **CVTE** |
| 7 | 🟠 | **AppOpService `Blocked setUidMode` RuntimeException ×92** during permission sync of preloaded 3rd-party apps (Netflix/Zoom/Amazon per earlier capture) — AOSP 15 PermissionPolicyService vs. preload method; noisy and may leave app-ops inconsistent | logcat 04:25:06+ | **Joint** (CVTE preload mechanism; iFIT owns preload list) |
| 8 | 🟠 | **iFIT service lifecycle roughness** — `com.ifit.eru` (running as uid 1000 system) force-stops `glassos_service`; NotificationListener unbind throws `Service not registered`; `UsageStatsService: Unexpected activity event` from ifit.launcher; MediaNotificationListener restart loop | logcat 04:25:48 | **iFIT** |
| 9 | 🟠 | **Binder-to-frozen-app failures** — settings → frozen process, error -74, 30× FAILED BINDER TRANSACTION + kernel `transaction credentials failed`. Freezer tuning vs. system apps issue; can cause dropped callbacks | logcat/dmesg 04:26:13 | **CVTE** (freezer config) |
| 10 | 🟠 | **Device never enters low-power** — permanent wakelocks `g520_no_system_suspend`, `disp_crtc0_wakelock`, `ssusb.wakelock` block suspend. If `g520_no_system_suspend` is intentional kiosk policy, document it; otherwise thermal/energy concern for always-on retail units | dmesg tail, repeating SPM messages | **Joint** (confirm intent, then CVTE) |
| 11 | 🟠 | **ADB socket churn** — `AdbDebuggingManager` IOException (socket not yet up), adbd double-start, wireless debugging gated on `persist.adb.tls_server.enable`. Earlier wifi-adb capture also showed `/adb_keys ENOENT` *(reported, unverified)*. Mostly benign on user builds but must be **locked down (adb off) for production** | logcat 04:25:12, 04:26:24 | **CVTE** (build config); iFIT to define production debug policy |
| 12 | 🟡 | Device-tree cleanup: `invalid resource` (scp, spmi, thermal-ntc1/2/3/6), `invalid clock index`, audio etdm clk node error -22, `husb238 Failed to read orientation`, `ccorr_prim_force_linear` read fail, `vndkcorevariant.libraries.txt` missing | dmesg boot | **CVTE** |
| 13 | 🟡 | Vendor HAL noise: `mtkpower@impl [setMode] unknown type` ×23, `MBrainLocalService notifyAppSwitch failed` ×18, PowerStats HAL uninitialized, `/proc/uid_concurrent_policy_time` missing (needs `CONFIG_CPU_FREQ_STAT` or MTK equivalent) | logcat | **CVTE** |
| 14 | 🟡 | Cosmetic AOSP noise on non-telephony hardware: `DeviceBasedSatelliteRepo` exceptions ×40, CellBroadcast lookups, `AbstrBtListPrefCtrl` errors | logcat | CVTE (config trims) |

---

## 4. Root cause summary

1. **Clock chain:** dead/unprovisioned RTC → kernel falls back to MTK 2010 epoch → AOSP overrides with **build time** ("no reliable RTC") → 16.6-year jump + 1.8 s backwards step every cold boot. This explains all cross-log timestamp anomalies in the whole 0831 capture set. Fix = make the PMIC RTC retain time (backup supply / driver) or at minimum persist last-known time (`persistent clock` / `time_detector` config). **CVTE.**
2. **HOME contention:** shipping both Quickstep-launcher3 and the iFIT kiosk launcher in the image causes the WindowManager input-consumer crash loop and the launcher kill/restart churn seen at 04:25:04–04:25:49. Fix = remove launcher3/Quickstep from the product makefile (or `pm disable` in provisioning). **Joint.**
3. **Bring-up gaps** (camera dead, WiFi cfg/TX-power tables missing, DT resources invalid) are classic PVT BSP integration gaps. **CVTE.**

## 5. Gaps / requested follow-ups

To complete the correlation you asked for, still needed (couldn't be pulled from Drive):
- WiFi-connection logcat + dmesg (Valinor start sequence)
- The two wifi-adb logcats + the analysis PDF
- Valinor kiosk app logs + bugreport (the large `VKC1_20260831*.zip` files exceed the 10 MB Drive-connector limit; note `VKC1_20260831_20260831A.zip` is actually an **OTA package**, not logs — worth renaming to avoid confusion)

Re-upload those as individual files <10 MB (or split), and the same correlation method (map everything onto UTC, anchor on the build-time clock-set event) can be extended across the full set.
