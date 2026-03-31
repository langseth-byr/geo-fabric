# GeoFabric — Coding Conventions

## Language and Style
- TypeScript strict mode (frontend)
- Python type hints (backend, if Python chosen)
- Lint and format before committing
- No secrets or credentials in code — use environment variables
- All AI-generated code must be test-gated

## Development Principles
- Preserve raw data always
- Make transformations explicit and traceable
- Correctness over performance initially
- Fail safely on ambiguity
- Separate processing from rendering
- Design for extensibility

## Security Requirements
All inputs are untrusted:
- Validate file content, not just extension
- Enforce size limits
- Safely parse GIS formats (isolate native tooling)
- Prevent path traversal during extraction
- Constrain long-running operations
- Parameterized database queries
- No shell execution with user input
- Safe logging (no internal leaks)

## Testing Strategy
- Geometry parsing, CRS transformation, topology repair tests
- API contract tests
- Large dataset performance tests
- Rendering smoke tests
- Regression tests with malformed inputs
- Test fixtures: valid polygons, multipolygons, holes, invalid geometries, mixed CRS, large datasets
