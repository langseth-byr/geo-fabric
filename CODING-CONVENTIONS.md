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

All incoming files and request data are untrusted.

- Validate file content, not only extensions
- Enforce upload size limits
- Guard archive extraction against path traversal
- Reject unsupported geometry types in V1
- Use parameterized queries
- Never pass user input into shell commands

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
