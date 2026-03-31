# GeoFabric — Coding Conventions

Adapted from OpenBSD [style(9)](https://man.openbsd.org/style.9) principles for a
Python + TypeScript + GraphQL stack.

---

## 1. General Principles

- Correctness over performance initially
- Preserve raw data always
- Make transformations explicit and traceable
- Fail safely on ambiguity
- Separate processing from rendering
- Design for extensibility
- All AI-generated code must be test-gated

## 2. Formatting

### Line Length

All code should fit within 88 columns (Python, matching ruff/black defaults) or
80 columns (TypeScript). Docstrings, comments, and URLs may exceed this when
breaking would reduce readability.

### Indentation

- **Python:** 4 spaces per level. Continuation lines use 4-space hanging indent.
- **TypeScript:** 2 spaces per level.
- No tabs in source files.
- No trailing whitespace on any line.
- No spaces in front of tabs (there should be no tabs, but enforce this in hooks).

### Whitespace

- Space after commas in argument lists and collections.
- Space after keywords (`if`, `for`, `while`, `return`, `match`, `with`).
- Spaces around binary operators (`=`, `==`, `+`, `and`, `or`, `in`).
- No spaces immediately inside parentheses, brackets, or braces.
- One blank line between functions in a class; two blank lines between top-level
  definitions.

### Braces and Blocks (TypeScript)

- Opening brace on the same line as the statement.
- Closing and opening braces on the same line as `else`:
  `} else {`
- Braces required for all control structures, even single-line bodies.

## 3. Import and Module Ordering

Strict ordering of imports, enforced by tooling. Separate each group with a blank
line.

### Python (enforced by ruff isort rules)

1. Standard library (`os`, `sys`, `pathlib`, `typing`)
2. Third-party packages (`fastapi`, `sqlalchemy`, `shapely`, `pydantic`)
3. Local application imports (project modules)

Within each group, sort alphabetically. Prefer absolute imports over relative.

### TypeScript (enforced by eslint)

1. Node built-ins and framework imports (`react`, `graphql`)
2. Third-party packages
3. Local application imports (`@/components`, `@/lib`)

Within each group, sort alphabetically.

## 4. Naming Conventions

### Python

- `snake_case` for functions, methods, variables, and module names.
- `PascalCase` for classes and Pydantic models.
- `UPPER_SNAKE_CASE` for module-level constants and enum members.
- Private members prefixed with a single underscore (`_internal_helper`).
- No Hungarian notation. No type prefixes or suffixes in names.
- Avoid abbreviations unless they are domain-standard (`crs`, `srid`, `wkt`).

### TypeScript

- `camelCase` for functions, methods, variables.
- `PascalCase` for components, classes, types, and interfaces.
- `UPPER_SNAKE_CASE` for constants.
- No `I` prefix on interfaces.

### GraphQL

- `PascalCase` for types and input types.
- `camelCase` for fields and query/mutation names.
- Enum values in `UPPER_SNAKE_CASE`.

## 5. Comments

Follow the style(9) philosophy: comments should be real sentences with proper
capitalization and punctuation.

- **Do not state the obvious.** Never comment what the code already says
  (`# Increment counter` above `counter += 1`).
- **Explain why, not what.** Comments justify decisions, document constraints,
  and warn about non-obvious behavior.
- Single-line comments: `# This works around a GeoAlchemy2 projection bug.`
- Multi-line comments should read as real paragraphs, not bullet fragments.
- TODO comments must reference an issue number: `# TODO(#42): Handle mixed CRS`.
- Remove dead/commented-out code. Version control preserves history.

## 6. Function and Method Design

- Type hints on all function signatures and return types (Python).
- Strict TypeScript mode — no `any` without justification.
- Functions that do not return a value should be annotated `-> None` (Python) or
  `: void` (TypeScript).
- Keep functions short and single-purpose. If a function needs a section comment
  to explain a block, that block may belong in its own function.
- Avoid side effects in initializers and default argument values. Never use mutable
  defaults (`def f(x=[]):`).
- Long parameter lists: wrap with a 4-space (Python) or 2-space (TypeScript)
  hanging indent, one parameter per line.

## 7. Variable Declarations

- Declare variables in the narrowest possible scope.
- Group related declarations together; sort by logical use, then alphabetically
  when no natural ordering exists.
- Avoid re-binding loop variables outside loops.
- Prefer explicit unpacking over index access: `lat, lon = point` not
  `point[0], point[1]`.
- Use `Final` (Python) or `const` (TypeScript) for values that should not be
  reassigned.

## 8. Boolean and Null Tests

Follow the style(9) principle of explicit comparison — do not rely on implicit
truthiness unless testing an actual boolean.

- **Explicit null checks:** `if value is None:` not `if not value:` (Python).
  `if (value === null)` not `if (!value)` (TypeScript).
- **Explicit empty checks:** `if len(items) == 0:` or `if not items:` only when
  the variable is guaranteed to be a list.
- **Boolean variables:** `if is_valid:` is correct — these are actual booleans.
- **String and numeric checks:** `if name == ""` and `if count == 0` — be explicit
  about what you are testing.

## 9. Error Handling

Use standard error handling patterns. Do not roll your own.

- **Python:** Raise domain-specific exceptions derived from a project base class.
  Let FastAPI exception handlers translate to HTTP responses. Never catch bare
  `Exception` unless re-raising.
- **TypeScript:** Propagate errors via return types or thrown errors with meaningful
  messages. No silent `catch {}` blocks.
- **Celery tasks:** Explicit timeout on every task (`soft_time_limit`,
  `time_limit`). Tasks must be idempotent where possible.
- **Exit codes and status:** Functions should return meaningful results, not print
  and exit. Let the calling layer decide how to report.
- **Structured logging:** Use structured log fields (JSON). Never log internal
  file paths, credentials, or PII.

## 10. Security

All inputs are untrusted.

- Validate file content, not just extension.
- Enforce size limits at the ASGI layer.
- Safely parse GIS formats (isolate native tooling in subprocesses).
- Prevent path traversal during archive extraction.
- Celery tasks must have max runtime timeouts.
- GraphQL query depth and complexity limits.
- Parameterized database queries — SQLAlchemy and DuckDB. Never interpolate user
  input into SQL strings.
- No shell execution with user input.
- Safe logging — no internal paths, credentials, or PII in log output.
- No secrets or credentials in code. Use environment variables or a secrets
  manager.

## 11. Python Backend

- Python 3.12+ required.
- Pydantic v2 models for all request/response schemas.
- `async`/`await` for all FastAPI route handlers.
- SQLAlchemy 2.0-style query API; GeoAlchemy2 for geometry columns.
- Shapely: prefer vectorized ufuncs over per-feature loops.
- DuckDB: batch processing only, never for serving; parameterized queries only.
- Lint with `ruff`; format with `ruff format`. Zero tolerance for lint warnings —
  treat all warnings as errors.

## 12. TypeScript Frontend

- TypeScript strict mode — no implicit `any`.
- React functional components with hooks. No class components.
- MapLibre GL JS for all map interactions.
- No backend internals or PostGIS types exposed to frontend.
- ESLint and Prettier enforced. Zero tolerance for lint warnings.

## 13. GraphQL (Strawberry)

- Code-first schema via Strawberry type decorators — type annotations drive the
  schema.
- Cursor-based pagination for all list queries.
- Mutations return the affected object.
- Pydantic input types for mutation arguments.
- Query depth and complexity limits enforced at the gateway layer.

## 14. Testing

- **pytest** as the test runner.
- **Hypothesis** for property-based geometry testing.
- PostGIS in Docker for integration tests — do not mock the database for
  integration-level concerns.
- Test tiers:
  - **Fast** (every commit): unit tests, geometry correctness, input validation
    — under 2 minutes.
  - **Medium** (every PR): integration tests, round-trip fidelity, API contracts
    — under 10 minutes.
  - **Slow** (nightly): large dataset tests, performance benchmarks, fuzzing
    — under 60 minutes.
- Test fixtures: valid polygons, multipolygons, holes, invalid geometries, mixed
  CRS, large datasets.
- Every production bug becomes a permanent regression test.

## 15. Code Quality

- Run all linters and formatters before committing. Configure pre-commit hooks.
- Zero suppressed warnings. If a linter rule is wrong for the project, disable it
  globally in configuration with a comment explaining why — never with inline
  `# noqa` or `// eslint-disable` unless there is a filed issue.
- Third-party or vendored code follows more relaxed guidelines but must be
  internally consistent.
- Prefer standard library and well-maintained dependencies. Audit all third-party
  packages for known CVEs before adoption.
