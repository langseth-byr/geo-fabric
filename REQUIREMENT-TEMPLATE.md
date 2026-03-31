# GeoFabric — Issue Template

Use this template for implementation issues. The goal is clarity, not ceremony.

## Title

Format:

`[Area] Short imperative summary`

Examples:

- `[Ingestion] Add GeoJSON dataset upload`
- `[Map] Show dataset features on the map`
- `[Validation] Record polygon repair warnings`

## Template

### Summary

What this issue changes and why it matters.

### Requirements

Keep this short and testable.

1. Requirement one
2. Requirement two
3. Requirement three

### Security Notes

Required when the issue handles uploads, parsing, file access, archive
extraction, query building, or any other untrusted input surface.

If not applicable, write: `No new untrusted input surface`.

### Implementation Notes

Only include the level of detail needed to build the change. Use bullets, not a
mini design document.

- Main files or modules likely to change
- Important constraints
- Any follow-on work that is intentionally out of scope

### Test Plan

- Unit tests:
- Integration tests:
- Manual verification:

### Acceptance Criteria

- [ ] Requirements are implemented
- [ ] Tests were added or updated appropriately
- [ ] Security notes were addressed
- [ ] Scope stayed focused

## Rules

- One issue should represent one coherent capability or fix
- Requirements must be testable
- Security notes are mandatory for untrusted input work
- Prefer short issue bodies unless the work is genuinely complex
