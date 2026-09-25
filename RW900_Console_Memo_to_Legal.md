**Attorney Client Privilege - Work Product - Prepared at the Direction of Counsel - CONFIDENTIAL - DO NOT SHARE**

# Memo: Engineering Preliminary Assessment – RW900 Replacement Console Smoke/Fire Events

**To:** Legal  
**From:** Engineering  
**Date:** September 25, 2026  
**Re:** Post-remedy console incidents, NTRW19147 recall (RP250562); replacement console ERWNT19147UX / "4 Little Pigs Universal" PCBA  
**Revision:** Rev 3, September 25, 2026

## Purpose

You asked for Engineering's view on the five post-remedy smoke or fire events logged in the console replacement tracker. This memo summarizes a desk review of the replacement console design documents and the incident tracker. It is preliminary and should be read with the caveats below.

## What we reviewed

Schematic ZH0106 Rev C, block diagram ZH0818, EBOM 437196 Rev C, the CPSC press release draft, and the 7/7/2026 incident tracker export. We have not examined any returned hardware, the PCB layout at full resolution, the tablet module, the power adapter, or the failure analysis of the original consoles.

## Preliminary observations

1. The replacement console carries the same basic power architecture as the recalled design. Changes since release are limited to capacitor type, one resistor value, and the tablet SKU. None targets the recall failure mode, and the root cause of the original fires remains unknown to us.
2. The board has no on-board fuse, transient suppressor, or reverse-polarity protection on the 12 V input. Fault current in a short is limited only by the customer's power adapter.
3. Several second-order design and component-selection items could plausibly produce smoke at first power-on: a 16 V-rated ceramic capacitor across the 12 V input, power wires hand-soldered onto unpopulated connector pads with hot-melt glue, a series resistor operating near its power rating on the motor supply, and regulator output capacitors outside the manufacturer's stability requirements.
4. Field conditions vary across the five events. Two were self-installed without the new harness, one used a non-iFIT adapter measured at 23.5 V, one had the upright wire replaced, and one (case 24556296) had a confirmed correct adapter and new harness and still smoked. All five occurred at or shortly after first power-on and none recurred with a second console.

## Note on the power adapter and "output protection did not trip"

The external adapter is specified at 12 V, 4 A (ZH1381). Its overcurrent protection, like that of any supply in this class, responds only to a hard, low-impedance short. The failure modes Engineering considers most plausible are resistive faults that draw well under the trip threshold while dissipating enough to char a board. The fact that the adapter did not trip is therefore consistent with a console-side fault and should not be read as evidence that the console was not at fault or that the adapter was healthy. ZH1381 also shows the preferred US adapter construction is not a limited-power-source type, so the console's lack of its own fuse matters more, not less.

## Note on installation error

The most likely installation error is reuse of the original rower's upright wire harness with the new console. iFIT's service notes flag "did not install wire harness" as the deviation in two cases, and two customers described the swap as "plug and play," which implies the legacy connectors mate with the new console. If the legacy harness pin assignment differs, it would apply 12 V to the wrong pins, which the console does not protect against. The second most likely error is use of a non-iFIT power adapter (one case, 23.5 V). One case (24556296) fits neither and still points at the console. Kits reaching the home before the technician, packaged without consumer-facing warnings, are the process condition behind the self-installs. Confirming the harness hypothesis requires the original console's harness drawing, which Engineering has requested.

## Important caveats

- **This analysis is speculative.** It identifies design characteristics that are consistent with the reported symptoms. It does not establish that any of them caused any incident, and it does not rule out installation error, adapter or harness condition, the tablet module, or a manufacturing defect in an individual unit.
- **No physical evidence has been examined.** Without teardown of the affected consoles, no conclusion about causation should be drawn from this memo.
- **Vendor follow-up is required for confidence.** The console is designed and built by Malata. Before we can state anything with confidence we need from Malata: the production test records and current-signature or burn-in data for the affected serial numbers, the PCB layout files, the tablet module's electrical specification and input protection, any internal failure analysis on the original 3 Little Pigs consoles, and any field-return or scrap data on this PCBA. We also need Malata's confirmation of which alternate regulator and capacitor sources were actually stuffed on the affected lots, and from the adapter supplier the specific model, its overcurrent and overvoltage thresholds and behavior, and whether the units shipped in the recall kit carry the LPS mark.

## Recommended next steps

1. Recover the five affected consoles, adapters, and harnesses. Prioritize case 24556296.
2. Open a formal failure-analysis request with Malata covering the items above, with an agreed timeline.
3. Hold on any design-change communication until the vendor data and teardown results are in hand.
4. Engineering will update this assessment when the vendor response and teardown results are available.

Please treat the accompanying detailed analysis as an internal engineering working document, not a finding.
