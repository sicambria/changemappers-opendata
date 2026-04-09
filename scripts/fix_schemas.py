#!/usr/bin/env python3
"""
Bulk Schema Fixer for changemappers.org

Updates all entity JSON schemas to align with ontology YAML definitions.
This script:
1. Reads ontology YML files as source of truth
2. Updates corresponding JSON schema enums to match ontology
3. Adds missing fields from ontology to schemas
"""

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
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "entities"
ONTOLOGY_DIR = PROJECT_ROOT / "ontology" / "entities"


def load_yaml(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def load_json(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_json_type_for_ontology(field: dict) -> dict:
    ontology_type = field.get("type", "string")
    enum_values = field.get("enum_values")
    
    if enum_values:
        return {
            "type": "string",
            "enum": enum_values,
            "description": field.get("description", ""),
        }
    
    type_map = {
        "string": {"type": "string"},
        "integer": {"type": "integer"},
        "number": {"type": "number"},
        "boolean": {"type": "boolean"},
        "datetime": {"type": "string", "format": "date-time"},
        "date": {"type": "string", "format": "date"},
        "object": {"type": "object"},
    }
    
    if "array" in ontology_type:
        item_type = ontology_type.replace("array[", "").replace("]", "")
        return {
            "type": "array",
            "items": {"type": "string" if item_type == "string" else "object"},
            "description": field.get("description", ""),
        }
    
    result = type_map.get(ontology_type, {"type": "string"}).copy()
    result["description"] = field.get("description", "")
    return result


def fix_entity_schema(entity_name: str, dry_run: bool = False) -> dict:
    schema_path = SCHEMAS_DIR / f"{entity_name}.schema.json"
    ontology_path = ONTOLOGY_DIR / f"{entity_name}.yml"
    
    result = {
        "entity": entity_name,
        "schema_exists": schema_path.exists(),
        "ontology_exists": ontology_path.exists(),
        "changes": [],
        "errors": [],
    }
    
    if not ontology_path.exists():
        result["errors"].append("Ontology file not found")
        return result
    
    ontology = load_yaml(ontology_path)
    if not ontology:
        result["errors"].append("Failed to load ontology")
        return result
    
    schema = load_json(schema_path) if schema_path.exists() else None
    if not schema:
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f"https://changemappers.org/schemas/entities/{entity_name}.schema.json",
            "title": entity_name.replace("_", " ").title(),
            "description": ontology.get("description", ""),
            "type": "object",
            "required": ["id"],
            "additionalProperties": False,
            "properties": {},
        }
        result["changes"].append("Created new schema")
    
    ontology_fields = ontology.get("schema", {}).get("fields", [])
    
    for field in ontology_fields:
        field_name = field.get("name")
        if not field_name:
            continue
        
        field_spec = get_json_type_for_ontology(field)
        
        if field_name in schema.get("properties", {}):
            existing = schema["properties"][field_name]
            
            if "enum" in field_spec:
                if existing.get("enum") != field_spec["enum"]:
                    old_enum = existing.get("enum", [])
                    existing["enum"] = field_spec["enum"]
                    result["changes"].append(
                        f"Updated {field_name} enum: {old_enum} -> {field_spec['enum']}"
                    )
        else:
            schema["properties"][field_name] = field_spec
            result["changes"].append(f"Added field: {field_name}")
    
    for field in ontology_fields:
        if field.get("required") and field.get("name"):
            req_field = field["name"]
            if req_field not in schema.get("required", []):
                schema.setdefault("required", []).append(req_field)
    
    if "id" not in schema.get("required", []):
        schema.setdefault("required", []).insert(0, "id")
    
    result["schema"] = schema
    
    if not dry_run and result["changes"]:
        save_json(schema, schema_path)
    
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix entity schemas to match ontology")
    parser.add_argument("--entity", "-e", help="Fix specific entity")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    entities = set()
    for f in SCHEMAS_DIR.glob("*.schema.json"):
        entities.add(f.stem)
    for f in ONTOLOGY_DIR.glob("*.yml"):
        entities.add(f.stem)
    
    if args.entity:
        entities = {e for e in entities if e == args.entity}
    
    total_changes = 0
    for entity in sorted(entities):
        result = fix_entity_schema(entity, dry_run=args.dry_run)
        
        if result["errors"]:
            print(f"\n[{entity}] ERRORS:")
            for err in result["errors"]:
                print(f"  - {err}")
        elif result["changes"]:
            print(f"\n[{entity}] {'Would apply' if args.dry_run else 'Applied'} {len(result['changes'])} changes:")
            if args.verbose:
                for change in result["changes"]:
                    print(f"  - {change}")
            total_changes += len(result["changes"])
        else:
            print(f"\n[{entity}] OK - No changes needed")
    
    print(f"\n{'='*60}")
    print(f"Total entities: {len(entities)}")
    print(f"Total changes: {total_changes}")
    
    if args.dry_run and total_changes > 0:
        print("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
