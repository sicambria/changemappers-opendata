"""
FastAPI Application Entry Point

ChangeMappers OpenData API - MVP Implementation

Provides read-only GET endpoints for:
- Entities (actors, organizations, initiatives, causes, patterns, stories)
- Relationships
- Search
- Graph traversal
"""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .dependencies import get_all_entity_types, get_entity_data, paginate
from .models import (
    EntityListResponse,
    ErrorResponse,
    GraphEdge,
    GraphNode,
    GraphResponse,
    HealthResponse,
    PaginationMeta,
    SearchResponse,
    SearchResult,
)

API_PREFIX = "/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Data directory: {settings.data_dir}")
    print(f"Entity types available: {len(get_all_entity_types())}")
    yield
    print("Shutting down API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail.get("error", "ERROR") if isinstance(exc.detail, dict) else str(exc.detail),
            "message": exc.detail.get("message", str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail),
        }
    )


@app.get(f"{API_PREFIX}/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """Health check endpoint"""
    entity_types = get_all_entity_types()
    total = sum(len(get_entity_data(t)) for t in entity_types)
    
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        entity_types=entity_types,
        total_entities=total,
    )


@app.get(f"{API_PREFIX}/{{entity_type}}", response_model=EntityListResponse, tags=["entities"])
async def list_entities(
    entity_type: str,
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
):
    """List entities of a specific type with pagination"""
    data = get_entity_data(entity_type)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Entity type '{entity_type}' not found or has no data"}
        )
    
    if name:
        data = [d for d in data if name.lower() in d.get("name", "").lower()]
    
    reverse = order == "desc"
    data = sorted(data, key=lambda x: x.get(sort, ""), reverse=reverse)
    
    paginated, pagination_meta = paginate(data, limit, offset)
    
    return EntityListResponse(
        data=paginated,
        pagination=PaginationMeta(**pagination_meta)
    )


@app.get(f"{API_PREFIX}/{{entity_type}}/{{entity_id}}", tags=["entities"])
async def get_entity(entity_type: str, entity_id: str):
    """Get a specific entity by ID"""
    data = get_entity_data(entity_type)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Entity type '{entity_type}' not found"}
        )
    
    for entity in data:
        if entity.get("id") == entity_id or entity.get("slug") == entity_id:
            return entity
    
    raise HTTPException(
        status_code=404,
        detail={"error": "NOT_FOUND", "message": f"Entity '{entity_id}' not found in {entity_type}"}
    )


@app.get(f"{API_PREFIX}/search", response_model=SearchResponse, tags=["search"])
async def search_entities(
    q: str = Query(..., min_length=1, description="Search query"),
    type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Search across all entities"""
    query = q.lower()
    entity_types = [type] if type else get_all_entity_types()
    
    results = []
    for etype in entity_types:
        data = get_entity_data(etype)
        for entity in data:
            name = entity.get("name", "").lower()
            description = entity.get("description", "").lower()
            
            score = 0.0
            highlights = {}
            
            if query in name:
                score += 2.0
                highlights["name"] = [entity.get("name", "")]
            if query in description:
                score += 1.0
            
            if score > 0:
                results.append(SearchResult(
                    id=entity.get("id", ""),
                    type=etype,
                    name=entity.get("name", ""),
                    description=entity.get("description"),
                    score=score,
                    highlights=highlights,
                ))
    
    results.sort(key=lambda x: x.score, reverse=True)
    paginated, pagination_meta = paginate(results, limit, offset)
    
    return SearchResponse(
        results=paginated,
        pagination=PaginationMeta(**pagination_meta),
        query=q,
        filters={"type": type} if type else {},
    )


@app.get(f"{API_PREFIX}/graph/{{entity_id}}", response_model=GraphResponse, tags=["graph"])
async def get_entity_graph(
    entity_id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth"),
    limit: int = Query(50, ge=1, le=200, description="Max nodes"),
):
    """Get the graph neighborhood of an entity"""
    nodes = []
    edges = []
    visited = set()
    node_count = 0
    
    entity_types = get_all_entity_types()
    entity_map = {}
    
    for etype in entity_types:
        data = get_entity_data(etype)
        for entity in data:
            eid = entity.get("id")
            if eid:
                entity_map[eid] = {**entity, "_type": etype}
    
    if entity_id not in entity_map:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"Entity '{entity_id}' not found"}
        )
    
    to_visit = [(entity_id, 0)]
    
    while to_visit and node_count < limit:
        current_id, current_depth = to_visit.pop(0)
        
        if current_id in visited or current_id not in entity_map:
            continue
        
        visited.add(current_id)
        entity = entity_map[current_id]
        
        nodes.append(GraphNode(
            id=current_id,
            type=entity.get("_type", "unknown"),
            name=entity.get("name"),
            properties={k: v for k, v in entity.items() if k not in ["id", "_type", "name"]},
        ))
        node_count += 1
        
        if current_depth >= depth:
            continue
        
        for key, value in entity.items():
            if key.endswith("_id") and isinstance(value, str) and value in entity_map:
                edges.append(GraphEdge(
                    source=current_id,
                    target=value,
                    type=key.replace("_id", ""),
                    properties={},
                ))
                to_visit.append((value, current_depth + 1))
            
            elif key.endswith("_ids") and isinstance(value, list):
                for vid in value[:10]:
                    if isinstance(vid, str) and vid in entity_map:
                        edges.append(GraphEdge(
                            source=current_id,
                            target=vid,
                            type=key.replace("_ids", ""),
                            properties={},
                        ))
                        to_visit.append((vid, current_depth + 1))
    
    node_types = defaultdict(int)
    for node in nodes:
        node_types[node.type] += 1
    
    return GraphResponse(
        nodes=nodes,
        edges=edges,
        statistics={
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_types": dict(node_types),
        }
    )


@app.get(f"{API_PREFIX}/taxonomies", tags=["taxonomies"])
async def list_taxonomies():
    """List all available entity types with counts"""
    taxonomies = []
    for etype in get_all_entity_types():
        data = get_entity_data(etype)
        taxonomies.append({
            "type": etype,
            "count": len(data),
            "endpoint": f"{API_PREFIX}/{etype}",
        })
    
    return {"taxonomies": taxonomies, "total_types": len(taxonomies)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
