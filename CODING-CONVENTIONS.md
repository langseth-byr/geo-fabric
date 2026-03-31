# GeoFabric — Coding Conventions

## Python Backend

- Python 3.12+ with type hints on all functions and return types
- Pydantic v2 models for all request/response schemas
- async/await for all FastAPI route handlers
- SQLAlchemy 2.0-style query API; GeoAlchemy2 for geometry columns
- Shapely: prefer vectorized ufuncs over per-feature loops
- DuckDB: batch processing only, never for serving; parameterized queries
- Celery tasks: explicit timeout on every task, structured logging, idempotent where possible
- Lint with ruff, format with ruff format
- No secrets or credentials in code — use environment variables
- All AI-generated code must be test-gated

## TypeScript Frontend

- TypeScript strict mode
- React functional components with hooks
- MapLibre GL JS for all map interactions
- No backend internals or PostGIS types exposed to frontend

## GraphQL (Strawberry)

- Code-first schema via Strawberry type decorators — type annotations drive the schema
- Cursor-based pagination for all list queries
- Mutations return the affected object
- Pydantic input types for mutation arguments
- Query depth and complexity limits to prevent abuse

## Development Principles

- Preserve raw data always
- Make transformations explicit and traceable
- Correctness over performance initially
- Fail safely on ambiguity
- Separate processing from rendering
- Design for extensibility

## Security

All inputs are untrusted:

- Validate file content, not just extension
- Enforce size limits at the ASGI layer
- Safely parse GIS formats (isolate native tooling)
- Prevent path traversal during archive extraction
- Celery tasks must have max runtime timeouts
- GraphQL query depth and complexity limits
- Parameterized database queries (SQLAlchemy and DuckDB)
- No shell execution with user input
- Safe logging (no internal paths or PII)

## Testing

- **pytest** as test runner
- **Hypothesis** for property-based geometry testing
- PostGIS in Docker for integration tests
- Test tiers:
  - **Fast** (every commit): unit tests, geometry correctness, input validation — under 2 minutes
  - **Medium** (every PR): integration tests, round-trip fidelity, API contracts — under 10 minutes
  - **Slow** (nightly): large dataset tests, performance benchmarks, fuzzing — under 60 minutes
- Test fixtures: valid polygons, multipolygons, holes, invalid geometries, mixed CRS, large datasets
- Every production bug becomes a permanent regression test
