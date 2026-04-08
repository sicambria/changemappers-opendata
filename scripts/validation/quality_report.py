#!/usr/bin/env python3
"""
Data Quality Report Generator for changemappers.org

Generates comprehensive data quality report:
- Calculates completeness metrics per entity type
- Checks for missing required fields
- Generates markdown quality report
- Includes statistics: record counts, field coverage, relationship counts

Usage:
    python quality_report.py [OPTIONS]

Options:
    --verbose    Enable verbose output
    --output     Output file for quality report
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
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "entities"


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


def get_required_fields(schema_path: Path) -> Set[str]:
    """Extract required fields from schema."""
    if not schema_path.exists():
        return set()
    
    data, _ = load_json(schema_path)
    if data is None:
        return set()
    
    return set(data.get("required", []))


def analyze_entity_file(
    entity_file: Path, 
    required_fields: Set[str],
    verbose: bool = False
) -> Dict:
    """Analyze an entity file for completeness metrics."""
    result = {
        "file": entity_file.name,
        "entity_type": entity_file.stem,
        "record_count": 0,
        "field_coverage": {},
        "missing_required": defaultdict(int),
        "empty_fields": defaultdict(int),
        "field_presence": defaultdict(int)
    }
    
    data, errors = load_json(entity_file)
    if errors and verbose:
        for error in errors:
            print(f"  Error: {error}")
    
    if data is None:
        return result
    
    records = data.get("records", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        records = [records]
    
    result["record_count"] = len(records)
    
    if result["record_count"] == 0:
        return result
    
    for record in records:
        if not isinstance(record, dict):
            continue
        
        for field in required_fields:
            if field not in record or record[field] is None or record[field] == "":
                result["missing_required"][field] += 1
        
        for field, value in record.items():
            result["field_presence"][field] += 1
            
            if value is None or value == "" or value == []:
                result["empty_fields"][field] += 1
    
    for field, count in result["field_presence"].items():
        result["field_coverage"][field] = round((count / result["record_count"]) * 100, 1)
    
    result["missing_required"] = dict(result["missing_required"])
    result["empty_fields"] = dict(result["empty_fields"])
    result["field_presence"] = dict(result["field_presence"])
    
    return result


def count_relationships(relationships_dir: Path) -> Dict[str, int]:
    """Count relationships by type."""
    relationship_counts = {}
    
    if not relationships_dir.exists():
        return relationship_counts
    
    for rel_file in relationships_dir.glob("*.json"):
        data, _ = load_json(rel_file)
        if data is None:
            continue
        
        records = data.get("records", data) if isinstance(data, dict) else data
        if isinstance(records, list):
            rel_type = data.get("relationship_type", rel_file.stem)
            relationship_counts[rel_type] = len(records)
    
    return relationship_counts


def calculate_overall_completeness(analysis_results: List[Dict]) -> float:
    """Calculate overall data completeness percentage."""
    total_fields = 0
    filled_fields = 0
    
    for result in analysis_results:
        for field, coverage in result.get("field_coverage", {}).items():
            total_fields += result["record_count"]
            filled_fields += int(coverage / 100 * result["record_count"])
    
    return round((filled_fields / total_fields * 100), 1) if total_fields > 0 else 0


def generate_quality_report(
    entity_analyses: List[Dict],
    relationship_counts: Dict[str, int],
    verbose: bool = False
) -> str:
    """Generate comprehensive data quality report."""
    report = []
    report.append(f"# Data Quality Report")
    report.append(f"")
    report.append(f"**Generated by {BRAND}**")
    report.append(f"")
    
    total_records = sum(a["record_count"] for a in entity_analyses)
    total_relationships = sum(relationship_counts.values())
    overall_completeness = calculate_overall_completeness(entity_analyses)
    
    report.append(f"## Overview")
    report.append(f"")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Entity Records | {total_records} |")
    report.append(f"| Total Relationships | {total_relationships} |")
    report.append(f"| Entity Types | {len(entity_analyses)} |")
    report.append(f"| Relationship Types | {len(relationship_counts)} |")
    report.append(f"| Overall Completeness | {overall_completeness}% |")
    report.append(f"")
    
    report.append(f"## Entity Statistics")
    report.append(f"")
    report.append(f"| Entity Type | Records | Fields | Avg Coverage |")
    report.append(f"|-------------|---------|--------|--------------|")
    
    for analysis in sorted(entity_analyses, key=lambda x: x["record_count"], reverse=True):
        entity_type = analysis["entity_type"]
        record_count = analysis["record_count"]
        field_count = len(analysis.get("field_coverage", {}))
        
        if analysis.get("field_coverage"):
            avg_coverage = sum(analysis["field_coverage"].values()) / len(analysis["field_coverage"])
        else:
            avg_coverage = 0
        
        report.append(f"| {entity_type} | {record_count} | {field_count} | {avg_coverage:.1f}% |")
    
    report.append(f"")
    
    report.append(f"## Relationship Statistics")
    report.append(f"")
    report.append(f"| Relationship Type | Count |")
    report.append(f"|-------------------|-------|")
    for rel_type, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True):
        report.append(f"| {rel_type} | {count} |")
    report.append(f"")
    
    report.append(f"## Field Coverage Details")
    report.append(f"")
    
    for analysis in sorted(entity_analyses, key=lambda x: x["entity_type"]):
        entity_type = analysis["entity_type"]
        report.append(f"### {entity_type}")
        report.append(f"")
        
        if analysis.get("field_coverage"):
            report.append(f"| Field | Coverage | Empty |")
            report.append(f"|-------|----------|-------|")
            for field, coverage in sorted(analysis["field_coverage"].items(), key=lambda x: x[1], reverse=True):
                empty_count = analysis.get("empty_fields", {}).get(field, 0)
                report.append(f"| {field} | {coverage}% | {empty_count} |")
            report.append(f"")
        
        if analysis.get("missing_required"):
            report.append(f"**Missing Required Fields:**")
            report.append(f"")
            for field, count in analysis["missing_required"].items():
                report.append(f"- {field}: {count} records")
            report.append(f"")
    
    issues_found = False
    for analysis in entity_analyses:
        if analysis.get("missing_required"):
            issues_found = True
            break
    
    report.append(f"## Quality Assessment")
    report.append(f"")
    
    if issues_found:
        report.append(f"| Issue Type | Status |")
        report.append(f"|------------|--------|")
        for analysis in entity_analyses:
            if analysis.get("missing_required"):
                entity_type = analysis["entity_type"]
                report.append(f"| {entity_type} - Missing required fields | WARNING |")
        report.append(f"")
    else:
        report.append(f"All entities have complete required fields.")
        report.append(f"")
    
    report.append(f"---")
    report.append(f"*{BRAND} - Data Quality Report Generator*")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description=f"Generate data quality report - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    python {Path(__file__).name} --verbose
    python {Path(__file__).name} --output quality_report.md

{BRAND} - Data Quality Report Generator
"""
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", type=str, help="Output file for quality report")
    
    args = parser.parse_args()
    
    print(f"=== {BRAND} Data Quality Report Generator ===")
    print()
    
    all_analyses = []
    all_errors = []
    
    if not ENTITIES_DIR.exists():
        print(f"Error: Entities directory not found: {ENTITIES_DIR}")
        sys.exit(1)
    
    print("Analyzing entity files...")
    entity_files = sorted(ENTITIES_DIR.glob("*.json"))
    
    for entity_file in entity_files:
        entity_type = entity_file.stem
        schema_file = SCHEMAS_DIR / f"{entity_type}.schema.json"
        
        if args.verbose:
            print(f"Processing: {entity_file.name}")
        
        required_fields = get_required_fields(schema_file)
        
        if args.verbose and required_fields:
            print(f"  Required fields: {required_fields}")
        
        analysis = analyze_entity_file(entity_file, required_fields, args.verbose)
        all_analyses.append(analysis)
        
        print(f"  {entity_type}: {analysis['record_count']} records")
    
    print()
    print("Counting relationships...")
    relationship_counts = count_relationships(RELATIONSHIPS_DIR)
    
    for rel_type, count in sorted(relationship_counts.items()):
        print(f"  {rel_type}: {count}")
    
    print()
    
    report = generate_quality_report(all_analyses, relationship_counts, args.verbose)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    print()
    
    issues_found = any(a.get("missing_required") for a in all_analyses)
    
    if issues_found:
        print(f"{BRAND} Quality Report: ISSUES FOUND")
        sys.exit(1)
    else:
        print(f"{BRAND} Quality Report: NO ISSUES FOUND")
        sys.exit(0)


if __name__ == "__main__":
    main()
