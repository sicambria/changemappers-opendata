#!/usr/bin/env python3
"""
Schema Validation Script for changemappers.org

Validates JSON data files against their corresponding JSON Schema definitions.
Reports validation errors with file:line references and exits with error code
if any validation fails.

Usage:
    python validate_schema.py [OPTIONS]

Options:
    --verbose    Enable verbose output
    --help       Show this help message
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

BRAND = "changemappers.org"
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "entities"
DATA_DIR = PROJECT_ROOT / "data" / "entities"


def load_json(file_path: Path, verbose: bool = False) -> Tuple[Any, List[str]]:
    """Load JSON file and return data with any errors."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
            if verbose:
                print(f"Loaded: {file_path}")
            return data, errors
    except json.JSONDecodeError as e:
        line_num = e.lineno if hasattr(e, 'lineno') else 1
        col_num = e.colno if hasattr(e, 'colno') else 1
        errors.append(f"{file_path}:{line_num}:{col_num} - JSON parse error: {e.msg}")
        return None, errors
    except FileNotFoundError:
        errors.append(f"{file_path} - File not found")
        return None, errors
    except Exception as e:
        errors.append(f"{file_path} - Error loading file: {str(e)}")
        return None, errors


def validate_type(value: Any, expected_type: str, path: str) -> List[str]:
    """Validate a value against an expected JSON Schema type."""
    errors = []
    type_mapping = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    
    if expected_type == "null":
        if value is not None:
            errors.append(f"{path} - Expected null, got {type(value).__name__}")
    elif expected_type in type_mapping:
        expected_python_type = type_mapping[expected_type]
        if expected_type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{path} - Expected {expected_type}, got {type(value).__name__}")
        elif not isinstance(value, expected_python_type):
            errors.append(f"{path} - Expected {expected_type}, got {type(value).__name__}")
    
    return errors


def validate_string_constraints(value: str, schema: Dict, path: str) -> List[str]:
    """Validate string against schema constraints."""
    errors = []
    
    if "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(f"{path} - String length {len(value)} is less than minimum {schema['minLength']}")
    
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        errors.append(f"{path} - String length {len(value)} exceeds maximum {schema['maxLength']}")
    
    if "pattern" in schema:
        import re
        if not re.match(schema["pattern"], value):
            errors.append(f"{path} - String '{value}' does not match pattern '{schema['pattern']}'")
    
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} - Value '{value}' not in enum {schema['enum']}")
    
    if "format" in schema:
        format_errors = validate_format(value, schema["format"], path)
        errors.extend(format_errors)
    
    return errors


def validate_format(value: str, format_type: str, path: str) -> List[str]:
    """Validate string format."""
    errors = []
    import re
    
    if format_type == "email":
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            errors.append(f"{path} - Invalid email format: {value}")
    elif format_type == "uri":
        if not re.match(r'^https?://', value):
            errors.append(f"{path} - Invalid URI format: {value}")
    elif format_type == "uuid":
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value.lower()):
            errors.append(f"{path} - Invalid UUID format: {value}")
    elif format_type == "date":
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            errors.append(f"{path} - Invalid date format: {value}")
    elif format_type == "date-time":
        if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
            errors.append(f"{path} - Invalid date-time format: {value}")
    
    return errors


def validate_number_constraints(value: float, schema: Dict, path: str) -> List[str]:
    """Validate number against schema constraints."""
    errors = []
    
    if "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path} - Value {value} is less than minimum {schema['minimum']}")
    
    if "maximum" in schema and value > schema["maximum"]:
        errors.append(f"{path} - Value {value} exceeds maximum {schema['maximum']}")
    
    if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
        errors.append(f"{path} - Value {value} must be greater than {schema['exclusiveMinimum']}")
    
    if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
        errors.append(f"{path} - Value {value} must be less than {schema['exclusiveMaximum']}")
    
    return errors


def validate_object(data: Dict, schema: Dict, path: str, verbose: bool = False) -> List[str]:
    """Validate object against schema."""
    errors = []
    
    if "required" in schema:
        for required_field in schema["required"]:
            if required_field not in data:
                errors.append(f"{path} - Missing required field: {required_field}")
    
    if "additionalProperties" in schema and schema["additionalProperties"] is False:
        allowed_props = set(schema.get("properties", {}).keys())
        for prop in data:
            if prop not in allowed_props:
                errors.append(f"{path}.{prop} - Additional property not allowed")
    
    for key, value in data.items():
        prop_path = f"{path}.{key}" if path else key
        if "properties" in schema and key in schema["properties"]:
            prop_schema = schema["properties"][key]
            errors.extend(validate_value(value, prop_schema, prop_path, verbose))
    
    return errors


def validate_array(data: list, schema: Dict, path: str, verbose: bool = False) -> List[str]:
    """Validate array against schema."""
    errors = []
    
    if "minItems" in schema and len(data) < schema["minItems"]:
        errors.append(f"{path} - Array length {len(data)} is less than minimum {schema['minItems']}")
    
    if "maxItems" in schema and len(data) > schema["maxItems"]:
        errors.append(f"{path} - Array length {len(data)} exceeds maximum {schema['maxItems']}")
    
    if "items" in schema:
        item_schema = schema["items"]
        for i, item in enumerate(data):
            item_path = f"{path}[{i}]"
            errors.extend(validate_value(item, item_schema, item_path, verbose))
    
    return errors


def validate_value(value: Any, schema: Dict, path: str, verbose: bool = False) -> List[str]:
    """Validate a value against its schema."""
    errors = []
    
    if "type" in schema:
        expected_type = schema["type"]
        type_errors = validate_type(value, expected_type, path)
        errors.extend(type_errors)
        
        if not type_errors:
            if expected_type == "string" and isinstance(value, str):
                errors.extend(validate_string_constraints(value, schema, path))
            elif expected_type in ("number", "integer") and isinstance(value, (int, float)):
                errors.extend(validate_number_constraints(value, schema, path))
            elif expected_type == "object" and isinstance(value, dict):
                errors.extend(validate_object(value, schema, path, verbose))
            elif expected_type == "array" and isinstance(value, list):
                errors.extend(validate_array(value, schema, path, verbose))
    
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} - Value '{value}' not in enum {schema['enum']}")
    
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path} - Value '{value}' does not match constant '{schema['const']}'")
    
    return errors


def get_entity_type_from_data_file(data_file: Path) -> str:
    """Extract entity type from data filename."""
    return data_file.stem.rstrip("s").rstrip("ie").rstrip("y")


def get_schema_for_data_file(data_file: Path) -> Path | None:
    """Find the corresponding schema file for a data file."""
    entity_type = data_file.stem
    possible_schemas = [
        SCHEMAS_DIR / f"{entity_type}.schema.json",
        SCHEMAS_DIR / f"{entity_type.rstrip('s')}.schema.json",
    ]
    
    for schema_path in possible_schemas:
        if schema_path.exists():
            return schema_path
    
    return None


def validate_data_file(data_file: Path, schema: Dict, verbose: bool = False) -> List[str]:
    """Validate a data file against its schema."""
    errors = []
    
    data, load_errors = load_json(data_file, verbose)
    errors.extend(load_errors)
    
    if data is None:
        return errors
    
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        records = [data]
    
    for i, record in enumerate(records):
        record_path = f"{data_file.name}:record[{i}]"
        record_errors = validate_value(record, schema, record_path, verbose)
        errors.extend(record_errors)
    
    return errors


def main():
    parser = argparse.ArgumentParser(
        description=f"Validate JSON data files against schemas - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    python {Path(__file__).name} --verbose
    python {Path(__file__).name}

{BRAND} - Schema Validation Tool
"""
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    print(f"=== {BRAND} Schema Validation ===")
    print()
    
    all_errors = []
    files_validated = 0
    files_failed = 0
    
    if not SCHEMAS_DIR.exists():
        print(f"Error: Schemas directory not found: {SCHEMAS_DIR}")
        sys.exit(1)
    
    if not DATA_DIR.exists():
        print(f"Error: Data directory not found: {DATA_DIR}")
        sys.exit(1)
    
    schema_files = sorted(SCHEMAS_DIR.glob("*.schema.json"))
    
    if args.verbose:
        print(f"Found {len(schema_files)} schema files")
        print()
    
    for schema_file in schema_files:
        entity_name = schema_file.stem.replace(".schema", "")
        data_file = DATA_DIR / f"{entity_name}s.json"
        
        if not data_file.exists():
            if args.verbose:
                print(f"Skipping {entity_name}: no data file at {data_file}")
            continue
        
        schema, schema_errors = load_json(schema_file, args.verbose)
        if schema_errors:
            all_errors.extend(schema_errors)
            files_failed += 1
            continue
        
        if args.verbose:
            print(f"Validating {data_file.name} against {schema_file.name}")
        
        validation_errors = validate_data_file(data_file, schema, args.verbose)
        
        if validation_errors:
            all_errors.extend(validation_errors)
            files_failed += 1
            print(f"  FAILED: {len(validation_errors)} errors")
        else:
            files_validated += 1
            print(f"  PASSED: {data_file.name}")
    
    print()
    print(f"=== Validation Summary ===")
    print(f"Files validated: {files_validated}")
    print(f"Files failed: {files_failed}")
    print(f"Total errors: {len(all_errors)}")
    
    if all_errors:
        print()
        print("=== Errors ===")
        for error in all_errors:
            print(f"  {error}")
        print()
        print(f"{BRAND} Schema Validation: FAILED")
        sys.exit(1)
    else:
        print()
        print(f"{BRAND} Schema Validation: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
