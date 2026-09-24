# NordicTrack RW900 (NTRW19147) Replacement Console – Production Fire Risk Analysis

**Console:** ERWNT19147UX, Icon P/N 437196 (EBOM Rev C, 4/15/2022)  
**PCBA:** "4 Little Pigs Universal", SCH ZH0106 Rev C, PCB ZH0107 Rev A  
**Block diagram:** ZH0818 Rev -  
**Context:** CPSC fast-track recall RP250562 (Oct 2025) of ~44,800 rowers for the original "3 Little Pigs" console overheating/igniting (8 incidents, 2 fires, 6 smoke/melt, $6k+ damage). Remedy is a technician-installed replacement console kit (1005091K). Post-remedy tracker (7/7/2026 export) shows 5 distinct replacement consoles that smoked or caught fire, mostly within seconds of first power-on.  

Sources reviewed: ZH0106 schematic (7 sheets + PCB), ZH0818 block diagram, EBOM 437196, CPSC press release draft, post-remedy incident tracker.

---

## 1. Summary

The 4 Little Pigs board is a re-stuff of the earlier "4 Little Pigs XA Rev A" design (ZH0106 Rev 1 note: "copied from 4 Little Pigs XA Rev. A, stuff all circuits for a universal board"). The only changes since release are cosmetic to fire risk: four electrolytics swapped to ceramics (Rev B), a buzzer resistor value (Rev C), and the tablet SKU (EBOM Rev C). Nothing was added to address the recall failure mode, and the root cause of the 3 Little Pigs fires is still unknown.

The dominant structural weakness is that **the console has no on-board overcurrent, overvoltage, or reverse-polarity protection on the 12 V input**. Raw VIN from the wall adapter is bused, through hand-soldered wires and 0 Ω jumpers, to the tablet, a buck converter, two linear regulators, and a fan driver. Any single short on that bus (solder bridge, cracked MLCC, wrong adapter, harness mis-pin) is limited only by whatever the customer's adapter will deliver. That is fully consistent with the field pattern: a flash and smoke within ~30 s of the first plug-in, and a second console working normally afterward.

The five smoke/fire events are also strongly correlated with installation conditions the board does not defend against: two were self-installs without the new harness, one used a non-iFIT adapter measured at 23.5 VDC, and one had the upright wire removed and replaced. Only one (Ji Ni, case 24556296) had a confirmed correct 12 V adapter and new harness and still smoked.

---

## 2. Scoring method

FMEA-style: **Severity (S)** 1–5, **Occurrence (O)** 1–5, **Detectability (D)** 1–5 (5 = will not be caught by current design/test/inspection). **Risk Priority Number = S × O × D** (max 125). Occurrence is judged from the design, the EBOM, and the five field events; the fleet incident rate is stated as well under 1 %.

---

## 3. Top 5 production fire risks (ranked)

### #1 — Unprotected 12 V input bus (RPN 5 × 4 × 4 = 80)

**Where:** IO sheet (sheet 6): HD4 pins 9/10 VIN, 11/12 GND (DNS header, wires soldered to pads); "Tablet Power" HD13 via R51/R52 0 Ω 1210; Audio sheet TPS54231 VIN with CA4 47 µF **16 V** 1210 ceramic; LM2940 via R21; LM1117 via D1 B130.

**Findings:**

- No fuse, PTC, TVS, or reverse-polarity element anywhere on VIN. D1 (B130) protects only the 3.3 V LDO branch. The tablet feed, the audio buck, the 5 V LDO and the fan driver see raw adapter voltage of either polarity.
- CA4 (47 µF, 16 V, X5R, 1210) sits directly across a nominal 12 V rail. Hot-plugging a 12 V adapter through the ~12-inch pigtail plus the frame harness produces an L-C ring that can approach 2× VIN; a 16 V-rated MLCC has essentially no margin. Any adapter above ~13 V (Cavallaro case: 23.5 V, fluctuating) exceeds its rating outright. MLCC over-voltage failure is a hard short followed by localized heating until the part or the trace opens, i.e. "flash then smoke."
- R51/R52 (0 Ω, 1210, ¼ W, "Any") carry the full tablet current. The EBOM specifies no current rating; generic 1210 jumpers are rated 1–3 A depending on vendor. The 21.5 in Argon2 tablet load is not stated in any document. If the tablet draws near or above the jumper rating (plausible at display start-up), these become the hottest parts on the board by design.
- The wrong-adapter case was survivable only because the adapter sagged to 2 V under the fault; a stiffer adapter would have delivered continuous power into the shorted node.

**Why it ranks first:** it is the enabler for almost every other item on this list. With a fuse and TVS at the entry point, most downstream single faults become an open fuse instead of a fire.

**Actions:** Add a fuse or PTC (sized for tablet + amp start-up) and a 14–16 V TVS (e.g. SMBJ14A) at HD4 VIN; add series or shunt reverse protection; raise CA4 to 25 V or replace with electrolytic + small MLCC; measure tablet inrush/steady current and specify R51/R52 with a rated current (or delete them and use copper). Capture the hot-plug waveform at CA4 on the real harness.

### #2 — Hand-soldered power wires on DNS pads with hot-melt glue (RPN 5 × 3 × 4 = 60)

**Where:** EBOM off-board section and manufacturing note 6. HD4 (12-pin dual-row 2.5 mm), HD13 (tablet 12 V), HDA1/HDA2 (speakers), HDA3 (tablet audio) are all **DNS**; the wires are soldered directly to the header pads and "secured with hot melt glue."

**Findings:**

- On HD4 the two VIN pads (9, 10) are adjacent to two GND pads (11, 12) at 2.5 mm pitch, with TACH and NC on the neighboring row. Eleven hand-soldered 22 AWG stranded wires into that field is a solder-bridge / stray-strand short across the adapter waiting to happen. Inspection is visual only (IPC-A-610 class II), and there is no functional power-on current-signature test called out in the EBOM.
- Wire color coding is a trap: on the 8-pin pigtail **black and green carry +12 V** while blue and black/white carry GND; on the 6-pin pigtail black is MTR−. A supplier operator following normal color intuition will swap power and ground.
- Hot-melt (EVA) glue is not flame-rated and is placed directly on the highest-energy joints on the board. It also creeps at the temperatures a shorted joint reaches, so it neither restrains the wire nor slows a fire.
- Field data: the two cases where the new harness was confirmed *not* installed (Groh) or its status is unknown (West, Philbrook) point at the console-to-frame interface, but the Ji Ni case (new harness, 12 V confirmed) shows the problem is not only the legacy harness.

**Actions:** Stuff the JST XA headers (they are already in the EBOM as DNS) instead of soldering leads; if soldering is retained, add a 100 % powered test on a current-limited 12 V supply with a current-signature pass/fail; replace hot-melt with a UL-recognized RTV or a mechanical strain relief; change VIN wire colors to red/orange.

### #3 — R21 (15 Ω, 2 W, 2512) acting as an un-rated fuse for the 5 V rail (RPN 4 × 3 × 4 = 48)

**Where:** IO sheet, "Tablet Power / Ext Audio PWR" area: VIN → R21 15 Ω → RG2 LM2940-5.0 → 5VDC → U3 BD6211 H-bridge (resistance motor, MTR+/MTR−, C12 1000 µF).

**Findings:**

- Every milliamp the resistance motor draws flows through R21. With LM2940 at ~0.5 V dropout, the rail can supply at most ≈ (12 − 5.5)/15 ≈ 0.43 A before it collapses. At 0.4 A R21 dissipates 2.4 W, already above its 2 W rating, on a board inside a sealed plastic console with no fan.
- Under a shorted 5 V rail (BD6211 failure, motor lead short in the frame harness, C12 short) R21 sees 12 V / 15 Ω = 0.8 A → **9.6 W in a 2 W part**. Stackpole RHC is a high-power thick-film, not a fusible or flame-proof type; at 5× overload it chars the PCB and can ignite flux/glue residue before it opens.
- The LM2940 has thermal shutdown, but R21 is upstream of it and is the first thing to burn.

**Actions:** Replace R21 with a fusible flame-proof resistor or a fuse; specify motor stall current and size the rail for it; or move the H-bridge onto the TPS54231 5 V buck and delete R21/RG2.

### #4 — Large-case MLCC cracking on power rails (RPN 4 × 2 × 4 = 32)

**Where:** CA4 47 µF 16 V 1210 (VIN); CA2/CA3 47 µF 16 V 1210 (5VDC_Audio, changed from electrolytic at Rev B, ECN 91521-06); C4/C18/C19 10 µF 1206 (VIN and 5 V); CA31/CA33 100 µF 6.3 V 1206 (headphone, Rev B).

**Findings:**

- 1206/1210 MLCCs are the most flex-crack-prone SMD parts. This board is mounted by four #4-40 screws into brass inserts in plastic, carries eleven hand-soldered wires that are pulled during harness routing, and then rides a 21.5 in tablet through ISTA 3A drop testing. A flex crack at CA4 is a latent 12 V short that can appear at first power-on or months later; a crack at CA2/CA3 loads the buck into its current limit at a single hot spot.
- The Rev B change (electrolytic → ceramic at CA2, CA3, CA31, CA33) was presumably for reliability or supply, but it increased the ceramic-crack short population. No soft-termination (flexible-electrode) MLCC is called out in the EBOM for any of these.
- 16 V rating on a 12 V rail is not a derated design for a consumer product on an unregulated-transient input.

**Actions:** Specify soft-termination MLCCs for all 1206/1210 caps on VIN and 5 V; raise voltage rating to ≥ 25 V on VIN; review PCB keep-out from mounting holes and wire pads; consider a small electrolytic in parallel so the ceramic can be reduced to 10 µF.

### #5 — Regulator stability / component-errata items that raise dissipation (RPN 3 × 3 × 4 = 36)

**Where:** RG2 LM2940-5.0 with C19 10 µF X7R ceramic; RG1 LM1117-3.3 (multi-source: TI LM1117, Diodes AZ1117C/IH, ST LD1117, Infineon IFX1117) with C5 22 µF **Y5V** ceramic.

**Findings:**

- **LM2940 requires ≥ 22 µF output capacitance with ESR between 0.1 Ω and 1 Ω** (TI datasheet). C19 is 10 µF ceramic with ESR in the milliohm range, violating both limits. The expected result is output oscillation, elevated regulator and R21 dissipation, and noisy 5 V into the H-bridge. Not a direct ignition source by itself, but it stacks on #3.
- LM1117 (TI) is specified with a 10 µF tantalum output; ceramic stability is vendor-dependent. Y5V dielectric loses 60–80 % of its capacitance at 3.3 V bias and at temperature, so C5 may be ~5 µF in service. Because four different regulator vendors are approved as "or equivalent", stability varies with whichever part the CM stuffed.
- TPS54231 is fine electrically (Vout set to 4.99 V by RA1/RA4, EN floating with internal pull-up is allowed), but its 28 V rating means it survives a 23.5 V adapter while its 16 V input cap does not.

**Actions:** Change C19 to ≥ 22 µF electrolytic (or ceramic plus series ESR) per the LM2940 datasheet; change C5 to X5R/X7R and limit RG1 to ceramic-stable parts; add these to the incoming-inspection alternate list.

---

## 4. Other findings (not in top 5, still worth tracking)

| Item | Observation | Risk |
|---|---|---|
| C12, CA16 (1000 µF, 6.3 V, 85 °C GP electrolytic) at 5 V | 79 % voltage derating, general-purpose 85 °C grade inside a sealed console. CA16 must be laid down and hot-glued (EBOM note 10). Reverse insertion of a radial electrolytic is the textbook "smoke at first power-on" and is not a power/ground reversal, so it would not show up in that check. | Smoke/vent event; verify polarity silkscreen vs. pick-and-place and add to AOI. |
| Ferrite beads RA2/RA5/RA6/RA7 (0603, 1 A) on speaker outputs | 5 V class-D into 4 Ω can peak above 1 A. Beads saturate and heat. | Low; audio-rate. |
| QF1 TIP32 linear fan driver from VIN, no heatsink | Stuffed on a rower console that has no fan. Harmless if nothing is plugged into HDF1/HDF4, but a fan or short on those pads dissipates VIN × I in a bare TO-220. | Low; consider DNS for this SKU. |
| VA2205 (VIVA) class-D amp | Single-source, limited datasheet, no thermal data. Exposed-pad part; pad soldering quality determines temperature. | Medium unknown. |
| No PCB flammability, CTI, or copper-weight spec in EBOM | EBOM has solder, ESD, RoHS, packaging notes but never states UL94 V-0 laminate or minimum trace width for the VIN path. | Gap for a product under a fire recall. |
| Tablet (Argon2, 421914) is a black box | "Icon assist buy, no cost." Its input stage sees raw VIN through R51/R52 with no protection. Field note "back side of the screen flashed" could be tablet, not PCBA. | Must be included in returned-unit teardown. |
| RS-485 / DMK / Pulse / membrane inputs | 3.3 V, series-resistor protected. | Negligible. |

---

## 5. Correlation with post-remedy field events

| Case | Installer | Harness | Adapter | Outcome |
|---|---|---|---|---|
| Groh 24416540 / 24520553 | Self | Not installed | Unknown (12.1 V measured later) | Fire, smoke from vents at ~30 s |
| West 24421918 | Technician | Unknown | Unknown | Smoke on plug-in |
| Philbrook 24491366 | Self ("plug and play") | Unknown | Unknown | Flash at back of screen, heavy smoke |
| Ji Ni 24556296 | Technician | New harness installed | Correct 12 V | Burning smell, smoke, lost power |
| Cavallaro 24503091 | Technician | Legacy | Wrong, 23.5 V non-iFIT | Burning smell, 2 V at console |

All five occurred at or within minutes of first power-on and none recurred with a second console on the same rower. That pattern points to a population of latent unit-level defects or install-condition sensitivities (items #1, #2, #4 above) rather than a wear-out mechanism, and it means a **100 % powered current-signature test at the CM on a current-limited supply** would have screened most of them. The Ji Ni unit is the highest-value teardown because it removes the harness and adapter variables.

---

## 6. Recommended immediate actions

1. **Recover and section the five smoked consoles** (at least Ji Ni and Groh). Root cause is currently unknown; the burned component will rank this list definitively.
2. **Add input protection** to the next PCB spin: fuse/PTC + TVS + reverse protection at HD4 VIN; ≥ 25 V soft-termination input MLCC.
3. **Stuff the connectors** already in the EBOM (HD4, HD13, HDA1–3) instead of soldering leads; if not possible, fix wire colors and add a powered end-of-line test.
4. **Fix the regulator errata**: R21 → fusible/flame-proof or fuse; C19 → ≥ 22 µF with LM2940-compliant ESR; C5 → X7R; restrict RG1 alternates.
5. **Specify the tablet load** and rate R51/R52 (or remove them).
6. **Add UL94 V-0 laminate and flame-rated adhesive** to the EBOM; remove hot-melt from power joints.
7. **Kit-level controls**: ship the adapter in every 1005091K, add a "do not use old adapter or harness" label on the console bag, and do not ship kits to self-installers where the tracker shows no technician coverage.

---

## 7. Assumptions and gaps

- Tablet current draw, resistance-motor stall current, and adapter part number/current rating are not in any supplied document; the R21 and R51/R52 dissipation numbers above use 12 V nominal and conservative estimates.
- The PCB layout (ZH0107) was only available as a low-resolution image; trace widths, clearances, and MLCC keep-outs were not verified.
- The failure analysis of the original 3 Little Pigs consoles was not provided, so this analysis cannot confirm that any of the five items above is the recall root cause. Items #1–#3 are the ones most consistent with a console that "overheats and ignites."
