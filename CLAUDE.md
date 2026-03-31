# GeoFabric — Project Memory

## Project Overview
Full-stack geospatial platform for ingesting, validating, processing, analyzing, and visualizing polygon-based GIS datasets at scale. See [INITIAL-PLAN.md](INITIAL-PLAN.md) for full system design and [ARCHITECTURE.md](ARCHITECTURE.md) for tech stack.

## Workspace Setup
1. Clone the repo
2. Use Docker Compose for local services (PostGIS, Redis)
3. Frontend and backend live in separate directories within the monorepo

## Branching Strategy
- `main` is the stable branch — always deployable
- Create feature branches from `main`: `issue-<number>-<short-description>`
- One branch per issue, one PR per branch
- PRs require review before merge
- Delete branches after merge
- Multiple contributors can work in parallel on separate issue branches

## Coding Conventions
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

## Phases
1. **Phase 1**: Project scaffold, GeoJSON ingestion, canonical model, basic validation, map rendering
2. **Phase 2**: PostGIS integration, reprojection, simplification, filtering, export
3. **Phase 3**: CSB dataset ingestion, large dataset handling, vector tiles, background processing, advanced analysis
