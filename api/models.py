"""
Pydantic models for API responses
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of records")
    limit: int = Field(..., description="Records per page")
    offset: int = Field(..., description="Current offset")
    has_more: bool = Field(..., description="More records available")


class EntityResponse(BaseModel):
    """Base response for single entity"""
    id: str
    slug: Optional[str] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    source: Optional[str] = None


class EntityListResponse(BaseModel):
    """Response for entity list"""
    data: list[dict[str, Any]]
    pagination: PaginationMeta


class RelationshipResponse(BaseModel):
    """Response for relationship"""
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    confidence: Optional[float] = None
    source_type: Optional[str] = None
    target_type: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class GraphNode(BaseModel):
    """Node in graph response"""
    id: str
    type: str
    name: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Edge in graph response"""
    source: str
    target: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphResponse(BaseModel):
    """Response for graph query"""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    statistics: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Search result item"""
    id: str
    type: str
    name: str
    description: Optional[str] = None
    score: float = Field(..., description="Relevance score")
    highlights: dict[str, list[str]] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response for search query"""
    results: list[SearchResult]
    pagination: PaginationMeta
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str
    entity_types: list[str]
    total_entities: int
