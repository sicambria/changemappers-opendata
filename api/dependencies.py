"""
Common dependencies for API endpoints
"""

from functools import lru_cache
from typing import Any

from .config import settings


@lru_cache
def get_entity_data(entity_type: str) -> list[dict[str, Any]]:
    """Load entity data from JSON file"""
    import json
    
    file_path = settings.data_dir / f"{entity_type}.json"
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    return data if isinstance(data, list) else []


def get_all_entity_types() -> list[str]:
    """Get list of all entity types with data"""
    entity_types = []
    for file_path in settings.data_dir.glob("*.json"):
        entity_types.append(file_path.stem)
    return sorted(entity_types)


def paginate(data: list, limit: int = 20, offset: int = 0) -> tuple[list, dict]:
    """Paginate results and return pagination metadata"""
    total = len(data)
    paginated = data[offset : offset + limit]
    has_more = offset + limit < total
    
    return paginated, {
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }
