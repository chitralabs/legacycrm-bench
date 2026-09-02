# Excerpt of legacy_system/SYSTEM_OVERVIEW.md (authoritative semantics)

## 4. CRMScript — semantics (relevant part)

Expressions use VRL operators/functions plus string concatenation `&` and additional builtins.
**Numeric division by zero yields 0 and logs audit `SCRIPT_DIV0`** (legacy quirk that migrations
must preserve or explicitly modernize per the case's target spec). Variables are dynamically
typed; uninitialized variables read as empty string.

## 2. VRL — numeric coercion (shared by CRMScript expressions)

Empty string in numeric comparison coerces to 0.
