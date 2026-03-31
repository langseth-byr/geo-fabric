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

Reference the [threat model](docs/threat-model/THREAT-MODEL-REPORT.md) and
[CODING-CONVENTIONS.md > Security](CODING-CONVENTIONS.md) when filling this out.
Address the relevant items:

- **Untrusted input:** What user-controlled data does this feature process?
- **Validation:** What content, size, or format checks are needed?
- **Archive safety:** Does this handle ZIP files? Address path traversal and
  zip bomb risks (CT-04, CT-13).
- **Native libraries:** Does this call Fiona, Shapely, or pyproj on untrusted
  data? Ensure subprocess isolation (CT-03).
- **Output encoding:** Does this render user-supplied data in the frontend?
  Address XSS (CT-14).
- **Database:** Are queries parameterized? Is `statement_timeout` respected
  (CT-08)?
- **Resource exhaustion:** Could this be abused to exhaust CPU, memory, or
  disk? Address rate limiting and size limits (CT-07, CT-09).

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
- [ ] Security notes were addressed (with threat model references where applicable)
- [ ] No credentials, PII, or internal paths in code or logs
- [ ] Scope stayed focused

## Rules

- One issue should represent one coherent capability or fix
- Requirements must be testable
- Security notes are mandatory for untrusted input work
- Prefer short issue bodies unless the work is genuinely complex
