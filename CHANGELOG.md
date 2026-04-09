# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Part of [changemappers.org](https://changemappers.org/) — Mapping pathways to regenerative futures**

---

## [1.1.0] - 2026-04-09

### Added

#### Schema Completion
- Reconciled all 35 entity JSON schemas with ontology YAML definitions
- Generated 20 relationship type schemas from ontology definitions
- Created schema validation and fix scripts (`scripts/validate_schemas.py`, `scripts/fix_schemas.py`)
- Enum values now align with ontology definitions

#### Data Import
- Transformed 434 legacy records to canonical format
- 8 legacy files transformed: tools, causes, patterns, stories, frameworks, traditions, programs, skills

#### API Implementation
- FastAPI-based REST API with read-only GET endpoints
- Entity endpoints: `/v1/{entity_type}`, `/v1/{entity_type}/{id}`
- Search endpoint: `/v1/search` with full-text search
- Graph traversal endpoint: `/v1/graph/{entity_id}`
- Taxonomies endpoint: `/v1/taxonomies`
- Health check: `/v1/health`
- Automatic OpenAPI documentation at `/v1/docs`

#### Geographic Data
- 8 GeoJSON layers available in `geo/layers/`

#### Scripts
- `scripts/validate_schemas.py` - Audit schema-ontology alignment
- `scripts/fix_schemas.py` - Apply ontology-based fixes
- `scripts/generate_relationship_schemas.py` - Generate relationship schemas
- `scripts/transform_legacy.py` - Transform legacy data

---

## [1.0.0] - 2024-01-15

### Added

#### Ontology
- Initial ontology definitions for 35 entity types across 6 categories
- Initial relationship types for 20 relationship types across 6 categories
- Taxonomy definitions for changemaker archetypes and classifications
- Meta-archetype system framework documentation

#### Data Structure
- Repository structure with organized directories for:
  - `data/` - Core datasets (entities, relationships)
  - `ontology/` - Entity and relationship type definitions
  - `schemas/` - JSON Schema validation schemas
  - `api/` - API specifications and endpoints
  - `catalog/` - Data catalog and metadata
  - `docs/` - Documentation
  - `geo/` - Geographic data and boundaries
  - `md/` - Knowledge base (archetypes, practices)
  - `scripts/` - Data processing scripts
  - `research/` - Research outputs and analysis

#### Documentation
- README.md with project overview and quick start guide
- LICENSE file with dual licensing (CC-BY-SA 4.0 for data, AGPL v3 for code)
- CONTRIBUTING.md with contribution guidelines
- CODE_OF_CONDUCT.md based on Contributor Covenant
- CHANGELOG.md for version history

#### Archetype Frameworks
- Meta-archetype system documentation (`00_meta_archetype_system.md`)
- Change network archetypes (12 movement types)
- Transition-temporal archetypes
- Organizational archetypes
- Resource archetypes
- Knowledge archetypes
- Scale archetypes
- Failure archetypes
- Relationship archetypes

#### Practice Documentation
- "The Architecture of Grassroots Transformation Nonviolent"
- "Reconnecting with the More-Than-Human World"

#### GitHub Infrastructure
- Issue templates for bug reports, feature requests, and data contributions
- Pull request templates
- GitHub Actions workflows for validation

### Security

- Data validation requirements for all contributions
- Source citation requirements for all data
- Privacy guidelines for personal information
- Code of Conduct enforcement procedures

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2026-04-09 | MVP: Schema completion, data import, FastAPI implementation |
| 1.0.0 | 2024-01-15 | Initial release with ontology, documentation, and archetype frameworks |

---

## Upcoming Features

The following are planned for future releases:

### [1.2.0] - Planned
- Search and query API enhancements
- Data quality dashboard
- Automated data validation CI/CD
- Bulk import tools
- Write operations (POST/PUT/DELETE)

### [2.0.0] - Planned
- Graph database integration
- Real-time collaboration features
- Advanced relationship mapping
- Integration with changemappers.org platform

---

## How to Contribute to This Changelog

When submitting a pull request, please add an entry to the `[Unreleased]` section (or create it if it doesn't exist) describing your changes. Use the following categories:

- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes

---

*Changelog maintained by the Changemappers team*
*https://changemappers.org/*
