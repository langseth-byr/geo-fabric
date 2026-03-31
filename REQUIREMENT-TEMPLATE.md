# GeoFabric — Issue Requirement Template

Use this template when opening new GitHub issues. Every issue must contain a detailed development plan derived from the project spec so that any contributor (human or AI) can implement it without ambiguity.

---

## Issue Title

Format: `[Component] Short imperative description`

Examples:
- `[Ingestion] Add GeoParquet format support`
- `[API] Implement dataset upload mutation`
- `[Map] Add zoom-based geometry simplification`

---

## Template

Copy everything below this line into the issue body.

---

### Summary

One or two sentences describing what this issue delivers. State the user-visible outcome or system capability, not implementation details.

### Motivation

- **Why:** Why is this needed now? Link to the relevant section in [INITIAL-PLAN.md](INITIAL-PLAN.md) or [ARCHITECTURE.md](ARCHITECTURE.md).
- **Blocked by:** List any prerequisite issues (e.g., `#12 must be merged first`).
- **Blocks:** List any downstream issues that depend on this.

### Spec Reference

Quote or link the specific sections from project documents that define this work:

- **INITIAL-PLAN.md section(s):** e.g., "Data Ingestion > CRS Handling"
- **ARCHITECTURE.md section(s):** e.g., "Geospatial Libraries > DuckDB"
- **CODING-CONVENTIONS.md section(s):** e.g., "Security > Validate file content, not just extension"

### Requirements

Numbered list of testable, unambiguous requirements. Each requirement must be verifiable — no subjective language ("should be fast", "nice UX"). Use concrete thresholds where applicable.

Example:
1. Accept `.parquet` and `.geoparquet` files via the GraphQL upload mutation
2. Detect GeoParquet format by file content (magic bytes), not file extension
3. Extract geometry column and all attribute columns
4. Normalize CRS to EPSG:4326; preserve source CRS in `source_crs` field
5. Reject files exceeding 2 GB with a structured error response
6. Write parsed features to the `spatial_feature` table matching the canonical data model

### Data Model Changes

If this issue modifies the data model, specify exact changes:

| Table | Column | Type | Description |
|---|---|---|---|
| `spatial_feature` | `new_column` | `TEXT` | What it stores |

If no data model changes: write "None".

### API Changes

If this issue adds or modifies API endpoints:

**GraphQL:**
```graphql
# New mutation / query / subscription signature
mutation uploadDataset($file: Upload!, $name: String!): DatasetUploadResult!
```

**REST (tile endpoints only):**
```
GET /{layer}/{z}/{x}/{y}
```

If no API changes: write "None".

### Security Considerations

Identify threats relevant to this issue. Reference [CODING-CONVENTIONS.md > Security](CODING-CONVENTIONS.md).

- What untrusted input does this feature handle?
- What validation is required?
- What size/complexity limits apply?
- Are there path traversal, injection, or resource exhaustion risks?

If no security-relevant surface: write "No new untrusted input surface" and explain why.

### Development Plan

Step-by-step implementation plan. Each step should be a single, reviewable unit of work. Include file paths where known.

```
Step 1: [Description]
  - Files: backend/app/ingestion/geoparquet.py (new)
  - Details: ...

Step 2: [Description]
  - Files: backend/app/models/spatial_feature.py
  - Details: ...

Step 3: [Description]
  - Files: backend/tests/ingestion/test_geoparquet.py (new)
  - Details: ...
```

### Test Plan

Map each requirement to at least one test. Follow the test tiers from [CODING-CONVENTIONS.md > Testing](CODING-CONVENTIONS.md).

| Requirement | Test | Tier |
|---|---|---|
| R1: Accept .parquet files | `test_upload_geoparquet_file` | Fast |
| R2: Content-based detection | `test_detect_geoparquet_magic_bytes` | Fast |
| R4: CRS normalization | `test_geoparquet_crs_normalized_to_4326` | Medium |
| R5: Reject oversized files | `test_reject_file_over_2gb` | Fast |

**Property-based tests (Hypothesis):** Describe any geometry invariants to test generatively.

**Regression fixtures:** List any specific test fixtures needed (malformed files, edge-case geometries, etc.).

### Acceptance Criteria

Checklist that must all be true before the issue can be closed:

- [ ] All requirements implemented and passing
- [ ] All tests passing across relevant tiers (Fast, Medium)
- [ ] No new ruff lint errors
- [ ] Security considerations addressed and validated
- [ ] Data model migration created (if applicable)
- [ ] No secrets, credentials, or PII in code or logs

### Labels

Apply all relevant labels:

- **Component:** `ingestion`, `api`, `map`, `processing`, `storage`, `infrastructure`
- **Type:** `feature`, `bug`, `refactor`, `security`, `performance`
- **Phase:** `phase-1`, `phase-2`, `phase-3` (per [INITIAL-PLAN.md > Milestones](INITIAL-PLAN.md))
- **Priority:** `critical`, `high`, `medium`, `low`

### Estimated Scope

- **Files touched:** approximate count
- **New files:** approximate count
- **Migration required:** yes/no

---

## Principles for Writing Issues

1. **Testable requirements only.** If you cannot write a test for it, rewrite the requirement until you can.
2. **One issue, one capability.** Split large features into multiple issues. Each issue should map to a single PR.
3. **Reference the spec.** Every requirement must trace back to INITIAL-PLAN.md, ARCHITECTURE.md, or CODING-CONVENTIONS.md. If it doesn't exist in the spec, update the spec first.
4. **Security by default.** Every issue that touches untrusted input must have a non-empty Security Considerations section.
5. **No vague acceptance criteria.** "Works correctly" is not an acceptance criterion. "Returns HTTP 400 with error code `INVALID_CRS` when source CRS is undetectable" is.
6. **Include the test plan up front.** Tests are not an afterthought — they are part of the requirement.
7. **Assume the implementer has no prior context.** Write issues so that a contributor seeing the codebase for the first time can implement them by following the development plan and reading the linked spec sections.
