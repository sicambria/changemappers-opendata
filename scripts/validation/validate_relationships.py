#!/usr/bin/env python3
"""
Relationship Integrity Validation Script for changemappers.org

Validates relationship integrity by checking:
- All source_id and target_id references exist
- Relationship types match ontology definitions
- No orphaned relationships exist

Usage:
    python validate_relationships.py [OPTIONS]

Options:
    --verbose    Enable verbose output
    --output     Output file for integrity report
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
RELATIONSHIPS_DIR = DATA_DIR / "relationships"

VALID_RELATIONSHIP_TYPES = {
    "supports", "contradicts", "follows", "precedes", 
    "collaborates_with", "funds", "enables", "measures",
    "transforms_to", "derives_from", "relates_to", "part_of",
    "occurs_at", "located_in", "uses", "produces", 
    "requires", "addresses", "implements", "initiates"
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


def collect_all_entity_ids(entities_dir: Path, verbose: bool = False) -> Tuple[Set[str], List[str]]:
    """Collect all entity IDs from data files."""
    all_ids = set()
    entity_type_map = {}
    errors = []
    
    if not entities_dir.exists():
        errors.append(f"Entities directory not found: {entities_dir}")
        return all_ids, errors
    
    for entity_file in entities_dir.glob("*.json"):
        data, load_errors = load_json(entity_file)
        if load_errors:
            errors.extend(load_errors)
            continue
        
        if data is None:
            continue
        
        records = data.get("records", data) if isinstance(data, dict) else data
        if isinstance(records, list):
            for record in records:
                if isinstance(record, dict) and "id" in record:
                    entity_id = record["id"]
                    all_ids.add(entity_id)
                    entity_type_map[entity_id] = entity_file.stem
                    if verbose:
                        print(f"  Found entity: {entity_id} ({entity_file.stem})")
    
    if verbose:
        print(f"Collected {len(all_ids)} unique entity IDs")
    
    return all_ids, errors


def validate_relationship_file(
    rel_file: Path, 
    known_ids: Set[str], 
    verbose: bool = False
) -> Tuple[List[Dict], List[str]]:
    """Validate a relationship file."""
    errors = []
    valid_relationships = []
    
    data, load_errors = load_json(rel_file)
    if load_errors:
        errors.extend(load_errors)
        return valid_relationships, errors
    
    if data is None:
        return valid_relationships, errors
    
    rel_type = data.get("relationship_type", rel_file.stem)
    
    if rel_type not in VALID_RELATIONSHIP_TYPES:
        errors.append(f"{rel_file} - Unknown relationship type: {rel_type}")
    
    records = data.get("records", [])
    
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{rel_file}:{i} - Invalid record format")
            continue
        
        source_id = record.get("source_id")
        target_id = record.get("target_id")
        
        if not source_id:
            errors.append(f"{rel_file}:{i} - Missing source_id")
            continue
        
        if not target_id:
            errors.append(f"{rel_file}:{i} - Missing target_id")
            continue
        
        source_exists = source_id in known_ids
        target_exists = target_id in known_ids
        
        if not source_exists:
            errors.append(f"{rel_file}:{i} - source_id '{source_id}' not found in entities")
        
        if not target_exists:
            errors.append(f"{rel_file}:{i} - target_id '{target_id}' not found in entities")
        
        if source_exists and target_exists:
            valid_relationships.append(record)
            if verbose:
                print(f"  Valid: {source_id} -> {target_id} ({rel_type})")
    
    return valid_relationships, errors


def check_orphaned_relationships(
    relationships: List[Dict], 
    known_ids: Set[str]
) -> List[str]:
    """Check for orphaned relationships."""
    orphans = []
    
    referenced_ids = set()
    for rel in relationships:
        referenced_ids.add(rel.get("source_id"))
        referenced_ids.add(rel.get("target_id"))
    
    orphan_ids = referenced_ids - known_ids
    
    for orphan_id in orphan_ids:
        orphans.append(f"Orphaned ID: {orphan_id}")
    
    return orphans


def generate_integrity_report(
    total_entities: int,
    total_relationships: int,
    valid_relationships: int,
    invalid_relationships: int,
    relationship_types: Dict[str, int],
    errors: List[str]
) -> str:
    """Generate relationship integrity report."""
    report = []
    report.append(f"# Relationship Integrity Report")
    report.append(f"")
    report.append(f"**Generated by {BRAND}**")
    report.append(f"")
    report.append(f"## Summary")
    report.append(f"")
    report.append(f"| Metric | Count |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Entities | {total_entities} |")
    report.append(f"| Total Relationships | {total_relationships} |")
    report.append(f"| Valid Relationships | {valid_relationships} |")
    report.append(f"| Invalid Relationships | {invalid_relationships} |")
    report.append(f"")
    report.append(f"## Relationship Types")
    report.append(f"")
    report.append(f"| Type | Count |")
    report.append(f"|------|-------|")
    for rel_type, count in sorted(relationship_types.items()):
        report.append(f"| {rel_type} | {count} |")
    report.append(f"")
    
    if errors:
        report.append(f"## Issues ({len(errors)})")
        report.append(f"")
        for error in errors:
            report.append(f"- {error}")
        report.append(f"")
    
    report.append(f"---")
    report.append(f"*{BRAND} - Relationship Integrity Validation*")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description=f"Validate relationship integrity - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    python {Path(__file__).name} --verbose
    python {Path(__file__).name} --output report.md

{BRAND} - Relationship Integrity Validation Tool
"""
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", type=str, help="Output file for integrity report")
    
    args = parser.parse_args()
    
    print(f"=== {BRAND} Relationship Integrity Validation ===")
    print()
    
    all_errors = []
    all_relationships = []
    relationship_type_counts = defaultdict(int)
    
    print("Collecting entity IDs...")
    known_ids, errors = collect_all_entity_ids(ENTITIES_DIR, args.verbose)
    all_errors.extend(errors)
    
    if not known_ids:
        print(f"Error: No entities found in {ENTITIES_DIR}")
        sys.exit(1)
    
    print(f"Found {len(known_ids)} entities")
    print()
    
    if not RELATIONSHIPS_DIR.exists():
        print(f"Error: Relationships directory not found: {RELATIONSHIPS_DIR}")
        sys.exit(1)
    
    print("Validating relationships...")
    rel_files = sorted(RELATIONSHIPS_DIR.glob("*.json"))
    
    for rel_file in rel_files:
        if args.verbose:
            print(f"Processing: {rel_file.name}")
        
        valid_rels, errors = validate_relationship_file(rel_file, known_ids, args.verbose)
        all_errors.extend(errors)
        all_relationships.extend(valid_rels)
        
        rel_type = rel_file.stem
        relationship_type_counts[rel_type] = len(valid_rels)
        
        if valid_rels:
            print(f"  {rel_file.name}: {len(valid_rels)} valid relationships")
    
    print()
    
    orphan_errors = check_orphaned_relationships(all_relationships, known_ids)
    all_errors.extend(orphan_errors)
    
    total_relationships = len(all_relationships) + len(all_errors)
    valid_count = len(all_relationships)
    invalid_count = len(all_errors)
    
    report = generate_integrity_report(
        total_entities=len(known_ids),
        total_relationships=total_relationships,
        valid_relationships=valid_count,
        invalid_relationships=invalid_count,
        relationship_types=dict(relationship_type_counts),
        errors=all_errors
    )
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    print()
    print(f"=== Validation Summary ===")
    print(f"Entities: {len(known_ids)}")
    print(f"Valid relationships: {valid_count}")
    print(f"Invalid relationships: {invalid_count}")
    
    if all_errors:
        print()
        print(f"{BRAND} Relationship Validation: FAILED")
        sys.exit(1)
    else:
        print()
        print(f"{BRAND} Relationship Validation: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
