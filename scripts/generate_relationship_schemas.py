#!/usr/bin/env python3
"""
Relationship Schema Generator for changemappers.org

Generates specific JSON schemas for each relationship type defined in ontology/relationships/*.yml
Uses the base relationship schema as template and adds type-specific properties.

Usage:
    python scripts/generate_relationship_schemas.py --dry-run
    python scripts/generate_relationship_schemas.py --fix
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

PROJECT_ROOT = Path(__file__).parent.parent
ONTOLOGY_DIR = PROJECT_ROOT / "ontology" / "relationships"
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "relationships"


def load_yaml(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def generate_relationship_schema(ontology: dict) -> dict:
    rel_id = ontology.get("id", "unknown")
    
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": f"https://changemappers.org/schemas/relationships/{rel_id}.schema.json",
        "title": ontology.get("name", rel_id.replace("_", " ").title()),
        "description": ontology.get("description", ""),
        "type": "object",
        "required": ["id", "source_id", "target_id", "relationship_type"],
        "additionalProperties": True,
        "properties": {
            "id": {
                "type": "string",
                "format": "uuid",
                "description": "Unique identifier for the relationship",
            },
            "source_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the source entity",
            },
            "target_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the target entity",
            },
            "relationship_type": {
                "type": "string",
                "const": rel_id,
                "description": "Type of relationship",
            },
            "source_type": {
                "type": "string",
                "description": "Type of the source entity",
            },
            "target_type": {
                "type": "string",
                "description": "Type of the target entity",
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence score for this relationship (0-1)",
            },
            "source_reference": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["official", "news", "research", "social", "government", "ngo", "corporate", "other"],
                    },
                    "name": {"type": "string"},
                    "url": {"type": "string", "format": "uri"},
                    "retrieved_at": {"type": "string", "format": "date-time"},
                },
                "required": ["type", "name"],
                "description": "Source of the relationship information",
            },
            "valid_from": {
                "type": "string",
                "format": "date-time",
                "description": "When the relationship became valid",
            },
            "valid_to": {
                "type": "string",
                "format": "date-time",
                "description": "When the relationship ceased to be valid",
            },
            "is_current": {
                "type": "boolean",
                "description": "Whether the relationship is currently active",
            },
            "created_at": {
                "type": "string",
                "format": "date-time",
                "description": "When this record was created",
            },
            "updated_at": {
                "type": "string",
                "format": "date-time",
                "description": "When this record was last updated",
            },
            "notes": {
                "type": "string",
                "description": "Additional notes about the relationship",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for categorizing the relationship",
            },
        },
    }
    
    allowed_from = ontology.get("allowed_from", [])
    if allowed_from:
        schema["properties"]["source_type"]["enum"] = allowed_from
    
    allowed_to = ontology.get("allowed_to", [])
    if allowed_to:
        schema["properties"]["target_type"]["enum"] = allowed_to
    
    properties = ontology.get("properties", {})
    for prop_name, prop_def in properties.items():
        prop_schema = {}
        prop_type = prop_def.get("type", "string")
        
        if prop_type == "string":
            prop_schema["type"] = "string"
        elif prop_type == "number":
            prop_schema["type"] = "number"
        elif prop_type == "integer":
            prop_schema["type"] = "integer"
        elif prop_type == "boolean":
            prop_schema["type"] = "boolean"
        elif prop_type == "date":
            prop_schema["type"] = "string"
            prop_schema["format"] = "date"
        elif prop_type == "datetime":
            prop_schema["type"] = "string"
            prop_schema["format"] = "date-time"
        else:
            prop_schema["type"] = "string"
        
        prop_schema["description"] = prop_def.get("description", "")
        
        if prop_def.get("required"):
            schema["required"].append(prop_name)
        
        schema["properties"][prop_name] = prop_schema
    
    schema["x-inverse"] = ontology.get("inverse")
    schema["x-cardinality"] = ontology.get("cardinality", "many-to-many")
    
    return schema


def main():
    parser = argparse.ArgumentParser(description="Generate relationship schemas from ontology")
    parser.add_argument("--fix", action="store_true", help="Write schemas to files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    relationships = sorted(ONTOLOGY_DIR.glob("*.yml"))
    
    if not relationships:
        print("No relationship ontologies found")
        sys.exit(1)
    
    print(f"Found {len(relationships)} relationship types")
    print()
    
    generated = 0
    for rel_path in relationships:
        ontology = load_yaml(rel_path)
        if not ontology:
            print(f"[ERROR] Failed to load: {rel_path.name}")
            continue
        
        rel_id = ontology.get("id", rel_path.stem)
        schema = generate_relationship_schema(ontology)
        
        schema_path = SCHEMAS_DIR / f"{rel_id}.schema.json"
        
        if args.verbose:
            print(f"[{rel_id}]")
            print(f"  Name: {ontology.get('name')}")
            print(f"  From: {ontology.get('allowed_from', [])}")
            print(f"  To: {ontology.get('allowed_to', [])}")
            print(f"  Properties: {list(ontology.get('properties', {}).keys())}")
            print(f"  Inverse: {ontology.get('inverse')}")
            print()
        
        if args.dry_run:
            print(f"[{rel_id}] Would write: {schema_path}")
        elif args.fix:
            save_json(schema, schema_path)
            print(f"[{rel_id}] Wrote: {schema_path}")
        
        generated += 1
    
    print()
    print(f"Generated {generated} relationship schemas")
    
    if args.dry_run:
        print("\nRun with --fix to write schemas")


if __name__ == "__main__":
    main()
