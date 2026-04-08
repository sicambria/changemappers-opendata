# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Part of [changemappers.org](https://changemappers.org/) — Mapping pathways to regenerative futures**

---

## [1.1.0] - 2026-04-08

### Added

#### Bulk Import/Export Tools
- Python CLI tool (`scripts/bulk_io.py`) for format conversion
- Support for JSON, CSV, GraphML, and Neo4j formats
- Export entities and relationships to multiple formats simultaneously
- Import from CSV and JSON formats
- Format conversion between all supported formats
- Graph statistics and information commands

#### Advanced WebGL Visualizer
- Three.js-based visualization for 10,000+ nodes
- WebGL rendering with octree-optimized force simulation
- Interactive controls for force strength, link distance, node size, and repulsion
- Mouse drag rotation and zoom navigation
- Color-coded nodes by entity type
- Real-time FPS counter and node/edge statistics
- Load custom JSON graphs or sample data
- Dynamic legend showing node type distribution

#### Simple D3.js Visualizer
- Force-directed graph visualization with D3.js v7
- Drag-and-drop JSON file loading
- Instant load with no server required
- Interactive node dragging and zoom/pan controls
- Adjustable link distance, charge strength, and node size
- Tooltip showing node details on hover
- Color-coded nodes by type with legend
- Sample data loading for testing

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
| 1.1.0 | 2026-04-08 | Bulk import/export tools, WebGL and D3.js visualizers |
| 1.0.0 | 2024-01-15 | Initial release with ontology, documentation, and archetype frameworks |

---

## Upcoming Features

The following are planned for future releases:

### [1.1.0] - Planned
- Complete entity schema definitions for all 35 entity types
- Complete relationship schema definitions for all 20 relationship types
- Initial data import from legacy systems
- API endpoint implementations
- Geographic data for key regions

### [1.2.0] - Planned

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
