# GeoFabric — Coding Conventions

## Purpose

These conventions are meant to keep the codebase small, readable, and safe.
They should help the team move faster, not create ceremony for its own sake.

## Core Principles

- Prefer simple designs over speculative abstractions
- Keep the first implementation easy to understand
- Treat all uploaded geospatial files as untrusted input
- Preserve provenance and validation results
- Write tests for behavior that matters
- Add infrastructure only when measurement justifies it

## Backend

- Python 3.12+
- FastAPI for HTTP APIs
- Pydantic v2 for request and response validation
- SQLAlchemy 2.x for database access
- PostGIS is the source of truth for stored geometry
- Shapely handles geometry validation and repair logic
- pyproj handles CRS transformations

## Frontend

- React with TypeScript
- Functional components only
- Keep map state and data-fetching flows explicit
- Do not expose database-specific shapes directly to UI components

## API Style

- Use REST for V1
- Keep endpoints small and purpose-specific
- Return structured errors with stable error codes where possible
- Reject invalid requests early

## Naming

- Python: `snake_case` for functions, variables, and modules
- Python: `PascalCase` for classes
- TypeScript: `camelCase` for functions and variables
- TypeScript: `PascalCase` for components and types
- Use domain names that match the product language: dataset, feature,
  validation, ingestion

## File And Function Design

- Keep modules focused on one concern
- Keep functions short enough to read without scrolling through unrelated work
- Split parsing, validation, persistence, and API concerns into separate modules
- Prefer explicit data flow over hidden side effects

## Error Handling

- Never swallow exceptions silently
- Convert domain failures into clear API responses
- Do not leak internal paths, secrets, or stack traces to users
- Log enough context to debug ingestion failures safely

## Security

All incoming files and request data are untrusted. These rules are informed by
the [threat model](docs/threat-model/THREAT-MODEL-REPORT.md) and scoped to the
lean V1 stack.

### Input Validation

- Validate file content by magic bytes and structure, not file extension
- Enforce a configurable upload size limit at the ASGI layer
- Reject unsupported geometry types in V1 (only Polygon and MultiPolygon)
- Sanitize GeoJSON feature properties at ingestion time — they are rendered in
  the frontend and must not contain executable content (CT-14)

### Archive Extraction (Shapefiles)

- Reject ZIP entries containing `..` or absolute paths (CT-04)
- Allow only Shapefile extensions: .shp, .shx, .dbf, .prj, .cpg
- Enforce maximum extraction size and reject compression ratios above 100:1 to
  block zip bombs (CT-13)
- Limit ZIP entry count (Shapefiles have 4-7 files)
- Extract to an isolated temp directory; validate before moving

### Native Library Isolation

- Run all GIS parsing (Fiona, Shapely, pyproj) in isolated subprocesses with
  memory and CPU limits (CT-03)
- Never let a native library crash take down the API process
- Monitor GDAL, GEOS, and PROJ CVE feeds and update promptly

### Database

- Use parameterized queries via SQLAlchemy — never interpolate user input
  into SQL strings
- Set `statement_timeout` on PostgreSQL connections to prevent expensive spatial
  queries from blocking the database (CT-08)
- Store database credentials in environment variables, never in code (CT-19)

### API Hardening

- Configure CORS to allow only the frontend origin (CT-16)
- Set security headers: Content-Security-Policy, X-Content-Type-Options,
  X-Frame-Options, Strict-Transport-Security (CT-16)
- Apply per-IP rate limiting on all endpoints, with stricter limits on upload
  (CT-09)
- Return structured error responses with stable error codes — never expose
  internal paths, stack traces, or database details

### Output Encoding

- Never use `dangerouslySetInnerHTML` in React components
- Encode feature properties when rendering in DOM attributes
- Rely on React JSX auto-escaping as a baseline, not the only defense

### Shell And Command Execution

- Never pass user input into shell commands
- No `subprocess.run(shell=True)` with user-controlled arguments

### Logging

- Use structured JSON logging for all security-relevant events: uploads,
  ingestion results, validation failures, rejected requests (CT-15)
- Include request metadata (IP, user-agent) in log entries
- Never log credentials, PII, or internal file paths

### Secrets

- No secrets or credentials in code or version control
- Use environment variables or a secrets manager
- Keep raw uploads outside the web root

### Dependency Scanning

- Audit third-party packages for known CVEs before adoption
- Run pip-audit and npm audit in CI (CT-25)

## Testing

Start with the tests that protect the core workflow:

- Unit tests for parsing and validation helpers
- Integration tests for ingestion into PostGIS
- API tests for dataset upload and feature retrieval
- Regression tests for every real bug found during ingestion

Property-based tests are useful for geometry edge cases, but add them where
they produce clear value instead of as a blanket rule.

## Tooling

- Use `ruff` for Python linting and formatting
- Use ESLint and Prettier for TypeScript
- Add pre-commit hooks once the repo has actual code
- Treat warnings seriously, but do not block progress with unnecessary tooling
  before the implementation exists

## What To Avoid Early

- Premature generic frameworks
- Architecture built around theoretical scale targets
- Heavy issue templates for small, obvious changes
- New infrastructure added without a concrete trigger
