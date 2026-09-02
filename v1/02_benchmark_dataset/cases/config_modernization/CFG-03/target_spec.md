# CFG-03 Target Specification

Structurally migrate `legacy/workflows.xml` (semantics: `legacy/SEMANTICS_EXCERPT.md`) to a
modern JSON configuration **`workflows.json`** — the single deliverable. This is a
*structural* migration: every workflow, state, timer, transition, guard, and action must be
preserved, in document order, with nothing added and nothing dropped.

## Required shape

```json
{
  "workflows": [
    {
      "name": "<workflow name>",
      "entity": "<entity>",
      "state_field": "<state_field>",
      "states": [
        {"code": "<code>", "initial": true|false,
         "timers": [{"after_days": <int>, "event": "<event>"}]}
      ],
      "transitions": [
        {"from": "<code>", "to": "<code>", "event": "<event>",
         "guard": "<verbatim VRL string>" | null,
         "actions": [
           {"type": "set", "field": "<F>", "value": "<V>"},
           {"type": "audit", "code": "<code>"},
           {"type": "notify", "template": "<template>"}
         ]}
      ]
    }
  ]
}
```

## Rules

1. **Document order retained** everywhere: workflows in file order; each workflow's states
   and transitions in their XML order; each transition's actions in their XML order.
   (Document order is load-bearing: first matching transition wins.)
2. `initial` is an explicit boolean on every state; exactly the states marked
   `initial="true"` in the XML carry `true`.
3. `timers` is always present as a list (empty for states without timers); `after_days` is an
   int; timer event names verbatim.
4. `guard` is the **verbatim** guard text after XML entity decoding (e.g.
   `NVL(AMT,0) &gt; 0` becomes the string `NVL(AMT,0) > 0`), whitespace-trimmed; `null` for
   transitions without a guard. Guards stay strings — do not translate, simplify, or
   re-encode them.
5. `actions` is always present as a list (empty when the XML transition has no `<actions>`);
   each action keeps its XML attribute values verbatim, including `=EXPR` set-values such as
   `=NVL(SEV_CD,'3')`.
6. **Completeness and no hallucination**: the set of transitions in the JSON must equal the
   set in the XML — none missing, none invented; likewise for workflows, states, timers, and
   actions.

## Deliverable

- `workflows.json` only (valid JSON, UTF-8).
