#!/usr/bin/env python3
"""
Schema Validation and Audit Tool for changemappers.org

Compares JSON schemas against ontology YAML definitions to identify:
- Field mismatches (names, types, constraints)
- Missing required fields
- Enum value differences
- Incomplete schemas

Usage:
    python scripts/validate_schemas.py
    python scripts/validate_schemas.py --entity actor
    python scripts/validate_schemas.py --fix
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

PROJECT_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "entities"
ONTOLOGY_DIR = PROJECT_ROOT / "ontology" / "entities"
RELATIONSHIPS_DIR = PROJECT_ROOT / "ontology" / "relationships"


def load_json(file_path: Path) -> tuple[dict | None, list[str]]:
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f), errors
    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error: {e}")
    except FileNotFoundError:
        errors.append("File not found")
    except Exception as e:
        errors.append(f"Error loading: {e}")
    return None, errors


def load_yaml(file_path: Path) -> tuple[dict | None, list[str]]:
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), errors
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
    except FileNotFoundError:
        errors.append("File not found")
    except Exception as e:
        errors.append(f"Error loading: {e}")
    return None, errors


def extract_schema_fields(schema: dict) -> dict:
    fields = {}
    props = schema.get("properties", {})
    for name, prop in props.items():
        field_info = {
            "type": prop.get("type", "unknown"),
            "required": name in schema.get("required", []),
            "description": prop.get("description", ""),
            "enum": prop.get("enum"),
            "format": prop.get("format"),
            "min_length": prop.get("minLength"),
            "max_length": prop.get("maxLength"),
        }
        if prop.get("type") == "array":
            items = prop.get("items", {})
            field_info["item_type"] = items.get("type")
            field_info["item_enum"] = items.get("enum")
        fields[name] = field_info
    return fields


def extract_ontology_fields(ontology: dict) -> dict:
    fields = {}
    for field in ontology.get("schema", {}).get("fields", []):
        field_info = {
            "type": field.get("type", "unknown"),
            "required": field.get("required", False),
            "description": field.get("description", ""),
            "enum_values": field.get("enum_values"),
        }
        if "array" in field.get("type", ""):
            field_info["item_type"] = "string"
        fields[field["name"]] = field_info
    return fields


def compare_schemas(entity_name: str) -> dict:
    schema_path = SCHEMAS_DIR / f"{entity_name}.schema.json"
    ontology_path = ONTOLOGY_DIR / f"{entity_name}.yml"
    
    result = {
        "entity": entity_name,
        "schema_exists": schema_path.exists(),
        "ontology_exists": ontology_path.exists(),
        "schema_valid": False,
        "ontology_valid": False,
        "field_mismatches": [],
        "missing_in_schema": [],
        "missing_in_ontology": [],
        "enum_mismatches": [],
        "type_mismatches": [],
        "completeness_score": 0.0,
    }
    
    schema, schema_errors = load_json(schema_path)
    if schema_errors:
        result["errors"] = schema_errors
        return result
    
    result["schema_valid"] = True
    ontology, ontology_errors = load_yaml(ontology_path)
    if ontology_errors:
        result["errors"] = ontology_errors
        return result

    result["ontology_valid"] = True

    if schema is None or ontology is None:
        result["errors"] = ["Failed to load schema or ontology"]
        return result

    schema_fields = extract_schema_fields(schema)
    ontology_fields = extract_ontology_fields(ontology)
    
    schema_field_names = set(schema_fields.keys())
    ontology_field_names = set(ontology_fields.keys())
    
    common_fields = schema_field_names & ontology_field_names
    
    for field in ontology_field_names - schema_field_names:
        result["missing_in_schema"].append({
            "field": field,
            "ontology_type": ontology_fields[field]["type"],
            "required": ontology_fields[field]["required"],
        })
    
    for field in schema_field_names - ontology_field_names:
        result["missing_in_ontology"].append({
            "field": field,
            "schema_type": schema_fields[field]["type"],
            "required": schema_fields[field]["required"],
        })
    
    for field in common_fields:
        sf = schema_fields[field]
        of = ontology_fields[field]
        
        schema_type = sf["type"]
        ontology_type = of["type"]
        
        type_map = {
            "string": "string",
            "integer": "integer",
            "number": "integer",
            "boolean": "boolean",
            "array": "array[string]",
            "object": "object",
        }
        
        normalized_schema_type = type_map.get(schema_type, schema_type)
        
        if "enum" in ontology_type:
            schema_enum = sf.get("enum") or sf.get("item_enum")
            ontology_enum = of.get("enum_values")
            
            if schema_enum and ontology_enum:
                schema_set = set(schema_enum)
                ontology_set = set(ontology_enum)
                
                if schema_set != ontology_set:
                    result["enum_mismatches"].append({
                        "field": field,
                        "schema_values": sorted(schema_set),
                        "ontology_values": sorted(ontology_set),
                        "in_schema_only": sorted(schema_set - ontology_set),
                        "in_ontology_only": sorted(ontology_set - schema_set),
                    })
        
        if normalized_schema_type != ontology_type and not (
            "array" in ontology_type and schema_type == "array"
        ):
            if not (schema_type == "string" and ontology_type.startswith("array")):
                result["type_mismatches"].append({
                    "field": field,
                    "schema_type": schema_type,
                    "ontology_type": ontology_type,
                })
    
    total_fields = len(ontology_field_names)
    matched_fields = len(common_fields) - len(result["type_mismatches"]) - len(result["enum_mismatches"])
    
    if total_fields > 0:
        result["completeness_score"] = (matched_fields / total_fields) * 100
    
    result["schema_fields"] = list(schema_field_names)
    result["ontology_fields"] = list(ontology_field_names)
    result["schema_required"] = schema.get("required", [])
    result["ontology_required"] = [
        f["name"] for f in ontology.get("schema", {}).get("fields", [])
        if f.get("required")
    ]
    
    return result


def get_all_entity_names() -> list[str]:
    entities = set()
    
    for schema_file in SCHEMAS_DIR.glob("*.schema.json"):
        entities.add(schema_file.stem)
    
    for ontology_file in ONTOLOGY_DIR.glob("*.yml"):
        entities.add(ontology_file.stem)
    
    return sorted(entities)


def audit_all_entities(entity_filter: str | None = None) -> list[dict]:
    entities = get_all_entity_names()
    
    if entity_filter:
        entities = [e for e in entities if e == entity_filter]
    
    results = []
    for entity in entities:
        result = compare_schemas(entity)
        results.append(result)
    
    return results


def generate_report(results: list[dict], verbose: bool = False) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("SCHEMA AUDIT REPORT")
    lines.append("=" * 70)
    lines.append("")
    
    total = len(results)
    valid = sum(1 for r in results if r.get("schema_valid") and r.get("ontology_valid"))
    complete = sum(1 for r in results if r.get("completeness_score", 0) >= 90)
    
    lines.append(f"Total Entities: {total}")
    lines.append(f"Valid (both schema & ontology): {valid}")
    lines.append(f"High Completeness (>=90%): {complete}")
    lines.append("")
    
    by_score = sorted(results, key=lambda r: r.get("completeness_score", 0))
    
    lines.append("-" * 70)
    lines.append("ENTITIES BY COMPLETENESS SCORE")
    lines.append("-" * 70)
    
    for r in by_score:
        score = r.get("completeness_score", 0)
        entity = r.get("entity", "unknown")
        status = "[OK]" if score >= 90 else "[!!]"
        lines.append(f"  {status} {entity:30} {score:6.1f}%")
    
    lines.append("")
    
    issues_found = False
    
    enum_issues = [r for r in results if r.get("enum_mismatches")]
    if enum_issues:
        issues_found = True
        lines.append("-" * 70)
        lines.append("ENUM MISMATCHES (schema vs ontology)")
        lines.append("-" * 70)
        
        for r in enum_issues:
            entity = r.get("entity")
            for mismatch in r.get("enum_mismatches", []):
                field = mismatch["field"]
                lines.append(f"\n  {entity}.{field}:")
                lines.append(f"    Schema:   {mismatch['schema_values']}")
                lines.append(f"    Ontology: {mismatch['ontology_values']}")
                if mismatch["in_schema_only"]:
                    lines.append(f"    Only in schema: {mismatch['in_schema_only']}")
                if mismatch["in_ontology_only"]:
                    lines.append(f"    Only in ontology: {mismatch['in_ontology_only']}")
    
    type_issues = [r for r in results if r.get("type_mismatches")]
    if type_issues:
        issues_found = True
        lines.append("")
        lines.append("-" * 70)
        lines.append("TYPE MISMATCHES")
        lines.append("-" * 70)
        
        for r in type_issues:
            entity = r.get("entity")
            for mismatch in r.get("type_mismatches", []):
                field = mismatch["field"]
                lines.append(
                    f"  {entity}.{field}: schema={mismatch['schema_type']} vs ontology={mismatch['ontology_type']}"
                )
    
    missing_in_schema = [r for r in results if r.get("missing_in_schema")]
    if missing_in_schema:
        issues_found = True
        lines.append("")
        lines.append("-" * 70)
        lines.append("FIELDS MISSING IN SCHEMA (present in ontology)")
        lines.append("-" * 70)
        
        for r in missing_in_schema:
            entity = r.get("entity")
            for field in r.get("missing_in_schema", []):
                req = " [required]" if field["required"] else ""
                lines.append(f"  {entity}.{field['field']}: {field['ontology_type']}{req}")
    
    missing_in_ontology = [r for r in results if r.get("missing_in_ontology")]
    if missing_in_ontology:
        issues_found = True
        lines.append("")
        lines.append("-" * 70)
        lines.append("FIELDS MISSING IN ONTOLOGY (present in schema)")
        lines.append("-" * 70)
        
        for r in missing_in_ontology:
            entity = r.get("entity")
            for field in r.get("missing_in_ontology", []):
                req = " [required]" if field["required"] else ""
                lines.append(f"  {entity}.{field['field']}: {field['schema_type']}{req}")
    
    if not issues_found:
        lines.append("")
        lines.append("[OK] No mismatches found!")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def fix_enum_mismatches(results: list[dict], dry_run: bool = True) -> list[str]:
    fixed = []
    
    for r in results:
        if not r.get("enum_mismatches"):
            continue
        
        entity = r.get("entity")
        schema_path = SCHEMAS_DIR / f"{entity}.schema.json"
        
        schema, _ = load_json(schema_path)
        if not schema:
            continue
        
        for mismatch in r.get("enum_mismatches", []):
            field = mismatch["field"]
            ontology_values = mismatch["ontology_values"]
            
            if field in schema.get("properties", {}):
                old_values = schema["properties"][field].get("enum", [])
                schema["properties"][field]["enum"] = ontology_values
                
                action = "Would update" if dry_run else "Updated"
                fixed.append(
                    f"{action} {entity}.{field}: {old_values} -> {ontology_values}"
                )
        
        if not dry_run:
            schema_path.write_text(
                json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8"
            )
    
    return fixed


def main():
    parser = argparse.ArgumentParser(
        description="Validate and audit entity schemas against ontology definitions"
    )
    parser.add_argument(
        "--entity", "-e",
        help="Audit specific entity only"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix enum mismatches (use ontology as source of truth)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    results = audit_all_entities(args.entity)
    
    if args.json:
        print(json.dumps(results, indent=2))
        return
    
    report = generate_report(results, args.verbose)
    print(report)
    
    if args.fix or args.dry_run:
        print("\n" + "=" * 70)
        print("FIXING ENUM MISMATCHES" + (" (DRY RUN)" if args.dry_run else ""))
        print("=" * 70)
        
        fixed = fix_enum_mismatches(results, dry_run=args.dry_run)
        if fixed:
            for f in fixed:
                print(f"  {f}")
        else:
            print("  No enum mismatches to fix")
    
    issues_count = sum(
        1 for r in results
        if r.get("enum_mismatches") or r.get("type_mismatches")
        or r.get("missing_in_schema") or r.get("missing_in_ontology")
    )
    
    if issues_count > 0:
        print(f"\nFound issues in {issues_count} entities")
        sys.exit(1)
    else:
        print("\n[OK] All schemas validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
