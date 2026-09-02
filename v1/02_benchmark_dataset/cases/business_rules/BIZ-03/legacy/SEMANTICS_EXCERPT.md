# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated. Booleans: blank CHAR(1) means `N`. Empty string in numeric context
  coerces to 0; `NVL(x, default)` returns `default` when `x` is empty/missing.
- ORD_HEADER.STAT_CD codes: E=Entered; A=Approved; S=Shipped; I=Invoiced; X=Cancelled.
- ORD_HEADER.TOT_AMT is denormalized: sum of line EXT_AMT after header discount.

## 2. VRL — rule in scope (excerpt)

ORD-003 (UPDATE): `NOT (OLD.STAT_CD = 'I' AND STAT_CD <> 'I' AND STAT_CD <> 'X')` else
`E5003 "Invoiced order can only be cancelled"` — once invoiced, an order may only stay
`I` or move to `X`.

## 3. Workflow engine — semantics (excerpt)

A transition fires iff current state = `from`, event matches, and guard (if any) is TRUE.
Actions run in document order. The `order_fulfilment` transition `I -> X` on `cancel`
performs `<audit code="ORD_CANC_INV"/>` then `<notify template="credit_note"/>`.

## 4. CRMScript — order_totals.crms (excerpt of behavior)

The nightly recompute iterates live, non-cancelled orders (`WHERE DEL_FLG='N' AND
STAT_CD <> 'X'`): per live line, `EXT_AMT = NVL(QTY,0) * NVL(UNIT_PRC,0)`; then
`TOT_AMT = total * (100 - NVL(DISC_PCT,0)) / 100`, **rounding half-up to cents**, and
`CALL AUDIT('ORD_RETOTAL', ord.ORD_ID)` only when TOT_AMT actually changed.
