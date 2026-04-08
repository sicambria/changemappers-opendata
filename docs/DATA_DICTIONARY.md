# ChangeMappers Data Dictionary

## Overview

This data dictionary provides comprehensive documentation of all entities, fields, and relationships in the ChangeMappers Open Data ecosystem. It serves as the authoritative reference for data structure and semantics.

## Version Information

| Item | Value |
|------|-------|
| Version | 1.0.0 |
| Last Updated | 2024-06-20 |
| Schema Standard | JSON Schema Draft-07 |

## Entity Summary

| Entity | Description | Documentation |
|--------|-------------|---------------|
| Actor | Individual or entity in change processes | [actor.md](entities/actor.md) |
| Organization | Structured entity (NGO, corporation, etc.) | [organization.md](entities/organization.md) |
| Initiative | Coordinated change effort | [initiative.md](entities/initiative.md) |
| Cause | Social/environmental/economic issue | [cause.md](entities/cause.md) |
| Pattern | Reusable solution approach | [pattern.md](entities/pattern.md) |
| Story | Narrative account of change | [story.md](entities/story.md) |
| Skill | Capability or competency | [skill.md](entities/skill.md) |
| Tool | Instrument or resource for change | [tool.md](entities/tool.md) |
| Location | Geographic place or area | [location.md](entities/location.md) |

## Core Field Types

### Identifiers

| Field | Type | Pattern | Description |
|-------|------|---------|-------------|
| `id` | UUID | RFC 4122 | Unique identifier |
| `slug` | string | `^[a-z0-9]+(?:-[a-z0-9]+)*$` | URL-friendly identifier |

### Timestamps

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `created_at` | datetime | ISO 8601 | Creation timestamp |
| `updated_at` | datetime | ISO 8601 | Last update timestamp |
| `published_at` | datetime | ISO 8601 | Publication timestamp |

### Text Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | string | 1-200 chars | Entity name |
| `title` | string | 1-200 chars | Entity title |
| `description` | string | max 5000 chars | Full description |
| `summary` | string | max 500 chars | Brief summary |
| `bio` | string | max 2000 chars | Biographical text |

### Contact Fields

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `email` | string | Email format | Email address |
| `phone` | string | `^\+?[0-9\-\s]+$` | Phone number |
| `website` | string | URI format | Website URL |

### Geographic Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `latitude` | number | -90 to 90 | Geographic latitude |
| `longitude` | number | -180 to 180 | Geographic longitude |
| `country` | string | ISO 3166-1 alpha-2 | Country code |

## Enumerations

### Actor Types

| Value | Description |
|-------|-------------|
| `individual` | Single person |
| `collective` | Informal group |
| `organization` | Formal organization (use Organization entity) |
| `network` | Network or alliance |

### Organization Types

| Value | Description |
|-------|-------------|
| `ngo` | Non-governmental organization |
| `nonprofit` | Nonprofit organization |
| `corporation` | For-profit corporation |
| `government` | Government body or agency |
| `grassroots` | Grassroots community organization |
| `network` | Network or coalition |
| `foundation` | Philanthropic foundation |
| `cooperative` | Cooperative enterprise |
| `community_organization` | Local community organization |
| `academic` | Academic institution |
| `research_institute` | Research institute |

### Initiative Status

| Value | Description |
|-------|-------------|
| `planning` | Being planned |
| `active` | Actively running |
| `paused` | Temporarily paused |
| `completed` | Completed |
| `archived` | Archived |

### Cause Types

| Value | Description |
|-------|-------------|
| `environmental` | Environmental issues |
| `social` | Social issues |
| `economic` | Economic issues |
| `political` | Political issues |
| `cultural` | Cultural issues |
| `health` | Health issues |
| `educational` | Educational issues |
| `technological` | Technology-related issues |

### Urgency Levels

| Value | Description |
|-------|-------------|
| `low` | Low urgency |
| `medium` | Medium urgency |
| `high` | High urgency |
| `critical` | Critical urgency |

### Geographic Scope

| Value | Description |
|-------|-------------|
| `local` | Local/community level |
| `regional` | Regional level |
| `national` | National level |
| `international` | International level |
| `global` | Global level |

### Pattern Categories

| Value | Description |
|-------|-------------|
| `engagement` | Community and stakeholder engagement |
| `governance` | Decision-making and governance |
| `communication` | Communication and messaging |
| `resource_mobilization` | Resource and funding mobilization |
| `capacity_building` | Skills and capacity development |
| `advocacy` | Advocacy and policy change |
| `monitoring` | Monitoring and evaluation |
| `collaboration` | Collaboration and partnership |
| `decision_making` | Decision-making processes |
| `implementation` | Implementation approaches |

### Skill Categories

| Value | Description |
|-------|-------------|
| `communication` | Communication skills |
| `leadership` | Leadership skills |
| `technical` | Technical skills |
| `analytical` | Analytical skills |
| `interpersonal` | Interpersonal skills |
| `organizational` | Organizational skills |
| `creative` | Creative skills |
| `strategic` | Strategic skills |
| `advocacy` | Advocacy skills |
| `research` | Research skills |

### Skill Levels

| Value | Description |
|-------|-------------|
| `beginner` | Basic understanding and awareness |
| `intermediate` | Can apply with guidance |
| `advanced` | Can apply independently |
| `expert` | Can teach and mentor others |

### Difficulty Levels

| Value | Description |
|-------|-------------|
| `beginner` | No prior experience needed |
| `intermediate` | Some experience helpful |
| `advanced` | Significant experience required |
| `expert` | Expert-level skills needed |

### Visibility Levels

| Value | Description |
|-------|-------------|
| `public` | Visible to all |
| `private` | Visible to author only |
| `restricted` | Visible to specific groups |

### Function Categories

| Value | Description |
|-------|-------------|
| `governance` | Governance functions |
| `operations` | Operations functions |
| `engagement` | Engagement functions |
| `learning` | Learning functions |
| `communication` | Communication functions |
| `mobilization` | Mobilization functions |
| `support` | Support functions |
| `coordination` | Coordination functions |
| `monitoring` | Monitoring functions |
| `financing` | Financing functions |

## Relationship Types

### Entity-to-Entity Relationships

| Source | Target | Relationship | Description |
|--------|--------|--------------|-------------|
| Actor | Organization | `affiliated_with` | Actor affiliated with organization |
| Actor | Initiative | `participates_in` | Actor participates in initiative |
| Actor | Location | `located_in` | Actor located in place |
| Organization | Initiative | `leads` | Organization leads initiative |
| Organization | Organization | `parent_of` | Parent/child organization |
| Organization | Organization | `partner_of` | Partnership relationship |
| Initiative | Cause | `addresses` | Initiative addresses cause |
| Initiative | Location | `operates_in` | Initiative operates in location |
| Pattern | Tool | `supported_by` | Pattern supported by tool |
| Skill | Actor | `possessed_by` | Skill possessed by actor |

### Hierarchical Relationships

| Relationship | Description |
|--------------|-------------|
| `parent_cause` | Broader cause category |
| `sub_causes` | Narrower cause aspects |
| `parent_domain` | Broader domain |
| `subdomains` | Narrower domains |
| `parent_location` | Broader location |
| `child_locations` | Narrower locations |
| `parent_organization` | Parent organization |
| `child_organizations` | Subsidiary organizations |
| `parent_scale` | Broader scale |
| `child_scales` | Narrower scales |

## Validation Patterns

### Common Patterns

| Field | Pattern | Example |
|-------|---------|---------|
| UUID | RFC 4122 | `550e8400-e29b-41d4-a716-446655440000` |
| Slug | `^[a-z0-9]+(?:-[a-z0-9]+)*$` | `jane-doe` |
| Email | Standard email | `user@example.com` |
| Phone | `^\+?[0-9\-\s]+$` | `+1-555-123-4567` |
| Country Code | ISO 3166-1 alpha-2 | `US`, `AR`, `FR` |
| Language Code | ISO 639-1 | `en`, `es`, `fr` |
| Currency | ISO 4217 | `USD`, `EUR`, `ARS` |

### JSON Schema Location

All schemas are located at: `schemas/entities/*.schema.json`

## Taxonomy References

- [Domain Taxonomy](taxonomies/domains.md)
- [Scale Taxonomy](taxonomies/scales.md)
- [Function Taxonomy](taxonomies/functions.md)

## Additional Entity Documentation

Additional entities not covered in detail:

| Entity | Description | Schema |
|--------|-------------|--------|
| Project | Specific project activity | project.schema.json |
| Event | Time-bound occurrence | event.schema.json |
| Outcome | Expected or achieved result | outcome.schema.json |
| Impact | Measured impact | impact.schema.json |
| Indicator | Measurement indicator | indicator.schema.json |
| Metric | Quantitative measurement | metric.schema.json |
| Resource | Available resource | resource.schema.json |
| Media | Media file | media.schema.json |
| Citation | Reference/citation | citation.schema.json |
| Framework | Conceptual framework | framework.schema.json |
| Methodology | Methodological approach | methodology.schema.json |

## Contact

For questions about the data dictionary:
- GitHub Issues: [changemappers-opendata/issues](https://github.com/changemappers/changemappers-opendata/issues)
- Documentation: [docs/](.)
