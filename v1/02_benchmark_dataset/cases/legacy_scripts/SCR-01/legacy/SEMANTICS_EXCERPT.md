# Excerpts from legacy_system/SYSTEM_OVERVIEW.md (Meridian CRM 4.2)

## 4. CRMScript — semantics

Directory: `scripts/`. BASIC-like, line-oriented; case-insensitive keywords; `'` starts comment.
Statements: `LET var = expr`, `IF expr THEN ... [ELSE ...] END IF`, `FOR EACH row IN <TABLE> [WHERE expr] ... NEXT`
(iterates live rows, ordered by primary key ascending), `UPDATE row SET col = expr`,
`INSERT INTO <TABLE> (cols...) VALUES (exprs...)`, `CALL AUDIT(code, entity_id)`,
`CALL HTTPPOST(endpoint_name, payload_expr)`, `RETURN expr`, `EXIT FOR`.
Expressions use VRL operators/functions plus string concatenation `&` and the additional builtins
`FIXED(s, w)` (left-align, space-pad, truncate to width w), `ZPAD(num, w)` (round half-up to integer,
right-align, zero-pad to width w), `CHR(n)` (character from code point), and `DATEDIFF(d1, d2)`
(whole days d1 − d2 for `YYYYMMDD` strings; 0 if either is the `00000000` sentinel). Numeric division by zero
yields 0 and logs audit `SCRIPT_DIV0` (legacy quirk that migrations must preserve or explicitly
modernize per the case's target spec). Variables are dynamically typed; uninitialized variables
read as empty string.

## 2. VRL expression semantics (used inside CRMScript expressions)

- Comparisons (`=`, `<>`, `<`, `<=`, `>`, `>=`), arithmetic, `AND`, `OR`, `NOT`;
  functions include `NVL(x, default)` (returns default when x is empty/missing).
- Empty string in numeric comparison coerces to 0. Date comparisons are lexicographic on
  the `YYYYMMDD` string, with sentinel `00000000` treated as "no value".

## 1. Legacy conventions (relevant subset)

- Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
- Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- Amounts stored as `NUMBER(15,2)` in the account's currency.
- Soft delete: `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them unless stated.
- ORD_LINE key is (ORD_ID, LINE_NO).
