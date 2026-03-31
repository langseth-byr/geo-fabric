# GeoFabric — Project Memory

## Project Direction

GeoFabric is starting as a small geospatial ingestion and visualization app, not
as a full GIS platform.

The first milestone is one working loop:

1. Upload a polygon dataset
2. Parse it safely
3. Normalize CRS
4. Validate geometry
5. Store it in PostGIS
6. Render it on a map
7. Inspect features and apply basic filters

## Key Documents

- [INITIAL-PLAN.md](INITIAL-PLAN.md) for scope and milestones
- [ARCHITECTURE.md](ARCHITECTURE.md) for the lean V1 stack and security architecture
- [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md) for engineering rules and security controls
- [REQUIREMENT-TEMPLATE.md](REQUIREMENT-TEMPLATE.md) for issue writing
- [Threat Model](docs/threat-model/THREAT-MODEL-REPORT.md) for security analysis

## Working Assumptions

- V1 is REST-first
- GeoJSON comes before broader format support
- Shapefile is the next format after GeoJSON
- Provenance, validation, and safe ingestion are non-negotiable
- Security controls from the threat model are integrated into the architecture
  and coding conventions — reference CT-XX identifiers when writing security
  notes in issues
- Background jobs, vector tiles, and more infrastructure are deferred until
  proven necessary

## Issue Writing

Issues should be specific enough to implement and test, but lighter than a full
spec package.

Every issue should include:

- The problem being solved
- A short list of testable requirements
- Security notes when untrusted input is involved
- A short implementation outline when the work is non-trivial
- A test plan

## Branching

- Base from `main`
- Use one branch per issue
- Keep PRs focused
- Prefer draft PRs while scope is still moving
- Use a separate worktree for each PR so we can work simultaneously on
  different issues

## Git Worktrees

Claude Code agents can run in isolated git worktrees (`isolation: "worktree"`).
This gives the agent its own copy of the repo so it cannot interfere with
uncommitted work on the current branch.

### When to use worktree isolation

- **Parallel implementation tasks** — two or more agents writing code at the
  same time must each have their own worktree to avoid file conflicts
- **Exploratory or spike work** — changes that may be discarded should not
  pollute the working tree
- **Risky refactors** — large-scale edits are safer in a worktree; review the
  diff before merging back

### When worktrees are unnecessary

- **Read-only agents** — exploration, search, and research agents do not modify
  files and do not need isolation
- **Single sequential edits** — if only one agent is writing code and the
  working tree is clean, a worktree adds overhead for no benefit

### Cleanup and merging

- If a worktree agent makes useful changes, review the resulting branch and
  merge it into the issue branch (or open a PR from it)
- If the changes are not needed, delete the worktree branch
- Do not leave orphaned worktree branches — clean up after each task
