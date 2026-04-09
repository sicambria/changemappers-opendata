# Changemappers Open Data

[![License: CC-BY-SA 4.0](https://img.shields.io/badge/Data-CC--BY--SA%204.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![License: AGPL v3](https://img.shields.io/badge/Code-AGPL%20v3-blue.svg)]https://www.gnu.org/licenses/agpl-3.0)
[![Data Quality](https://img.shields.io/badge/Data%20Quality-Validated-green.svg)](docs/data-quality.md)
[![Website](https://img.shields.io/badge/Changemappers-Open_Data_Hub-blue)](https://changemappers.org/opendata/)

**Part of [changemappers.org](https://changemappers.org/) — Mapping pathways to regenerative futures**

---

## Overview

Changemappers Open Data provides datasets, frameworks, and structured knowledge emerging from regenerative action research and community co-creation. Our goal is to make insights, patterns, and tools openly accessible to accelerate collective impact and avoid duplicated effort across changemaker initiatives.

This repository contains:
- **35 entity types** covering organizations, people, places, resources, and knowledge
- **20 relationship types** mapping connections across the changemaker ecosystem
- Archetype frameworks for understanding changemaker identities and dynamics
- Structured taxonomies for consistent classification
- API specifications for programmatic access

---

## Repository Structure

```
changemappers-opendata/
├── api/                    # API specifications and endpoints
│   ├── endpoints/          # API endpoint definitions
│   └── graph/              # Graph query interfaces
├── catalog/                # Data catalog and metadata
├── data/                   # Core datasets
│   ├── entities/           # Entity records (JSON)
│   ├── relationships/      # Relationship records (JSON)
│   └── legacy/             # Legacy data imports
├── docs/                   # Documentation
│   ├── entities/           # Entity documentation
│   └── taxonomies/         # Taxonomy documentation
├── geo/                    # Geographic data and boundaries
├── md/                     # Markdown knowledge base
│   ├── archetypes/         # Archetype framework documents
│   └── practices/          # Practice pattern documents
├── ontology/               # Ontology definitions
│   ├── entities/           # Entity type schemas
│   ├── relationships/      # Relationship type schemas
│   └── taxonomies/         # Taxonomy definitions
├── research/               # Research outputs and analysis
├── schemas/                # JSON Schema definitions
│   ├── entities/           # Entity validation schemas
│   └── utilities/          # Shared schema utilities
└── scripts/                # Data processing scripts
```

---

## Quick Start

### Browse the Data

1. Clone the repository:
   ```bash
   git clone https://github.com/changemappers/changemappers-opendata.git
   cd changemappers-opendata
   ```

2. Explore entity types in `ontology/entities/`
3. Browse relationship types in `ontology/relationships/`
4. View actual data in `data/entities/` and `data/relationships/`

### Use the API

API documentation is available in `api/` directory. See [API Documentation](#api-documentation) below.

### Understand the Framework

Start with the meta-archetype system in `md/archetypes/00_meta_archetype_system.md` to understand the conceptual foundation.

---

## Data Catalog

### Entity Types (35)

Our ontology defines 35 entity types organized into the following categories:

| Category | Entity Types |
|----------|--------------|
| **Actors** | Person, Organization, Community, Network, Collective |
| **Places** | Place, Region, Territory, Bioregion, Watershed |
| **Resources** | Resource, Tool, Funding, Land, Building |
| **Knowledge** | Knowledge, Practice, Methodology, Framework, Pattern |
| **Events** | Event, Campaign, Project, Initiative, Program |
| **Systems** | System, Sector, Domain, Ecosystem, Transition Pathway |

See `ontology/entities/` for detailed definitions and schemas.

### Relationship Types (20)

Our relationship types capture connections across the changemaker ecosystem:

| Category | Relationship Types |
|----------|-------------------|
| **Membership** | member_of, affiliated_with, participant_in |
| **Location** | located_in, serves, operates_in |
| **Collaboration** | collaborates_with, partnered_with, funded_by |
| **Knowledge** | created_by, derived_from, applies_to |
| **Impact** | impacts, enables, transforms |
| **Lineage** | parent_of, child_of, successor_to |

See `ontology/relationships/` for detailed definitions.

---

## API Documentation

### Current Status

> **Note:** The API implementation is available in this repository (`api/` directory) but is not yet deployed to a public endpoint. You can run the API locally using the instructions below.

### Running the API Locally

```bash
# Install dependencies
pip install -r api/requirements.txt

# Run the server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Access the API documentation
open http://localhost:8000/v1/docs
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/health` | GET | Health check with entity counts |
| `/v1/{entity_type}` | GET | List entities with pagination and filtering |
| `/v1/{entity_type}/{id}` | GET | Get single entity by ID or slug |
| `/v1/search` | GET | Full-text search across entities |
| `/v1/graph/{id}` | GET | Graph traversal with configurable depth |
| `/v1/taxonomies` | GET | List all entity types with counts |

### API Specifications

Detailed API endpoint specifications are available in `api/endpoints/` directory.

### Rate Limits (when deployed)

- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Contributing data
- Contributing code
- Data quality standards
- Pull request process

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## License

This repository uses dual licensing:

### Data License: CC-BY-SA 4.0

All data files (JSON, CSV, and other data formats) are licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

You are free to:
- Share and redistribute the material
- Adapt, remix, and build upon it

Under the following terms:
- **Attribution** — You must give appropriate credit
- **ShareAlike** — If you remix or transform, you must distribute under the same license

See [LICENSE](LICENSE) for full text or visit https://creativecommons.org/licenses/by-sa/4.0/

### Code License: GNU AGPL v3.0

All code (scripts, API implementations, utilities) is licensed under the GNU Affero General Public License v3.0.

This ensures that:
- You can use, study, and modify the code
- Any modifications must be shared under the same license
- Network use (including SaaS) requires providing source code

See [LICENSE](LICENSE) for full text or visit https://www.gnu.org/licenses/agpl-3.0/

---

## Contact

- **Website:** https://changemappers.org/
- **Open Data Portal:** https://changemappers.org/opendata/
- **Issues:** https://github.com/changemappers/changemappers-opendata/issues

---

*Mapping pathways to regenerative futures*
