# CSA Group review feedback log

Running record of feedback from weekly CSA Group meetings and how each item was handled in the asset inventory.

## 2026-10-02 meeting

CSA Group frustrated at pace; progress acknowledged. Allen polishing the Sheet directly; reconcile pass to follow.

### F-001 — Asset 57 (row 58), HackerOne H1-456 hardcoded root password: OUT OF SCOPE

- **Feedback:** the finding applies to legacy Malata-built tablets (Argon2/Neon era), not Xenon or Cesium. Should not sit in the register as a Critical open gap on the product under assessment.
- **Decision:** mark asset 57 NOT APPLICABLE (grey, text retained for traceability), same treatment as asset 7.
- **Dependent cells to soften** (currently cite row 57 as a live Critical finding):
  - Asset 8 col M — downgrade from "CRITICAL OPEN GAP tied to confirmed finding" to OPEN, ODM confirmation pending; H1-456 as legacy background only.
  - Asset 6 col M — keep precedent note, drop "see new row 57" pointer.
  - Interfaces row 7 col H — keep, add legacy qualifier.
  - Where to Look step 1 col E — keep, add legacy qualifier.
- **Gap count impact:** removes one Critical (7 → 6).
- **Status:** awaiting Allen's edits in the Sheet; reconcile after.
