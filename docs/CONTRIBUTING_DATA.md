# Data Contribution Guidelines

## Overview

Thank you for your interest in contributing data to ChangeMappers Open Data! This guide explains how to contribute high-quality data that follows our standards and schemas.

## Before You Begin

### What We Accept

We welcome contributions of:
- New entity records (actors, organizations, initiatives, etc.)
- Updates to existing records
- Corrections to inaccurate data
- Additional relationships and connections
- Documentation improvements

### Data Quality Standards

All contributions must meet these standards:

| Standard | Requirement |
|----------|-------------|
| Accuracy | Data must be factually correct |
| Verifiable | Information should be sourceable |
| Complete | Required fields must be filled |
| Consistent | Follow existing naming conventions |
| Relevant | Must relate to change-making activities |

## Contribution Process

### Step 1: Prepare Your Data

1. **Identify the entity type** you're contributing
2. **Review the schema** at `schemas/entities/[entity].schema.json`
3. **Check existing data** to avoid duplicates
4. **Gather required information** for all required fields

### Step 2: Format Your Data

#### JSON Format

Each record should be a valid JSON file following the schema:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "unique-slug",
  "name": "Entity Name",
  "type": "valid_enum_value",
  "description": "Full description...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Field Guidelines

| Field | Guidelines |
|-------|------------|
| `id` | Generate a new UUID v4 |
| `slug` | Lowercase, hyphens only, unique |
| `name` | Official or commonly used name |
| `description` | Clear, objective, informative |
| `tags` | Use existing tags when possible |

### Step 3: Validate Your Data

#### Using JSON Schema

```bash
# Install a JSON validator like ajv-cli
npm install -g ajv-cli

# Validate your file
ajv validate -s schemas/entities/actor.schema.json -d your-data.json
```

#### Common Validation Errors

| Error | Solution |
|-------|----------|
| Missing required field | Add all required fields |
| Invalid enum value | Use exact enum values from schema |
| Invalid format | Check UUID, email, date formats |
| Pattern mismatch | Fix slug pattern (lowercase + hyphens) |

### Step 4: Submit Your Contribution

#### Via GitHub Pull Request

1. Fork the repository
2. Add your data file to the appropriate directory
3. Validate locally
4. Submit a pull request with description
5. Respond to review feedback

#### Via Issue

1. Create a new issue
2. Use the data contribution template
3. Provide all data in the issue
4. Wait for maintainer review

## Entity-Specific Guidelines

### Actors

**Required Fields:**
- `id`, `slug`, `name`, `type`

**Best Practices:**
- Use public information only
- Include bio with consent when possible
- Link to existing organizations
- Use appropriate expertise enums

**Avoid:**
- Private contact information without consent
- Unverified biographical claims
- Duplicate actors

### Organizations

**Required Fields:**
- `id`, `slug`, `name`, `type`

**Best Practices:**
- Use official organization name
- Include founded_date when known
- Link to parent/child organizations
- Use standardized sector enums

**Avoid:**
- Outdated information
- Unofficial names as primary
- Missing geographic context

### Initiatives

**Required Fields:**
- `id`, `slug`, `name`, `status`

**Best Practices:**
- Provide clear description of goals
- Link to lead organizations
- Include timeline with milestones
- Connect to relevant causes

**Avoid:**
- Vague descriptions
- Missing status updates
- Unlinked relationships

### Causes

**Required Fields:**
- `id`, `slug`, `name`

**Best Practices:**
- Use widely recognized names
- Link to parent causes appropriately
- Set urgency based on evidence
- Connect to affected domains

**Avoid:**
- Overlapping duplicate causes
- Subjective urgency ratings
- Missing scope information

### Patterns

**Required Fields:**
- `id`, `slug`, `name`, `category`

**Best Practices:**
- Clear problem statement
- Actionable solution description
- Include implementation steps
- Link to supporting evidence

**Avoid:**
- Vague problem statements
- Theoretical solutions without evidence
- Missing context information

### Stories

**Required Fields:**
- `id`, `slug`, `title`, `type`

**Best Practices:**
- Get consent from author
- Include key lessons learned
- Link to relevant entities
- Use appropriate visibility setting

**Avoid:**
- Publishing without consent
- Identifiable private individuals
- Unverified claims as fact

### Skills

**Required Fields:**
- `id`, `slug`, `name`, `category`

**Best Practices:**
- Use clear, recognizable names
- Define all skill levels
- Link to related skills
- Connect to learning resources

**Avoid:**
- Overlapping duplicate skills
- Undefined skill levels
- Missing assessment criteria

### Tools

**Required Fields:**
- `id`, `slug`, `name`, `type`

**Best Practices:**
- Include website/documentation URLs
- List required skills
- Describe features and limitations
- Link to related patterns

**Avoid:**
- Promotional language
- Missing license information
- Incomplete platform support

### Locations

**Required Fields:**
- `id`, `slug`, `name`, `type`

**Best Practices:**
- Use official place names
- Include coordinates when possible
- Link to parent locations
- Document indigenous territories

**Avoid:**
- Duplicate locations
- Missing country context
- Inaccurate coordinates

## Data Relationships

### Creating Relationships

When linking entities:
1. Use the UUID of the related entity
2. Verify the related entity exists
3. Include appropriate context
4. Update both sides of the relationship

### Relationship Types

| Source | Target | Field |
|--------|--------|-------|
| Actor | Organization | `affiliations[].organization_id` |
| Organization | Initiative | `initiatives[]` |
| Initiative | Cause | `causes[]` |
| Location | Actor | `actors[]` |

## Ethical Guidelines

### Privacy

- **Do not** include private contact information without consent
- **Do not** publish personally identifiable information
- **Do** respect visibility settings
- **Do** anonymize when appropriate

### Consent

- Obtain consent for personal stories
- Respect requests for removal
- Credit authors appropriately
- Honor privacy preferences

### Accuracy

- Cite sources when possible
- Distinguish fact from opinion
- Update outdated information
- Correct errors promptly

### Respect

- Use respectful language
- Honor indigenous territories
- Represent diverse perspectives
- Avoid bias in descriptions

## Review Process

### What to Expect

1. **Initial Check**: Schema validation
2. **Content Review**: Accuracy and relevance
3. **Relationship Verification**: Links validated
4. **Feedback**: Any issues or questions
5. **Approval**: Merge or publication

### Timeline

- Initial review: 1-3 days
- Full review: 1-2 weeks
- Complex contributions: May take longer

## Getting Help

### Questions?

- Check [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- Review [QUICK_START.md](QUICK_START.md)
- Open a GitHub Discussion
- Create an Issue with question label

### Found an Error?

1. Check if already reported
2. Create an issue with details
3. Include the entity ID/slug
4. Provide correction with source

## Recognition

Contributors are acknowledged in:
- Commit history
- Release notes
- Contributors file

Thank you for contributing to open knowledge about social change!
