# Excerpt of SYSTEM_OVERVIEW.md relevant to CFG-03

## 3. Workflow engine — semantics

File: `workflows.xml`. Each `<workflow>` has `entity`, a `<states>` list (one `initial="true"`),
`<transition>` elements with `from`, `to`, `event`, optional `<guard>` (VRL expression over the
entity's fields), and optional `<actions>` (list of `<set field="F" value="V"/>`,
`<audit code="..."/>`, `<notify template="..."/>` — notify is queued via INT_ENDPOINT `notifier`).
Semantics:
- A transition fires iff current state = `from`, event name matches, and guard (if any) is TRUE.
- If several transitions match, the **first in document order** wins.
- `<set>` actions apply after the state change, in order. `value` may be a literal or `=EXPR` (VRL expr).
- An event with no matching transition is a **no-op that logs** audit code `WF_NOMATCH` (it is not an error).
- Escalation timers: `<timer after_days="N" event="E"/>` inside a state fires event E when the entity
  has been in that state ≥ N days (evaluated by the nightly batch, day granularity).

Because document order decides which transition wins, a structural migration must preserve
the exact order of workflows, states, and transitions, and must keep guard expressions
verbatim (they remain VRL strings interpreted elsewhere).
