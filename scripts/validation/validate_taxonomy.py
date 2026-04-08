#!/usr/bin/env python3
"""
Taxonomy Validation Script for changemappers.org

Validates taxonomy references in entity data:
- Checks that all taxonomy codes exist in ontology definitions
- Verifies domain/scale/function references are valid
- Reports any invalid taxonomy references

Usage:
    python validate_taxonomy.py [OPTIONS]

Options:
    --verbose    Enable verbose output
    --help       Show this help message
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

BRAND = "changemappers.org"
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ENTITIES_DIR = DATA_DIR / "entities"
ONTOLOGY_DIR = PROJECT_ROOT / "ontology"

TAXONOMY_FIELDS = {
    "domain", "scale", "function", "sector", "phase",
    "topic", "subdomain", "transition", "impact_type",
    "outcome_type", "actor_type", "location_type"
}


def load_json(file_path: Path) -> Tuple[Any, List[str]]:
    """Load JSON file and return data with any errors."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data, errors
    except json.JSONDecodeError as e:
        errors.append(f"{file_path}:{e.lineno}:{e.colno} - JSON parse error: {e.msg}")
        return None, errors
    except FileNotFoundError:
        errors.append(f"{file_path} - File not found")
        return None, errors
    except Exception as e:
        errors.append(f"{file_path} - Error loading file: {str(e)}")
        return None, errors


def load_taxonomy_definitions(ontology_dir: Path, verbose: bool = False) -> Tuple[Dict[str, Set[str]], List[str]]:
    """Load all taxonomy definitions from ontology directory."""
    taxonomies = defaultdict(set)
    errors = []
    
    if not ontology_dir.exists():
        errors.append(f"Ontology directory not found: {ontology_dir}")
        return dict(taxonomies), errors
    
    taxonomy_files = list(ontology_dir.glob("**/*.json"))
    
    if not taxonomy_files:
        if verbose:
            print(f"No taxonomy files found in {ontology_dir}")
        
        taxonomy_data = {
            "domain": {"environmental", "social", "economic", "political", "cultural"},
            "scale": {"individual", "community", "regional", "national", "global"},
            "function": {"advocacy", "research", "implementation", "coordination", "education"},
            "sector": {"health", "education", "environment", "economy", "governance"},
            "phase": {"planning", "implementation", "evaluation", "sustainability"},
            "topic": {"climate", "justice", "rights", "sustainability"},
        }
        
        for tax_type, values in taxonomy_data.items():
            taxonomies[tax_type] = values
        
        return dict(taxonomies), errors
    
    for tax_file in taxonomy_files:
        data, load_errors = load_json(tax_file)
        if load_errors:
            errors.extend(load_errors)
            continue
        
        if data is None:
            continue
        
        tax_type = tax_file.stem
        
        if isinstance(data, dict):
            if "values" in data:
                values = data["values"]
                if isinstance(values, list):
                    for v in values:
                        if isinstance(v, dict) and "id" in v:
                            taxonomies[tax_type].add(v["id"])
                        elif isinstance(v, str):
                            taxonomies[tax_type].add(v)
            elif "records" in data:
                records = data["records"]
                if isinstance(records, list):
                    for r in records:
                        if isinstance(r, dict):
                            if "id" in r:
                                taxonomies[tax_type].add(r["id"])
                            elif "slug" in r:
                                taxonomies[tax_type].add(r["slug"])
                            elif "code" in r:
                                taxonomies[tax_type].add(r["code"])
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key in ["id", "slug", "code", "name"]:
                        if key in item:
                            taxonomies[tax_type].add(item[key])
                            break
                elif isinstance(item, str):
                    taxonomies[tax_type].add(item)
        
        if verbose:
            print(f"Loaded taxonomy '{tax_type}' with {len(taxonomies[tax_type])} values")
    
    return dict(taxonomies), errors


def validate_taxonomy_field(
    field_name: str, 
    field_value: Any, 
    valid_taxonomies: Dict[str, Set[str]],
    entity_file: Path,
    record_index: int
) -> List[str]:
    """Validate a taxonomy field value."""
    errors = []
    
    if field_name not in TAXONOMY_FIELDS:
        return errors
    
    valid_values = valid_taxonomies.get(field_name, set())
    
    if isinstance(field_value, str):
        if valid_values and field_value not in valid_values:
            errors.append(
                f"{entity_file.name}:record[{record_index}].{field_name} - "
                f"Invalid taxonomy value '{field_value}' (valid: {sorted(valid_values)[:5]}...)"
            )
    elif isinstance(field_value, list):
        for i, item in enumerate(field_value):
            if isinstance(item, str) and valid_values and item not in valid_values:
                errors.append(
                    f"{entity_file.name}:record[{record_index}].{field_name}[{i}] - "
                    f"Invalid taxonomy value '{item}'"
                )
    
    return errors


def validate_entity_taxonomy(
    entity_file: Path, 
    valid_taxonomies: Dict[str, Set[str]], 
    verbose: bool = False
) -> Tuple[int, List[str]]:
    """Validate taxonomy references in an entity file."""
    errors = []
    checked_count = 0
    
    data, load_errors = load_json(entity_file)
    if load_errors:
        errors.extend(load_errors)
        return checked_count, errors
    
    if data is None:
        return checked_count, errors
    
    records = data.get("records", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        records = [records]
    
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        
        for field_name, field_value in record.items():
            if field_name in TAXONOMY_FIELDS:
                field_errors = validate_taxonomy_field(
                    field_name, field_value, valid_taxonomies, entity_file, i
                )
                errors.extend(field_errors)
                checked_count += 1
        
        nested_objects = ["properties", "metadata", "taxonomy", "classification"]
        for nested_key in nested_objects:
            if nested_key in record and isinstance(record[nested_key], dict):
                for field_name, field_value in record[nested_key].items():
                    if field_name in TAXONOMY_FIELDS:
                        field_errors = validate_taxonomy_field(
                            field_name, field_value, valid_taxonomies, entity_file, i
                        )
                        errors.extend(field_errors)
                        checked_count += 1
    
    return checked_count, errors


def main():
    parser = argparse.ArgumentParser(
        description=f"Validate taxonomy references - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    python {Path(__file__).name} --verbose
    python {Path(__file__).name}

{BRAND} - Taxonomy Validation Tool
"""
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    print(f"=== {BRAND} Taxonomy Validation ===")
    print()
    
    all_errors = []
    total_checked = 0
    
    print("Loading taxonomy definitions...")
    valid_taxonomies, errors = load_taxonomy_definitions(ONTOLOGY_DIR, args.verbose)
    all_errors.extend(errors)
    
    taxonomy_types = list(valid_taxonomies.keys())
    if taxonomy_types:
        print(f"Loaded {len(taxonomy_types)} taxonomy types")
        for tax_type, values in valid_taxonomies.items():
            print(f"  {tax_type}: {len(values)} valid values")
    else:
        print("No taxonomy definitions found - will validate structure only")
    print()
    
    if not ENTITIES_DIR.exists():
        print(f"Error: Entities directory not found: {ENTITIES_DIR}")
        sys.exit(1)
    
    print("Validating entity taxonomy references...")
    entity_files = sorted(ENTITIES_DIR.glob("*.json"))
    
    for entity_file in entity_files:
        if args.verbose:
            print(f"Processing: {entity_file.name}")
        
        checked, errors = validate_entity_taxonomy(entity_file, valid_taxonomies, args.verbose)
        total_checked += checked
        all_errors.extend(errors)
        
        if errors:
            print(f"  {entity_file.name}: {len(errors)} invalid references")
        elif checked > 0:
            print(f"  {entity_file.name}: {checked} references OK")
    
    print()
    print(f"=== Validation Summary ===")
    print(f"Taxonomy types: {len(valid_taxonomies)}")
    print(f"References checked: {total_checked}")
    print(f"Invalid references: {len(all_errors)}")
    
    if all_errors:
        print()
        print("=== Issues ===")
        for error in all_errors:
            print(f"  {error}")
        print()
        print(f"{BRAND} Taxonomy Validation: FAILED")
        sys.exit(1)
    else:
        print()
        print(f"{BRAND} Taxonomy Validation: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
