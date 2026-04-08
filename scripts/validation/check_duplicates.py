#!/usr/bin/env python3
"""
Duplicate Detection Script for changemappers.org

Checks for duplicate records:
- Detects duplicate slugs across all entities
- Detects duplicate names/titles
- Reports potential duplicates for manual review

Usage:
    python check_duplicates.py [OPTIONS]

Options:
    --verbose    Enable verbose output
    --output     Output file for duplicate report
    --help       Show this help message
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

BRAND = "changemappers.org"
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ENTITIES_DIR = DATA_DIR / "entities"


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


def normalize_string(s: str) -> str:
    """Normalize string for comparison."""
    if not s:
        return ""
    return " ".join(s.lower().split())


def extract_entity_names(records: List[Dict], entity_type: str) -> Dict[str, List[Tuple[str, str, str]]]:
    """Extract names and slugs from entity records."""
    name_map = defaultdict(list)
    
    for record in records:
        if not isinstance(record, dict):
            continue
        
        entity_id = record.get("id", "unknown")
        
        if "slug" in record:
            slug = record["slug"]
            name_map[f"slug:{slug}"].append((entity_type, entity_id, slug))
        
        name_fields = ["name", "title", "label"]
        for field in name_fields:
            if field in record and record[field]:
                name = record[field]
                normalized = normalize_string(name)
                name_map[f"name:{normalized}"].append((entity_type, entity_id, name))
        
        if "properties" in record and isinstance(record["properties"], dict):
            for field in ["name", "title", "label"]:
                if field in record["properties"] and record["properties"][field]:
                    name = record["properties"][field]
                    normalized = normalize_string(name)
                    name_map[f"name:{normalized}"].append((entity_type, entity_id, name))
    
    return name_map


def find_duplicates(entities_dir: Path, verbose: bool = False) -> Tuple[Dict[str, List], List[str]]:
    """Find duplicate slugs and names across all entities."""
    all_names = defaultdict(list)
    errors = []
    
    if not entities_dir.exists():
        errors.append(f"Entities directory not found: {entities_dir}")
        return dict(all_names), errors
    
    for entity_file in sorted(entities_dir.glob("*.json")):
        entity_type = entity_file.stem
        
        if verbose:
            print(f"Processing: {entity_file.name}")
        
        data, load_errors = load_json(entity_file)
        if load_errors:
            errors.extend(load_errors)
            continue
        
        if data is None:
            continue
        
        records = data.get("records", data) if isinstance(data, dict) else data
        if not isinstance(records, list):
            records = [records]
        
        entity_names = extract_entity_names(records, entity_type)
        
        for key, occurrences in entity_names.items():
            all_names[key].extend(occurrences)
    
    duplicates = {}
    for key, occurrences in all_names.items():
        if len(occurrences) > 1:
            duplicates[key] = occurrences
    
    return duplicates, errors


def calculate_similarity(s1: str, s2: str) -> float:
    """Calculate simple similarity ratio between two strings."""
    if not s1 or not s2:
        return 0.0
    
    s1 = normalize_string(s1)
    s2 = normalize_string(s2)
    
    if s1 == s2:
        return 1.0
    
    words1 = set(s1.split())
    words2 = set(s2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def find_similar_entities(entities_dir: Path, threshold: float = 0.8, verbose: bool = False) -> List[Dict]:
    """Find entities with similar names (potential duplicates)."""
    similar_pairs = []
    all_entities = []
    
    for entity_file in sorted(entities_dir.glob("*.json")):
        entity_type = entity_file.stem
        
        data, _ = load_json(entity_file)
        if data is None:
            continue
        
        records = data.get("records", data) if isinstance(data, dict) else data
        if not isinstance(records, list):
            records = [records]
        
        for record in records:
            if not isinstance(record, dict):
                continue
            
            entity_id = record.get("id", "unknown")
            name = record.get("name") or record.get("title") or record.get("label", "")
            
            if name:
                all_entities.append({
                    "type": entity_type,
                    "id": entity_id,
                    "name": name
                })
    
    for i, entity1 in enumerate(all_entities):
        for entity2 in all_entities[i+1:]:
            if entity1["type"] != entity2["type"]:
                continue
            
            similarity = calculate_similarity(entity1["name"], entity2["name"])
            
            if similarity >= threshold and similarity < 1.0:
                similar_pairs.append({
                    "entity1": entity1,
                    "entity2": entity2,
                    "similarity": round(similarity, 2)
                })
                
                if verbose:
                    print(f"  Similar: {entity1['name']} <-> {entity2['name']} ({similarity:.2f})")
    
    return similar_pairs


def generate_duplicate_report(
    duplicates: Dict[str, List],
    similar_pairs: List[Dict],
    total_entities: int
) -> str:
    """Generate duplicate report."""
    report = []
    report.append(f"# Duplicate Detection Report")
    report.append(f"")
    report.append(f"**Generated by {BRAND}**")
    report.append(f"")
    report.append(f"## Summary")
    report.append(f"")
    report.append(f"| Metric | Count |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Entities | {total_entities} |")
    report.append(f"| Exact Duplicates | {len(duplicates)} |")
    report.append(f"| Similar Pairs | {len(similar_pairs)} |")
    report.append(f"")
    
    if duplicates:
        report.append(f"## Exact Duplicates ({len(duplicates)})")
        report.append(f"")
        for key, occurrences in sorted(duplicates.items()):
            key_type, key_value = key.split(":", 1)
            report.append(f"### {key_type}: `{key_value}`")
            report.append(f"")
            for entity_type, entity_id, name in occurrences:
                report.append(f"- {entity_type}/{entity_id}: {name}")
            report.append(f"")
    
    if similar_pairs:
        report.append(f"## Similar Entities ({len(similar_pairs)})")
        report.append(f"")
        report.append(f"| Type | Entity 1 | Entity 2 | Similarity |")
        report.append(f"|------|----------|----------|------------|")
        for pair in sorted(similar_pairs, key=lambda x: x["similarity"], reverse=True):
            report.append(
                f"| {pair['entity1']['type']} | "
                f"{pair['entity1']['name']} | "
                f"{pair['entity2']['name']} | "
                f"{pair['similarity']:.0%} |"
            )
        report.append(f"")
    
    if not duplicates and not similar_pairs:
        report.append(f"## Result")
        report.append(f"")
        report.append(f"No duplicates detected.")
        report.append(f"")
    
    report.append(f"---")
    report.append(f"*{BRAND} - Duplicate Detection Tool*")
    
    return "\n".join(report)


def count_entities(entities_dir: Path) -> int:
    """Count total number of entities."""
    count = 0
    for entity_file in entities_dir.glob("*.json"):
        data, _ = load_json(entity_file)
        if data is None:
            continue
        records = data.get("records", data) if isinstance(data, dict) else data
        if isinstance(records, list):
            count += len(records)
    return count


def main():
    parser = argparse.ArgumentParser(
        description=f"Check for duplicate records - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    python {Path(__file__).name} --verbose
    python {Path(__file__).name} --output duplicates.md

{BRAND} - Duplicate Detection Tool
"""
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", type=str, help="Output file for duplicate report")
    
    args = parser.parse_args()
    
    print(f"=== {BRAND} Duplicate Detection ===")
    print()
    
    total_entities = count_entities(ENTITIES_DIR)
    
    print("Scanning for exact duplicates...")
    duplicates, errors = find_duplicates(ENTITIES_DIR, args.verbose)
    
    if errors:
        for error in errors:
            print(f"  Error: {error}")
    
    print(f"Found {len(duplicates)} exact duplicate groups")
    print()
    
    print("Scanning for similar entities...")
    similar_pairs = find_similar_entities(ENTITIES_DIR, threshold=0.8, verbose=args.verbose)
    print(f"Found {len(similar_pairs)} similar entity pairs")
    print()
    
    report = generate_duplicate_report(duplicates, similar_pairs, total_entities)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    print()
    
    duplicate_count = sum(len(occ) for occ in duplicates.values())
    if duplicates or similar_pairs:
        print(f"{BRAND} Duplicate Detection: ISSUES FOUND")
        print(f"  - {duplicate_count} exact duplicate occurrences")
        print(f"  - {len(similar_pairs)} potential similar pairs")
        sys.exit(1)
    else:
        print(f"{BRAND} Duplicate Detection: NO ISSUES FOUND")
        sys.exit(0)


if __name__ == "__main__":
    main()
