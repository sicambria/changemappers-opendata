#!/usr/bin/env python3
"""
Legacy Data Transformation Script for changemappers.org

Transforms legacy data files to canonical schema format:
- open_source_tools.json -> tools.json
- causes.json -> causes.json
- systemic-change-patterns.json -> patterns.json
- systemic-change-stories.json -> stories.json
- metamodels.json -> frameworks.json
- traditions.json -> traditions.json
- learning-programs.json -> programs.json
- regenerative-skills.json -> skills.json

Usage:
    python scripts/transform_legacy.py --dry-run
    python scripts/transform_legacy.py --transform
"""

import argparse
import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

PROJECT_ROOT = Path(__file__).parent.parent
LEGACY_DIR = PROJECT_ROOT / "data" / "legacy"
OUTPUT_DIR = PROJECT_ROOT / "data" / "entities"


def generate_uuid(name: str) -> str:
    namespace = uuid.NAMESPACE_DNS
    return str(uuid.uuid5(namespace, name))


def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def get_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def transform_tool(record: dict) -> dict:
    name = record.get("name", "Unknown Tool")
    return {
        "id": generate_uuid(f"tool-{name}"),
        "slug": generate_slug(name),
        "name": name,
        "description": record.get("description", ""),
        "url": record.get("url"),
        "category": record.get("category", "").lower().replace("_", " "),
        "purpose": record.get("purpose"),
        "platform": record.get("platform"),
        "ease_of_use": record.get("ease_of_use", "").lower(),
        "type": "software",
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:open_source_tools",
    }


def transform_cause(record: dict) -> dict:
    title = record.get("title", "Untitled Cause")
    slug = record.get("slug", generate_slug(title))
    return {
        "id": generate_uuid(f"cause-{slug}"),
        "slug": slug,
        "name": title,
        "description": record.get("description", ""),
        "problems": record.get("problems"),
        "solutions": record.get("solutions"),
        "type": "systemic",
        "domain_refs": record.get("rdgDomains", []),
        "needed_functions": record.get("neededFunctions", []),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:causes",
    }


def transform_pattern(record: dict) -> dict:
    name = record.get("name", "Unnamed Pattern")
    return {
        "id": generate_uuid(f"pattern-{record.get('id', name)}"),
        "slug": generate_slug(name),
        "name": name,
        "description": record.get("description", ""),
        "country": record.get("country"),
        "type": record.get("type", "tactic").lower(),
        "complexity": record.get("c"),
        "scale": record.get("s"),
        "time_impact": record.get("t"),
        "category": record.get("category"),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:systemic-change-patterns",
    }


def transform_story(record: dict) -> dict:
    title = record.get("title", "Untitled Story")
    return {
        "id": generate_uuid(f"story-{generate_slug(title)}"),
        "slug": generate_slug(title),
        "name": title,
        "description": record.get("description", ""),
        "type": "case_study",
        "content": record.get("content"),
        "location": record.get("location"),
        "year": record.get("year"),
        "outcome": record.get("outcome"),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:systemic-change-stories",
    }


def transform_framework(record: dict) -> dict:
    name = record.get("name", record.get("title", "Unnamed Framework"))
    return {
        "id": generate_uuid(f"framework-{generate_slug(name)}"),
        "slug": generate_slug(name),
        "name": name,
        "description": record.get("description", ""),
        "type": "conceptual",
        "components": record.get("components", []),
        "principles": record.get("principles", []),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:metamodels",
    }


def transform_tradition(record: dict) -> dict:
    name = record.get("name", "Unnamed Tradition")
    return {
        "id": generate_uuid(f"tradition-{generate_slug(name)}"),
        "slug": generate_slug(name),
        "name": name,
        "description": record.get("description", ""),
        "type": record.get("type", "cultural").lower(),
        "origin": record.get("origin"),
        "values": record.get("values", []),
        "practices": record.get("practices", []),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:traditions",
    }


def transform_program(record: dict) -> dict:
    name = record.get("name", record.get("title", "Unnamed Program"))
    return {
        "id": generate_uuid(f"program-{generate_slug(name)}"),
        "slug": generate_slug(name),
        "name": name,
        "description": record.get("description", ""),
        "type": "educational",
        "format": "workshop_series",
        "duration": record.get("duration"),
        "target_audience": record.get("target_audience"),
        "prerequisites": record.get("prerequisites", []),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:learning-programs",
    }


def transform_skill(record: dict) -> dict:
    name = record.get("name", "Unnamed Skill")
    return {
        "id": generate_uuid(f"skill-{generate_slug(name)}"),
        "slug": generate_slug(name),
        "name": name,
        "description": record.get("description", ""),
        "type": "competency",
        "category": record.get("category", "").lower(),
        "level_options": record.get("levels", ["beginner", "intermediate", "advanced"]),
        "created_at": get_timestamp(),
        "updated_at": get_timestamp(),
        "source": "legacy:regenerative-skills",
    }


TRANSFORMERS = {
    "open_source_tools.json": ("tools", transform_tool),
    "causes.json": ("causes", transform_cause),
    "systemic-change-patterns.json": ("patterns", transform_pattern),
    "systemic-change-stories.json": ("stories", transform_story),
    "metamodels.json": ("frameworks", transform_framework),
    "traditions.json": ("traditions", transform_tradition),
    "learning-programs.json": ("programs", transform_program),
    "regenerative-skills.json": ("skills", transform_skill),
}


def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def transform_file(legacy_file: str, dry_run: bool = False) -> dict:
    legacy_path = LEGACY_DIR / legacy_file
    if not legacy_path.exists():
        return {"error": f"File not found: {legacy_path}"}
    
    output_type, transformer = TRANSFORMERS.get(legacy_file, (None, None))
    if not output_type:
        return {"error": f"No transformer for: {legacy_file}"}
    
    data = load_json(legacy_path)
    if data is None:
        return {"error": f"Failed to load: {legacy_file}"}
    
    if legacy_file == "systemic-change-patterns.json":
        patterns = data.get("change-patterns", data.get("patterns", data.get("records", [])))
        data = patterns if isinstance(patterns, list) else []
    elif legacy_file == "systemic-change-stories.json":
        stories = data.get("change-stories", data.get("stories", data.get("records", [])))
        data = stories if isinstance(stories, list) else []
    
    if not isinstance(data, list):
        data = [data]
    
    transformed = []
    for record in data:
        try:
            transformed.append(transformer(record))
        except Exception as e:
            print(f"  Error transforming record: {e}")
    
    output_path = OUTPUT_DIR / f"{output_type}.json"
    
    result = {
        "source": legacy_file,
        "output_type": output_type,
        "input_count": len(data),
        "output_count": len(transformed),
        "output_path": str(output_path),
    }
    
    if not dry_run:
        save_json({
            "records": transformed,
            "metadata": {
                "source": f"legacy:{legacy_file}",
                "transformed_at": get_timestamp(),
                "count": len(transformed),
            }
        }, output_path)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Transform legacy data to canonical format")
    parser.add_argument("--transform", action="store_true", help="Write transformed data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be transformed")
    parser.add_argument("--file", "-f", help="Transform specific file only")
    args = parser.parse_args()
    
    files_to_process = [args.file] if args.file else list(TRANSFORMERS.keys())
    
    print("=" * 60)
    print("LEGACY DATA TRANSFORMATION")
    print("=" * 60)
    print()
    
    total_input = 0
    total_output = 0
    
    for legacy_file in files_to_process:
        print(f"\n[{legacy_file}]")
        result = transform_file(legacy_file, dry_run=not args.transform)
        
        if "error" in result:
            print(f"  ERROR: {result['error']}")
            continue
        
        print(f"  Type: {result['output_type']}")
        print(f"  Input: {result['input_count']} records")
        print(f"  Output: {result['output_count']} records")
        
        if args.dry_run:
            print(f"  Would write: {result['output_path']}")
        elif args.transform:
            print(f"  Wrote: {result['output_path']}")
        
        total_input += result['input_count']
        total_output += result['output_count']
    
    print()
    print("=" * 60)
    print(f"Total input records: {total_input}")
    print(f"Total output records: {total_output}")
    
    if args.dry_run:
        print("\nRun with --transform to write files")


if __name__ == "__main__":
    main()
