# THREAT MODEL REPORT

**System:** GeoFabric — Geospatial Data Platform
**Date:** 2026-03-31
**Classification:** Internal
**Version:** 1.0

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope and Methodology](#2-scope-and-methodology)
3. [System Architecture](#3-system-architecture)
4. [Threat Inventory](#4-threat-inventory)
5. [Risk Matrix](#5-risk-matrix)
6. [Control Gap Analysis](#6-control-gap-analysis)
7. [Remediation Roadmap](#7-remediation-roadmap)
8. [Compliance Mapping](#8-compliance-mapping)
9. [Appendices](#9-appendices)

---

## 1. Executive Summary

### Overall Risk Assessment: HIGH

GeoFabric is a geospatial platform that processes untrusted polygon datasets
uploaded by users. The system parses files through native C/C++ libraries,
stores data in PostGIS, and serves it through a GraphQL API and vector tile
server to a web map interface.

**This assessment identified 27 threats: 2 Critical, 13 High, 10 Medium, and
2 Low.**

### Findings by Severity

| Severity | Count |
|---|---|
| Critical | 2 |
| High | 13 |
| Medium | 10 |
| Low | 2 |
| **Total** | **27** |

### Top 5 Risks (Business Terms)

1. **Anyone on the internet can access all data and perform all operations.**
   No authentication or authorization exists in the architecture. All
   datasets — including potentially proprietary GIS data — are accessible
   to anonymous users. (CT-01, CT-02)

2. **Malicious file uploads could compromise the server.** The platform
   processes untrusted files through native C/C++ libraries (GDAL, GEOS,
   PROJ) that have historical vulnerabilities. A crafted file could achieve
   code execution on the processing servers. (CT-03, CT-04, CT-13)

3. **The API can be abused to overwhelm the system.** No rate limiting,
   no query complexity limits, and no upload size caps. A single attacker
   can exhaust database, storage, and processing resources. (CT-06, CT-07,
   CT-08, CT-09)

4. **Internal services are not protected from lateral movement.** Redis has
   no authentication, inter-service communication is unencrypted, and Celery
   uses pickle serialization. If any component is compromised, the attacker
   can reach all others. (CT-05, CT-10, CT-12)

5. **No audit trail exists for any operation.** Dataset uploads, deletions,
   and access cannot be attributed to any user. Security incidents cannot be
   investigated. (CT-15)

### Key Recommendations (Priority Order)

1. Design and implement authentication (OAuth2/OIDC) and authorization
   (RBAC with dataset ownership) before any production deployment
2. Enable Redis AUTH and switch Celery to JSON serialization immediately
3. Implement GraphQL depth/complexity limits and upload size caps
4. Implement subprocess isolation for native GIS library execution
5. Add rate limiting, CORS, CSP, and security headers
6. Implement audit logging for all security-relevant events
7. Enable TLS for all inter-service communication

### Compliance Implications

The absence of authentication, authorization, audit logging, and encryption
at rest means the system cannot meet baseline requirements for SOC 2, PCI
DSS, HIPAA, or GDPR. These must be addressed before handling any regulated
data.

---

## 2. Scope and Methodology

### 2.1 System Description

GeoFabric is a full-stack geospatial platform for ingesting, validating,
processing, and visualizing polygon-based GIS datasets at scale. The system
accepts file uploads in GeoJSON, Shapefile, GeoParquet, and WKT formats;
normalizes data to EPSG:4326; stores it in PostGIS; and serves it through a
GraphQL API and vector tile server.

### 2.2 Scope

**In scope:** All components defined in ARCHITECTURE.md — React frontend,
GraphQL API (FastAPI/Strawberry), Martin tile server, PgBouncer, PostGIS,
Redis, Celery workers, DuckDB, object storage, and CDN.

**Excluded:** Production deployment infrastructure (not yet defined),
third-party CDN configuration details, specific cloud provider security
controls.

### 2.3 Methodology

Three analysis methods were applied:

| Method | Prompt | Purpose |
|---|---|---|
| Automated Repository Analysis | 05 | Autonomous scan of repository for tech stack, entry points, data stores, trust boundaries |
| Document Analysis | 06 | Extraction of threat data from INITIAL-PLAN.md, ARCHITECTURE.md, CODING-CONVENTIONS.md, README.md |
| STRIDE | 00 | Systematic analysis of all 6 STRIDE dimensions across all 9 major components |

### 2.4 Participants and Perspectives

This threat model was produced by AI-assisted security architecture analysis.
No interactive interview was conducted.

**Perspective Coverage:**

| Perspective | Status |
|---|---|
| Security Architecture | Covered (AI analysis) |
| GIS Domain Expert | NOT covered |
| DevOps / SRE | NOT covered |
| Business Stakeholder | NOT covered |
| Frontend Developer | NOT covered |
| Backend Developer | NOT covered |

### 2.5 Data Sources

- GeoFabric repository (spec-phase, no implementation code)
- INITIAL-PLAN.md — System design, data model, user flows, security requirements
- ARCHITECTURE.md — Tech stack, architecture diagram, scale requirements, risk mitigations
- CODING-CONVENTIONS.md — Code style, security rules, testing tiers
- README.md — Project overview and onboarding

### 2.6 Limitations

1. **No implementation code exists.** All security controls documented in
   CODING-CONVENTIONS.md are plans, not verified implementations. The actual
   security posture is unknown.
2. **Single-perspective analysis.** No GIS domain expert, DevOps, business,
   or developer input. Blind spots exist in GIS-specific attack vectors,
   deployment threats, business impact calibration, and implementation-level
   concerns.
3. **Scope contradictions in specs.** INITIAL-PLAN.md V1 excludes Redis,
   Celery, and Martin, but ARCHITECTURE.md includes them. This threat model
   covers the full architecture.
4. **No production deployment architecture.** Network topology, firewall
   rules, and service isolation for production are undocumented.

---

## 3. System Architecture

### 3.1 System Context

See [08-diagrams.md](08-diagrams.md) Diagram 1 and [09-visual-designs.md](09-visual-designs.md) Figure 1.

**Actors:**
- End Users (browser) — upload datasets, view maps, inspect features
- API Consumers (programmatic) — query and mutate GIS data
- Administrators — undefined (no admin role documented)

### 3.2 Component Architecture

See [08-diagrams.md](08-diagrams.md) Diagram 2 and [09-visual-designs.md](09-visual-designs.md) Figure 2.

**Components (13 total):**

| Component | Technology | Zone |
|---|---|---|
| React Frontend | TypeScript, MapLibre GL JS | Internet |
| GraphQL API | Python 3.12+, FastAPI, Strawberry | Application |
| Martin Tile Server | Rust 0.15+ | Application |
| PgBouncer | 1.23+ | Data |
| PostGIS | PostgreSQL + PostGIS | Data |
| Redis | Redis | Data |
| Celery Workers | Python, Celery 5.x | Processing |
| DuckDB | 1.2+ with spatial extension | Processing |
| Object Storage | S3 / local | Data |
| CDN | CloudFront / Cloudflare | Edge |
| GDAL/OGR (Fiona) | Fiona 1.10+ | Processing |
| Shapely (GEOS) | Shapely 2.x | Processing |
| pyproj (PROJ) | pyproj 3.7+ | Processing |

### 3.3 Data Flow

See [08-diagrams.md](08-diagrams.md) Diagram 3 and [09-visual-designs.md](09-visual-designs.md) Figure 3.

**Critical data flows:**
1. **Upload flow:** Browser -> API -> Object Storage + PostGIS -> Redis -> Celery Worker
2. **Ingestion flow:** Worker -> Object Storage -> GDAL/Shapely/pyproj -> PostGIS
3. **Map view flow:** Browser -> CDN -> Martin -> PostGIS
4. **Query flow:** Browser -> API -> PostGIS (via PgBouncer) -> Redis cache

### 3.4 Trust Boundaries

| Boundary | From | To | Controls |
|---|---|---|---|
| Internet -> Application | Browser / API Client | GraphQL API | **NONE** (no auth, no rate limiting) |
| Internet -> Edge | Browser | CDN | CDN DDoS protection (assumed) |
| Edge -> Application | CDN | Martin | **NONE** (no auth) |
| Application -> Data | API / Martin | PgBouncer / Redis | **NONE** (no TLS, Redis no AUTH) |
| Application -> Processing | API (via Redis) | Celery Workers | **NONE** (no message signing) |
| Processing -> Data | Workers | PostGIS / Object Storage | **NONE** (full DB privileges) |

### 3.5 Attack Surface

See [08-diagrams.md](08-diagrams.md) Diagram 5 and [09-visual-designs.md](09-visual-designs.md) Figure 5.

**8 entry points identified. All external entry points lack authentication.**

---

## 4. Threat Inventory

### CT-01: No Authentication Architecture (CRITICAL)

**Severity:** Critical | **STRIDE:** Spoofing | **Risk Score:** 10/10
**Affected Assets:** GraphQL API, Martin Tile Server, Frontend
**Trust Boundary:** Internet -> Application

#### Description

No authentication mechanism is specified in any project document. All
GraphQL mutations (upload, delete, reproject) and queries (dataset listing,
feature data) are accessible to anonymous network clients. The Martin tile
server serves tiles without authentication. Any internet user can upload
malicious files, query all stored data, and delete datasets.

#### Attack Scenario

1. Attacker discovers the GraphQL endpoint (introspection enabled by default)
2. Attacker queries all datasets and features — full data exfiltration
3. Attacker uploads crafted malicious files to exploit downstream processing
4. Attacker deletes all datasets

#### Business Impact

Complete unauthorized access to all platform data and operations. Data breach
of all stored GIS datasets. Potential destruction of all data. Regulatory
violations if any data is protected.

#### Existing Controls

None.

#### Recommended Mitigations

1. Design authentication architecture (add to ARCHITECTURE.md)
2. Implement OAuth2/OIDC with proven identity provider (Auth0, Keycloak)
3. Require authentication on all mutations and sensitive queries
4. Proxy tile requests through authenticated API or use signed tile URLs
5. Consider allowing anonymous read-only access to explicitly public datasets

#### Residual Risk

Low after implementation.

---

### CT-02: No Authorization Model (CRITICAL)

**Severity:** Critical | **STRIDE:** Elevation of Privilege | **Risk Score:** 10/10
**Affected Assets:** GraphQL API, PostGIS
**Trust Boundary:** Application internal

#### Description

No RBAC, ABAC, or ownership model exists. The data model has no owner field.
No admin role is defined. Once authentication is added, all authenticated
users will have identical access to all datasets — any user can view, modify,
and delete any other user's datasets.

#### Attack Scenario

1. Authenticated user A uploads proprietary GIS data
2. Authenticated user B (or compromised account) queries and downloads user
   A's dataset
3. User B deletes user A's datasets — no authorization check prevents this

#### Business Impact

Cross-user data breach. Loss of customer data. Potential legal liability for
failing to protect proprietary data.

#### Existing Controls

None.

#### Recommended Mitigations

1. Add `owner_id` / `created_by` to dataset model
2. Implement dataset-level ownership (only owner can update/delete)
3. Define RBAC: at minimum user and admin roles
4. Enforce authorization in GraphQL resolvers
5. Write authorization integration tests for every mutation

#### Residual Risk

Low after implementation.

---

### CT-03: Native C/C++ Library Exploitation via Crafted GIS Input (HIGH)

**Severity:** High | **STRIDE:** Elevation of Privilege | **Risk Score:** 8/10
**Affected Assets:** GDAL/OGR, Shapely/GEOS, pyproj/PROJ, Celery Workers
**Trust Boundary:** Processing Zone (untrusted data in native code)

#### Description

GDAL/OGR, GEOS, and PROJ are C/C++ libraries with historical CVEs for
buffer overflows, use-after-free, and integer overflows. Uploaded GIS files
are processed through these libraries in Celery workers. A crafted input
could achieve remote code execution within the worker process, which has
database access, filesystem access, and Redis access.

#### Attack Scenario

1. Attacker uploads a crafted GeoJSON or Shapefile with malformed geometry
   designed to trigger a buffer overflow in GEOS
2. Celery worker processes the file, GEOS overwrites memory
3. Attacker achieves code execution in the worker process
4. Attacker uses worker's database credentials to read/modify all data
5. Attacker pivots to Redis to inject tasks on other workers

#### Business Impact

Full system compromise. Data breach. Data destruction. Potential lateral
movement to other infrastructure.

#### Existing Controls

- CODING-CONVENTIONS.md: "Safely parse GIS formats (isolate native tooling
  in subprocesses)" — **Planned, not implemented**

#### Recommended Mitigations

1. Run all GIS parsing in isolated subprocesses with memory/CPU limits
2. Apply seccomp/AppArmor profiles to restrict subprocess capabilities
3. Run GIS processing in dedicated containers with no network access
4. Monitor GDAL, GEOS, PROJ CVE feeds and update promptly
5. Consider gVisor or similar sandbox for worker containers

#### Residual Risk

Medium — new native library CVEs are discovered periodically.

---

### CT-04: Shapefile ZIP Archive Path Traversal (HIGH)

**Severity:** High | **STRIDE:** Tampering | **Risk Score:** 7/10
**Affected Assets:** API, Celery Workers, Object Storage
**Trust Boundary:** Internet -> Processing

#### Description

Crafted ZIP archives containing entries with path traversal sequences
(`../../etc/cron.d/backdoor`) could write files outside the extraction
directory, potentially overwriting application code or configuration.

#### Existing Controls

- Path traversal prevention documented in CODING-CONVENTIONS.md and
  INITIAL-PLAN.md — **Planned, not implemented**

#### Recommended Mitigations

1. Validate all ZIP entry paths — reject entries containing `..` or absolute paths
2. Extract to isolated temp directory; validate before moving
3. Verify Shapefile-specific extensions only (.shp, .shx, .dbf, .prj, .cpg)
4. Enforce maximum extraction size

#### Residual Risk

Low after implementation.

---

### CT-05: Redis Without Authentication (HIGH)

**Severity:** High | **STRIDE:** Tampering | **Risk Score:** 6/10
**Affected Assets:** Redis, Celery Workers, API
**Trust Boundary:** Application -> Data

#### Description

Redis has no AUTH documented. Any network-accessible process can poison
cached queries, inject Celery tasks, modify job state, or flush the cache.
Combined with Celery pickle deserialization (CT-12), this enables remote code
execution on workers.

#### Recommended Mitigations

1. Enable Redis AUTH with strong password
2. Use Redis ACLs for role separation (cache vs. broker)
3. Bind to internal interfaces only
4. Enable TLS for Redis connections in production

#### Residual Risk

Low.

---

### CT-06: GraphQL Query Depth/Complexity Abuse (HIGH)

**Severity:** High | **STRIDE:** Denial of Service | **Risk Score:** 8/10
**Affected Assets:** GraphQL API, PostGIS
**Trust Boundary:** Internet -> Application

#### Description

Without enforced depth and complexity limits, deeply nested or
cartesian-product GraphQL queries can exhaust API memory, CPU, and PostGIS
connections. A single malicious query can deny service to all users.

#### Existing Controls

- CODING-CONVENTIONS.md mentions limits as convention — **Not enforced**

#### Recommended Mitigations

1. Implement Strawberry depth validation (max depth 10)
2. Implement cost-based complexity analysis with configurable limits
3. Set per-query timeout (30 seconds)
4. Consider persisted queries in production

#### Residual Risk

Low.

---

### CT-07: Unlimited File Upload Size (HIGH)

**Severity:** High | **STRIDE:** Denial of Service | **Risk Score:** 8/10
**Affected Assets:** API, Object Storage, Celery Workers

#### Description

No specific upload size limits defined. Multi-GB uploads exhaust disk,
memory, and processing time.

#### Recommended Mitigations

1. Configure maximum upload size (e.g., 500MB)
2. Implement streaming upload — do not buffer in memory
3. Set per-user upload quotas
4. Monitor storage utilization

#### Residual Risk

Low.

---

### CT-08: Expensive Spatial Operations Cause Database DoS (HIGH)

**Severity:** High | **STRIDE:** Denial of Service | **Risk Score:** 7/10
**Affected Assets:** PostGIS, Celery Workers, API

#### Description

Spatial operations on 50K+ vertex polygons are CPU-intensive. Crafted
queries or datasets lock PostGIS for extended periods. ARCHITECTURE.md
explicitly identifies this risk.

#### Existing Controls

- Celery timeouts and pre-simplification — **Planned**

#### Recommended Mitigations

1. Set PostgreSQL `statement_timeout` for API queries (30s)
2. Route expensive operations to Celery with hard time limits
3. Implement geometry complexity limits for interactive queries
4. Use PostGIS query cost estimation to reject expensive queries

#### Residual Risk

Medium — legitimate large dataset queries are inherently expensive.

---

### CT-09: No Rate Limiting (HIGH)

**Severity:** High | **STRIDE:** Denial of Service | **Risk Score:** 8/10
**Affected Assets:** API, Martin, PostGIS

#### Description

No rate limiting on any endpoint. Unlimited requests enable resource
exhaustion, brute-force, and API abuse.

#### Recommended Mitigations

1. Implement API-level rate limiting (per-IP and per-user)
2. Stricter limits on upload and processing endpoints
3. CDN-level rate limiting for tiles

#### Residual Risk

Low.

---

### CT-10: No TLS for Inter-Service Communication (HIGH)

**Severity:** High | **STRIDE:** Information Disclosure | **Risk Score:** 5/10
**Affected Assets:** All internal services

#### Description

SQL queries, spatial data, cache contents, and task messages traverse
the internal network in plaintext.

#### Recommended Mitigations

1. Enable TLS for PostgreSQL and Redis connections
2. Use encrypted overlay networks in production
3. Consider mTLS for service-to-service authentication

#### Residual Risk

Low.

---

### CT-11: Martin Serves All Data Without Access Controls (HIGH)

**Severity:** High | **STRIDE:** Information Disclosure | **Risk Score:** 7/10
**Affected Assets:** Martin, PostGIS, CDN

#### Description

Martin has direct, unrestricted PostGIS read access. No layer filtering,
no row-level security, no authentication. All spatial data accessible via
tile requests.

#### Recommended Mitigations

1. Configure Martin for specific layers only
2. Use read-only PostgreSQL user with minimal grants
3. Implement PostGIS row-level security for multi-tenant
4. Proxy tiles through authenticated API or use signed URLs

#### Residual Risk

Medium.

---

### CT-12: Celery Pickle Deserialization Enables RCE (HIGH)

**Severity:** High | **STRIDE:** Elevation of Privilege | **Risk Score:** 7/10
**Affected Assets:** Celery Workers, Redis

#### Description

Celery defaults to pickle serialization. Combined with unauthenticated
Redis (CT-05), an attacker who gains Redis access can inject pickle
payloads for arbitrary code execution on workers.

#### Recommended Mitigations

1. Set `CELERY_TASK_SERIALIZER = 'json'` and `CELERY_ACCEPT_CONTENT = ['json']`
2. Enable Celery message signing
3. Secure Redis with AUTH (CT-05)

#### Residual Risk

Low.

---

### CT-13: Zip Bomb Exhausts Disk and Memory (HIGH)

**Severity:** High | **STRIDE:** Denial of Service | **Risk Score:** 7/10
**Affected Assets:** API, Celery Workers, Object Storage

#### Description

High compression ratio ZIP archives expand to massive sizes, filling disk
and crashing processes.

#### Recommended Mitigations

1. Check compression ratio (reject >100:1)
2. Set maximum total extraction size
3. Limit ZIP entry count (Shapefiles have 4-7 files)
4. Extract in quota-limited temp directory

#### Residual Risk

Low.

---

### CT-14: Stored XSS via Malicious GeoJSON Properties (HIGH)

**Severity:** High | **STRIDE:** Tampering | **Risk Score:** 7/10
**Affected Assets:** Frontend, API, PostGIS

#### Description

GeoJSON properties stored verbatim and rendered in frontend inspector.
Malicious HTML/JS in properties executes in other users' browsers.

#### Existing Controls

- React JSX auto-escaping — **Partial**

#### Recommended Mitigations

1. Sanitize properties at ingestion time
2. Never use `dangerouslySetInnerHTML`
3. Implement CSP
4. Encode when rendering in DOM attributes

#### Residual Risk

Low.

---

### CT-15: No Audit Logging (HIGH)

**Severity:** High | **STRIDE:** Repudiation | **Risk Score:** 8/10
**Affected Assets:** API, Celery Workers, PostGIS

#### Description

No audit logging architecture. Operations cannot be attributed or
investigated. Structured logging is mentioned as a convention but covers
operational concerns, not security audit trails.

#### Recommended Mitigations

1. Implement audit logging for auth events, CRUD operations, admin actions
2. Include user identity, action, resource, IP, outcome
3. Store in append-only storage
4. Define retention period

#### Residual Risk

Low.

---

### CT-16 through CT-26 (MEDIUM and LOW)

| ID | Title | Severity | STRIDE |
|---|---|---|---|
| CT-16 | No CORS or CSP configuration | Medium | Tampering |
| CT-17 | GraphQL introspection exposes schema | Medium | Info Disclosure |
| CT-18 | No encryption at rest | Medium | Info Disclosure |
| CT-19 | Database credentials at risk of exposure | Medium | Info Disclosure |
| CT-20 | PgBouncer connection pool exhaustion | Medium | DoS |
| CT-21 | Celery workers with full DB privileges | Medium | Elevation |
| CT-22 | DuckDB native parser risks on GeoParquet | Medium | Elevation |
| CT-23 | Tile request flooding bypasses CDN | Medium | DoS |
| CT-24 | Feature properties expose sensitive data | Medium | Info Disclosure |
| CT-25 | No dependency vulnerability scanning | Low | Elevation |
| CT-26 | No data retention or deletion policies | Low | Info Disclosure |

Full details for each threat are available in the consolidated CycloneDX
JSON at [07-consolidated.json](07-consolidated.json).

---

## 5. Risk Matrix

### 5.1 Risk Heat Map

```
              IMPACT
              Low      Medium     High       Critical
           ┌──────────┬──────────┬──────────┬──────────┐
  High     │          │ CT-25    │ CT-06    │ CT-01    │
           │          │          │ CT-07    │ CT-02    │
           │          │          │ CT-09    │          │
           │          │          │ CT-15    │          │
           ├──────────┼──────────┼──────────┼──────────┤
  Medium   │          │ CT-16    │ CT-04    │ CT-03    │
           │          │ CT-17    │ CT-05    │          │
  LIKELI-  │          │ CT-20    │ CT-08    │          │
  HOOD     │          │ CT-23    │ CT-11    │          │
           │          │ CT-24    │ CT-12    │          │
           │          │          │ CT-13    │          │
           │          │          │ CT-14    │          │
           ├──────────┼──────────┼──────────┼──────────┤
  Low      │          │ CT-26    │ CT-10    │          │
           │          │          │ CT-18    │          │
           │          │          │ CT-19    │          │
           │          │          │ CT-21    │          │
           │          │          │ CT-22    │          │
           └──────────┴──────────┴──────────┴──────────┘
```

### 5.2 Risk by STRIDE Category

| STRIDE Category | Critical | High | Medium | Low | Total |
|---|---|---|---|---|---|
| Spoofing | 1 | 1 | 1 | 0 | 3 |
| Tampering | 0 | 3 | 1 | 0 | 4 |
| Repudiation | 0 | 1 | 1 | 0 | 2 |
| Information Disclosure | 0 | 2 | 4 | 0 | 6 |
| Denial of Service | 0 | 5 | 2 | 0 | 7 |
| Elevation of Privilege | 1 | 2 | 2 | 1 | 6 |
| **Total** | **2** | **14** | **11** | **1** | **28** |

### 5.3 Risk by Component

| Component | Threat Count | Highest Severity |
|---|---|---|
| GraphQL API | 14 | Critical |
| Celery Workers | 7 | High |
| PostGIS | 6 | High |
| Martin | 4 | High |
| Redis | 3 | High |
| Object Storage | 3 | High |
| Frontend | 2 | High |
| PgBouncer | 2 | Medium |
| DuckDB | 3 | Medium |
| CDN | 1 | Medium |

---

## 6. Control Gap Analysis

### 6.1 Controls Inventory

| Control | Status | Verified in Code |
|---|---|---|
| File content validation | Planned | No |
| ASGI upload size limits | Planned | No |
| Path traversal prevention | Planned | No |
| Subprocess isolation for GIS | Planned | No |
| Parameterized SQL queries | Planned | No |
| No shell execution with user input | Planned | No |
| Structured safe logging | Planned | No |
| GraphQL depth/complexity limits | Planned | No |
| Celery task timeouts | Planned | No |
| No secrets in code | Planned | No |
| Raw uploads outside web root | Planned | No |
| CDN tile caching | Planned | No |
| PgBouncer connection pooling | Planned | No |
| React JSX auto-escaping | Inherent to framework | No |

**All 14 documented controls are plans, not implementations. None are
verified in code because no implementation code exists.**

### 6.2 Missing Controls (Not Documented Anywhere)

| Missing Control | Related Threats | Priority |
|---|---|---|
| Authentication | CT-01 | **Critical** |
| Authorization / RBAC | CT-02 | **Critical** |
| Rate limiting | CT-09 | **High** |
| Redis AUTH | CT-05 | **High** |
| Celery JSON serialization | CT-12 | **High** |
| Audit logging | CT-15 | **High** |
| CORS / CSP / security headers | CT-16 | **High** |
| TLS for inter-service communication | CT-10 | **High** |
| Martin layer/access restrictions | CT-11 | **High** |
| Per-service DB credentials | CT-21 | **Medium** |
| Encryption at rest | CT-18 | **Medium** |
| Dependency scanning | CT-25 | **Medium** |
| Data retention policies | CT-26 | **Low** |

### 6.3 Defense in Depth Assessment

The current architecture has **multiple single points of failure**:

1. **No authentication** means the entire perimeter is open
2. **No authorization** means a single compromised account accesses
   everything
3. **Shared DB credentials** across services means any compromised
   component has full database access
4. **Unauthenticated Redis** means any internal network access leads to
   cache poisoning and task injection
5. **Pickle serialization** means Redis access leads to code execution on
   workers

The combination of CT-05 (Redis no AUTH) + CT-12 (pickle) creates a
particularly dangerous chain: network access -> Redis -> RCE on workers ->
full DB access.

---

## 7. Remediation Roadmap

### Immediate (Before Any Production Deployment)

| Priority | Threat | Remediation | Effort |
|---|---|---|---|
| P0 | CT-01 | Design and implement authentication (OAuth2/OIDC) | Large |
| P0 | CT-02 | Implement authorization model with dataset ownership | Large |
| P0 | CT-12 | Set Celery serializer to JSON, disable pickle | Small |
| P0 | CT-05 | Enable Redis AUTH | Small |
| P1 | CT-06 | Implement GraphQL depth/complexity limits | Small |
| P1 | CT-07 | Configure upload size limits | Small |
| P1 | CT-09 | Implement rate limiting | Medium |

### Short-Term (1-2 Sprints After Auth)

| Priority | Threat | Remediation | Effort |
|---|---|---|---|
| P1 | CT-03 | Implement subprocess isolation for GIS parsing | Medium |
| P1 | CT-04 | Implement ZIP path traversal validation | Small |
| P1 | CT-13 | Implement zip bomb detection (ratio + size limits) | Small |
| P1 | CT-14 | Sanitize feature properties at ingestion | Small |
| P1 | CT-15 | Implement audit logging | Medium |
| P1 | CT-16 | Configure CORS, CSP, security headers | Small |
| P2 | CT-17 | Disable GraphQL introspection in production | Small |

### Medium-Term (1-3 Months)

| Priority | Threat | Remediation | Effort |
|---|---|---|---|
| P2 | CT-10 | Enable TLS for all inter-service connections | Medium |
| P2 | CT-11 | Configure Martin with restricted layers and read-only user | Small |
| P2 | CT-21 | Create per-service PostgreSQL users with least privilege | Small |
| P2 | CT-08 | Implement statement_timeout and query complexity limits | Medium |
| P2 | CT-18 | Enable encryption at rest for PostGIS and object storage | Medium |
| P2 | CT-19 | Adopt secrets manager for production | Medium |
| P2 | CT-25 | Enable Dependabot, pip-audit, npm audit in CI | Small |

### Long-Term (Architectural)

| Priority | Threat | Remediation | Effort |
|---|---|---|---|
| P3 | CT-03 | Container-level isolation for GIS processing (gVisor/similar) | Large |
| P3 | CT-24 | Property-level access controls for sensitive attributes | Large |
| P3 | CT-20 | Per-service connection pool tuning based on production metrics | Medium |
| P3 | CT-26 | Data lifecycle management and automated retention enforcement | Medium |

---

## 8. Compliance Mapping

### OWASP Top 10 (2021)

| OWASP | Finding | Status |
|---|---|---|
| A01 Broken Access Control | CT-01, CT-02, CT-11 | **Non-Compliant** |
| A02 Cryptographic Failures | CT-10, CT-18, CT-19 | **Non-Compliant** |
| A03 Injection | Parameterized queries planned (ctrl-05) | Planned |
| A04 Insecure Design | CT-15, no threat model prior to this | **Partially Addressed** |
| A05 Security Misconfiguration | CT-05, CT-16, CT-17 | **Non-Compliant** |
| A06 Vulnerable Components | CT-03, CT-25 | **Non-Compliant** |
| A07 Auth Failures | CT-01, CT-04 (no session mgmt) | **Non-Compliant** |
| A08 Data Integrity Failures | CT-12 (pickle), CT-03 | **Non-Compliant** |
| A09 Logging Failures | CT-15 | **Non-Compliant** |
| A10 SSRF | Not assessed (no outbound URL fetching identified) | N/A |

### OWASP API Security Top 10 (2023)

| OWASP API | Finding | Status |
|---|---|---|
| API1 Broken Object-Level Auth | CT-02 | **Non-Compliant** |
| API2 Broken Authentication | CT-01 | **Non-Compliant** |
| API3 Broken Object Property Auth | CT-24 | **Non-Compliant** |
| API4 Unrestricted Resource Consumption | CT-06, CT-07, CT-08, CT-09 | **Non-Compliant** |
| API5 Broken Function-Level Auth | CT-02 | **Non-Compliant** |
| API6 Unrestricted Access to Sensitive Flows | CT-01, CT-11 | **Non-Compliant** |
| API7 SSRF | Not assessed | N/A |
| API8 Security Misconfiguration | CT-05, CT-16, CT-17 | **Non-Compliant** |
| API9 Improper Inventory Management | CT-17 (introspection) | **Non-Compliant** |
| API10 Unsafe Consumption of APIs | CT-03 (native libs) | **Partially Addressed** |

### SOC 2 Trust Service Criteria (Relevant)

| Criteria | Finding | Status |
|---|---|---|
| CC6.1 Logical access security | CT-01, CT-02 | **Non-Compliant** |
| CC6.2 Auth prior to access | CT-01 | **Non-Compliant** |
| CC6.3 Auth for changes | CT-02 | **Non-Compliant** |
| CC7.1 Detection of changes | CT-15 | **Non-Compliant** |
| CC7.2 Monitoring | CT-15 | **Non-Compliant** |
| CC6.7 Data transmission encryption | CT-10 | **Non-Compliant** |

---

## 9. Appendices

### A. CycloneDX Threat Model JSON

The complete consolidated CycloneDX Threat Modeling Blueprint 2.0 JSON is
available at [07-consolidated.json](07-consolidated.json).

### B. Diagram Set

- ASCII and Mermaid diagrams: [08-diagrams.md](08-diagrams.md)
- PlantUML C4 and sequence diagrams: [09-visual-designs.md](09-visual-designs.md)

### C. Upstream Analysis Artifacts

- Repository reconnaissance: [05-repo-recon.json](05-repo-recon.json)
- Document absorption: [06-doc-absorption.json](06-doc-absorption.json)
- STRIDE analysis: [00-stride-interview.json](00-stride-interview.json)

### D. Documents Reviewed

| Document | Purpose |
|---|---|
| INITIAL-PLAN.md | System design, data model, user flows, security requirements, delivery phases |
| ARCHITECTURE.md | Tech stack, architecture diagram, API design, scale requirements, risks |
| CODING-CONVENTIONS.md | Code style, security rules (Section 10), error handling, testing tiers |
| README.md | Project overview, contributing guide, key capabilities |
| REQUIREMENT-TEMPLATE.md | Issue template structure |

### E. Glossary

| Term | Definition |
|---|---|
| CRS | Coordinate Reference System — defines how coordinates map to Earth locations |
| EPSG:4326 | WGS 84 geographic coordinate system (latitude/longitude) |
| GeoJSON | JSON-based format for geospatial data |
| GeoParquet | Parquet file format with geospatial metadata |
| MVT | Mapbox Vector Tiles — binary format for vector tile data |
| PostGIS | PostgreSQL extension for spatial data types and functions |
| Shapefile | Esri format for vector GIS data (distributed as ZIP of .shp, .shx, .dbf files) |
| STRIDE | Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege |
| WKT | Well-Known Text — text representation of geometry |
