# Memo: Engineering Preliminary Assessment – RW900 Replacement Console Smoke/Fire Events

**To:** Legal  
**From:** Engineering  
**Date:** September 24, 2026  
**Re:** Post-remedy console incidents, NTRW19147 recall (RP250562); replacement console ERWNT19147UX / "4 Little Pigs Universal" PCBA  
**Privileged & Confidential – Prepared at the Direction of Counsel**

## Purpose

You asked for Engineering's view on the five post-remedy smoke or fire events logged in the console replacement tracker. This memo summarizes a desk review of the replacement console design documents and the incident tracker. It is preliminary and should be read with the caveats below.

## What we reviewed

Schematic ZH0106 Rev C, block diagram ZH0818, EBOM 437196 Rev C, the CPSC press release draft, and the 7/7/2026 incident tracker export. We have not examined any returned hardware, the PCB layout at full resolution, the tablet module, the power adapter, or the failure analysis of the original consoles.

## Preliminary observations

1. The replacement console carries the same basic power architecture as the recalled design. Changes since release are limited to capacitor type, one resistor value, and the tablet SKU. None targets the recall failure mode, and the root cause of the original fires remains unknown to us.
2. The board has no on-board fuse, transient suppressor, or reverse-polarity protection on the 12 V input. Fault current in a short is limited only by the customer's power adapter.
3. Several second-order design and component-selection items could plausibly produce smoke at first power-on: a 16 V-rated ceramic capacitor across the 12 V input, power wires hand-soldered onto unpopulated connector pads with hot-melt glue, a series resistor operating near its power rating on the motor supply, and regulator output capacitors outside the manufacturer's stability requirements.
4. Field conditions vary across the five events. Two were self-installed without the new harness, one used a non-iFIT adapter measured at 23.5 V, one had the upright wire replaced, and one (case 24556296) had a confirmed correct adapter and new harness and still smoked. All five occurred at or shortly after first power-on and none recurred with a second console.

## Important caveats

- **This analysis is speculative.** It identifies design characteristics that are consistent with the reported symptoms. It does not establish that any of them caused any incident, and it does not rule out installation error, adapter or harness condition, the tablet module, or a manufacturing defect in an individual unit.
- **No physical evidence has been examined.** Without teardown of the affected consoles, no conclusion about causation should be drawn from this memo.
- **Vendor follow-up is required for confidence.** The console is designed and built by Malata. Before we can state anything with confidence we need from Malata: the production test records and current-signature or burn-in data for the affected serial numbers, the PCB layout files, the tablet module's electrical specification and input protection, any internal failure analysis on the original 3 Little Pigs consoles, and any field-return or scrap data on this PCBA. We also need Malata's confirmation of which alternate regulator and capacitor sources were actually stuffed on the affected lots.

## Recommended next steps

1. Recover the five affected consoles, adapters, and harnesses. Prioritize case 24556296.
2. Open a formal failure-analysis request with Malata covering the items above, with an agreed timeline.
3. Hold on any design-change communication until the vendor data and teardown results are in hand.
4. Engineering will update this assessment when the vendor response and teardown results are available.

Please treat the accompanying detailed analysis as an internal engineering working document, not a finding.
