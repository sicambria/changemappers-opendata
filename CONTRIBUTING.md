# Contributing to Changemappers Open Data

**Part of [changemappers.org](https://changemappers.org/) — Mapping pathways to regenerative futures**

Thank you for your interest in contributing to Changemappers Open Data! This document provides guidelines and instructions for contributing.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Contributing Data](#contributing-data)
  - [Contributing Code](#contributing-code)
  - [Improving Documentation](#improving-documentation)
- [Data Quality Standards](#data-quality-standards)
- [Pull Request Process](#pull-request-process)
- [Style Guides](#style-guides)
- [Getting Help](#getting-help)

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the team via https://changemappers.org/.

---

## How to Contribute

### Contributing Data

We welcome data contributions that align with our ontology and quality standards.

#### Before You Submit Data

1. **Check existing data** — Browse `data/entities/` and `data/relationships/` to avoid duplicates
2. **Review the ontology** — Ensure your data matches our entity and relationship types in `ontology/`
3. **Validate your data** — Use schemas in `schemas/entities/` to validate your JSON files

#### Data Submission Process

1. **Fork the repository** and create a branch for your data contribution
2. **Add your data files** to the appropriate directory:
   - Entities → `data/entities/`
   - Relationships → `data/relationships/`
3. **Follow naming conventions**:
   - Use lowercase with hyphens: `organization-name.json`
   - Include type prefix for disambiguation: `org-patagonia.json`
4. **Validate your files** against the appropriate schema
5. **Submit a pull request** with a clear description of your contribution

#### Data Requirements

Each entity record must include:
- `id`: Unique identifier (UUID or semantic ID)
- `type`: Entity type from our ontology
- `name`: Human-readable name
- `created_at`: ISO 8601 timestamp
- `sources`: Array of source references
- `confidence`: Data quality score (0-1)

Example entity:
```json
{
  "id": "org-patagonia",
  "type": "Organization",
  "name": "Patagonia",
  "description": "Outdoor apparel company known for environmental activism",
  "created_at": "2024-01-15T10:30:00Z",
  "sources": [
    {"type": "website", "url": "https://patagonia.com", "retrieved": "2024-01-15"}
  ],
  "confidence": 0.95,
  "archetypes": ["b-corporation", "regenerative-agriculture"]
}
```

#### What We Welcome

- New entities matching our ontology
- Corrections to existing data
- Additional relationship connections
- Source citations for uncited data
- Translations and localizations

#### What We Don't Accept

- Data without sources
- Personal information without consent
- Copyrighted material without permission
- Promotional or spam content
- Data that violates our Code of Conduct

---

### Contributing Code

We welcome code contributions for data processing, API development, and tooling.

#### Development Setup

1. **Prerequisites**:
   - Python 3.10+ (for data scripts)
   - Node.js 18+ (for API tools)
   - Git

2. **Clone and setup**:
   ```bash
   git clone https://github.com/changemappers/changemappers-opendata.git
   cd changemappers-opendata
   ```

3. **Install dependencies**:
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node.js dependencies (if applicable)
   npm install
   ```

#### Code Contribution Process

1. **Create an issue** — Discuss your proposed changes before starting work
2. **Fork and branch** — Create a feature branch from `main`
3. **Write code** — Follow our style guides below
4. **Write tests** — Add tests for new functionality
5. **Run tests** — Ensure all tests pass
6. **Submit PR** — Create a pull request with clear description

#### Code Style

- Python: Follow PEP 8, use `black` for formatting
- JavaScript: Follow ESLint configuration
- JSON: 2-space indentation, trailing newlines

---

### Improving Documentation

Documentation improvements are always welcome!

- Fix typos and clarify existing documentation
- Add examples and use cases
- Translate documentation to other languages
- Update API documentation for changes

---

## Data Quality Standards

### Confidence Scoring

We use confidence scores to indicate data quality:

| Score | Description | Criteria |
|-------|-------------|----------|
| 0.95-1.0 | Verified | Multiple reliable sources, direct confirmation |
| 0.80-0.94 | High confidence | One reliable source, consistent with related data |
| 0.60-0.79 | Medium confidence | Inferred from patterns, single unverified source |
| 0.40-0.59 | Low confidence | Uncertain, needs verification |
| 0.00-0.39 | Unverified | No sources, placeholder data |

### Source Requirements

All data must include sources:
- Prefer primary sources (official websites, official documents)
- Include retrieval date for web sources
- Use permanent URLs when available
- Note if source requires translation or interpretation

### Validation

All data is validated against JSON schemas in `schemas/`. Validation is automated in our CI pipeline.

To validate locally:
```bash
# Using Python
python scripts/validate.py data/entities/

# Using Node.js
npm run validate
```

---

## Pull Request Process

1. **Small, focused PRs** — One logical change per PR
2. **Descriptive title** — Clear summary of changes
3. **Fill out the PR template** — Include:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if applicable)
4. **Pass all checks** — CI must pass before review
5. **Address review feedback** — Respond to all comments
6. **Maintainer approval** — At least one maintainer must approve

### PR Checklist

- [ ] Code/data follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new warnings introduced

---

## Style Guides

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `data:` Data addition or correction
- `docs:` Documentation changes
- `style:` Formatting, no code changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance

Example:
```
data: add regenerative agriculture organizations

Add 15 new organizations focused on regenerative agriculture
and permaculture. Includes relationships to relevant networks.

Closes #42
```

### JSON Formatting

- 2-space indentation
- Keys in alphabetical order (except id, type, name first)
- Trailing newline
- No trailing commas
- Use UTF-8 encoding

---

## Getting Help

- **Documentation**: Browse `docs/` directory
- **Questions**: Open a GitHub issue with the `question` label
- **Discussions**: Join discussions at https://changemappers.org/
- **Issues**: Report bugs or suggest features via GitHub Issues

---

## Recognition

Contributors are recognized in:
- Our contributor list (updated automatically)
- Release notes for significant contributions
- Special recognition for major data contributions

---

*Thank you for helping map pathways to regenerative futures!*

*https://changemappers.org/*
