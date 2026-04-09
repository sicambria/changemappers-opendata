#!/usr/bin/env python3
"""
Schema Reconciliation Tool for changemappers.org

Merges JSON schemas with ontology YAML definitions to create complete schemas.
Strategy:
- Ontology provides canonical field definitions, types, and enums
- Schema provides JSON Schema specifics (format, pattern, constraints)
- Merge both, using ontology as source of truth for field definitions

Usage:
    python scripts/reconcile_schemas.py --dry-run
    python scripts/reconcile_schemas.py --fix
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

PROJECT_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "entities"
ONTOLOGY_DIR = PROJECT_ROOT / "ontology" / "entities"


def load_json(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


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


def map_ontology_type_to_json_schema(field: dict) -> dict:
    ontology_type = field.get("type", "string")
    enum_values = field.get("enum_values")
    
    result = {}
    
    if enum_values:
        result["type"] = "string"
        result["enum"] = enum_values
        result["description"] = field.get("description", "")
        return result
    
    type_mapping = {
        "string": {"type": "string"},
        "integer": {"type": "integer"},
        "number": {"type": "number"},
        "boolean": {"type": "boolean"},
        "datetime": {"type": "string", "format": "date-time"},
        "date": {"type": "string", "format": "date"},
        "object": {"type": "object"},
    }
    
    if "array" in ontology_type:
        result["type"] = "array"
        item_type = ontology_type.replace("array[", "").replace("]", "")
        if item_type == "string":
            result["items"] = {"type": "string"}
        elif item_type == "object":
            result["items"] = {"type": "object"}
        else:
            result["items"] = {"type": "string"}
    elif ontology_type in type_mapping:
        result.update(type_mapping[ontology_type])
    else:
        result["type"] = "string"
    
    result["description"] = field.get("description", "")
    return result


def reconcile_entity(entity_name: str) -> dict:
    schema_path = SCHEMAS_DIR / f"{entity_name}.schema.json"
    ontology_path = ONTOLOGY_DIR / f"{entity_name}.yml"
    
    result = {
        "entity": entity_name,
        "schema_path": str(schema_path),
        "ontology_path": str(ontology_path),
        "changes": [],
        "errors": [],
    }
    
    schema = load_json(schema_path)
    ontology = load_yaml(ontology_path)
    
    if not ontology:
        result["errors"].append("Ontology file not found or invalid")
        return result
    
    if not schema:
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f"https://changemappers.org/schemas/entities/{entity_name}.schema.json",
            "title": entity_name.replace("_", " ").title(),
            "description": ontology.get("description", ""),
            "type": "object",
            "required": [],
            "additionalProperties": False,
            "properties": {},
        }
        result["changes"].append("Created new schema from ontology")
    
    ontology_fields = ontology.get("schema", {}).get("fields", [])
    
    required_fields = []
    properties = {}
    
    for field in ontology_fields:
        field_name = field.get("name")
        if not field_name:
            continue
        
        field_schema = map_ontology_type_to_json_schema(field)
        
        if field.get("required"):
            required_fields.append(field_name)
        
    existing_prop = schema.get("properties", {}).get(field_name, {})
    if existing_prop:
        if "enum" in field_schema and field_schema.get("enum") != existing_prop.get("enum"):
            result["changes"].append(
                f"Updated {field_name} enum: {existing_prop.get('enum')} -> {field_schema['enum']}"
            )
            existing_prop["enum"] = field_schema["enum"]
        for key in ["description", "type", "format", "items"]:
            if key in field_schema and field_schema[key] != existing_prop.get(key):
                if key == "type" and existing_prop.get("enum"):
                    continue
                if key not in ["description"] or not existing_prop.get(key):
                    existing_prop[key] = field_schema[key]
        properties[field_name] = existing_prop
    else:
        properties[field_name] = field_schema
        result["changes"].append(f"Added field: {field_name}")
    
    for prop_name, prop_value in schema.get("properties", {}).items():
        if prop_name not in properties:
            properties[prop_name] = prop_value
    
    schema["properties"] = properties
    
    ontology_required = [f["name"] for f in ontology_fields if f.get("required")]
    for req in ontology_required:
        if req not in schema.get("required", []):
            if req not in schema.get("required", []):
                schema.setdefault("required", []).append(req)
    
    schema["required"] = list(set(schema.get("required", []) + required_fields))
    
    if "id" not in schema["required"]:
        schema["required"].insert(0, "id")
    
    result["schema"] = schema
    return result


def reconcile_all(entity_filter: str | None = None) -> list[dict]:
    entities = set()
    
    for schema_file in SCHEMAS_DIR.glob("*.schema.json"):
        entities.add(schema_file.stem)
    
    for ontology_file in ONTOLOGY_DIR.glob("*.yml"):
        entities.add(ontology_file.stem)
    
    if entity_filter:
        entities = {e for e in entities if e == entity_filter}
    
    results = []
    for entity in sorted(entities):
        result = reconcile_entity(entity)
        results.append(result)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Reconcile schemas with ontology definitions")
    parser.add_argument("--entity", "-e", help="Reconcile specific entity")
    parser.add_argument("--fix", action="store_true", help="Apply fixes to schema files")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    
    args = parser.parse_args()
    
    results = reconcile_all(args.entity)
    
    for result in results:
        entity = result["entity"]
        changes = result.get("changes", [])
        errors = result.get("errors", [])
        
        if errors:
            print(f"\n[{entity}] ERRORS:")
            for err in errors:
                print(f"  - {err}")
        elif changes:
            print(f"\n[{entity}] CHANGES ({len(changes)}):")
            if args.verbose:
                for change in changes:
                    print(f"  - {change}")
            else:
                print(f"  {len(changes)} changes pending")
        else:
            print(f"\n[{entity}] OK - No changes needed")
        
        if (args.fix or args.dry_run) and "schema" in result:
            if args.dry_run:
                print(f"  Would write: {result['schema_path']}")
            else:
                save_json(result["schema"], Path(result["schema_path"]))
                print(f"  Wrote: {result['schema_path']}")
    
    total_changes = sum(len(r.get("changes", [])) for r in results)
    total_errors = sum(len(r.get("errors", [])) for r in results)
    
    print(f"\n{'='*60}")
    print(f"Total entities: {len(results)}")
    print(f"Entities with changes: {sum(1 for r in results if r.get('changes'))}")
    print(f"Total changes: {total_changes}")
    print(f"Total errors: {total_errors}")
    
    if args.dry_run:
        print("\nRun with --fix to apply changes")
    
    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
