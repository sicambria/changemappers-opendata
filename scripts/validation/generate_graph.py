#!/usr/bin/env python3
"""
Knowledge Graph Generation Script for changemappers.org

Generates knowledge graph from entity and relationship data:
- Loads all entity and relationship data
- Builds network graph structure
- Exports as GraphML and JSON formats
- Generates graph statistics report

Usage:
    python generate_graph.py [OPTIONS]

Options:
    --output-dir    Output directory for generated files
    --verbose       Enable verbose output
    --help          Show this help message
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

BRAND = "changemappers.org"
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ENTITIES_DIR = DATA_DIR / "entities"
RELATIONSHIPS_DIR = DATA_DIR / "relationships"


def load_json(file_path: Path) -> tuple[Any, list[str]]:
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


class KnowledgeGraph:
    """Simple knowledge graph representation."""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.node_types: Dict[str, str] = {}
        self.edge_types: Dict[str, int] = defaultdict(int)
    
    def add_node(self, node_id: str, node_type: str, properties: Dict | None = None):
        """Add a node to the graph."""
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "properties": properties or {}
            }
            self.node_types[node_id] = node_type
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: Dict | None = None):
        """Add an edge to the graph."""
        edge = {
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "properties": properties or {}
        }
        self.edges.append(edge)
        self.edge_types[edge_type] += 1
    
    def get_node_degree(self, node_id: str) -> int:
        """Get the degree (number of connections) for a node."""
        degree = 0
        for edge in self.edges:
            if edge["source"] == node_id or edge["target"] == node_id:
                degree += 1
        return degree
    
    def get_statistics(self) -> Dict:
        """Generate graph statistics."""
        degrees = [self.get_node_degree(n) for n in self.nodes]
        
        type_counts = defaultdict(int)
        for node_type in self.node_types.values():
            type_counts[node_type] += 1
        
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": dict(type_counts),
            "edge_types": dict(self.edge_types),
            "avg_degree": sum(degrees) / len(degrees) if degrees else 0,
            "max_degree": max(degrees) if degrees else 0,
            "min_degree": min(degrees) if degrees else 0,
            "isolated_nodes": degrees.count(0)
        }


def load_entities(entities_dir: Path, graph: KnowledgeGraph, verbose: bool = False) -> list[str]:
    """Load all entities into the graph."""
    errors = []
    
    if not entities_dir.exists():
        errors.append(f"Entities directory not found: {entities_dir}")
        return errors
    
    for entity_file in sorted(entities_dir.glob("*.json")):
        entity_type = entity_file.stem
        
        data, load_errors = load_json(entity_file)
        if load_errors:
            errors.extend(load_errors)
            continue
        
        if data is None:
            continue
        
        records = data.get("records", data) if isinstance(data, dict) else data
        if not isinstance(records, list):
            records = [records]
        
        for record in records:
            if not isinstance(record, dict):
                continue
            
            node_id = record.get("id")
            if not node_id:
                continue
            
            properties = {k: v for k, v in record.items() if k != "id"}
            graph.add_node(node_id, entity_type, properties)
            
            if verbose:
                print(f"  Added node: {node_id} ({entity_type})")
        
        if verbose:
            print(f"Loaded {len(records)} {entity_type} entities")
    
    return errors


def load_relationships(relationships_dir: Path, graph: KnowledgeGraph, verbose: bool = False) -> list[str]:
    """Load all relationships into the graph."""
    errors = []
    
    if not relationships_dir.exists():
        errors.append(f"Relationships directory not found: {relationships_dir}")
        return errors
    
    for rel_file in sorted(relationships_dir.glob("*.json")):
        rel_type = rel_file.stem
        
        data, load_errors = load_json(rel_file)
        if load_errors:
            errors.extend(load_errors)
            continue
        
        if data is None:
            continue
        
        rel_type_from_data = data.get("relationship_type", rel_type)
        records = data.get("records", data) if isinstance(data, dict) else data
        if not isinstance(records, list):
            records = [records]
        
        for record in records:
            if not isinstance(record, dict):
                continue
            
            source_id = record.get("source_id")
            target_id = record.get("target_id")
            
            if not source_id or not target_id:
                continue
            
            properties = {k: v for k, v in record.items() if k not in ("source_id", "target_id")}
            graph.add_edge(source_id, target_id, rel_type_from_data, properties)
            
            if verbose:
                print(f"  Added edge: {source_id} -> {target_id} ({rel_type_from_data})")
        
        if verbose:
            print(f"Loaded {len(records)} {rel_type_from_data} relationships")
    
    return errors


def export_graphml(graph: KnowledgeGraph, output_path: Path):
    """Export graph as GraphML format."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<graphml xmlns="http://graphml.graphdrawing.ml/xmlns">')
    lines.append('  <key id="type" for="node" attr.name="type" attr.type="string"/>')
    lines.append('  <key id="label" for="node" attr.name="label" attr.type="string"/>')
    lines.append('  <key id="type" for="edge" attr.name="type" attr.type="string"/>')
    lines.append('  <graph id="G" edgedefault="directed">')
    
    for node_id, node_data in graph.nodes.items():
        node_type = node_data.get("type", "unknown")
        label = node_data.get("properties", {}).get("name", node_id)
        lines.append(f'    <node id="{node_id}">')
        lines.append(f'      <data key="type">{node_type}</data>')
        lines.append(f'      <data key="label">{label}</data>')
        lines.append('    </node>')
    
    for i, edge in enumerate(graph.edges):
        lines.append(f'    <edge id="e{i}" source="{edge["source"]}" target="{edge["target"]}">')
        lines.append(f'      <data key="type">{edge["type"]}</data>')
        lines.append('    </edge>')
    
    lines.append('  </graph>')
    lines.append('</graphml>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def export_json_graph(graph: KnowledgeGraph, output_path: Path):
    """Export graph as JSON format."""
    graph_data = {
        "metadata": {
            "generator": BRAND,
            "format": "knowledge_graph_json",
            "version": "1.0.0"
        },
        "nodes": list(graph.nodes.values()),
        "edges": graph.edges,
        "statistics": graph.get_statistics()
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)


def generate_statistics_report(stats: Dict) -> str:
    """Generate markdown statistics report."""
    report = []
    report.append(f"# Knowledge Graph Statistics")
    report.append(f"")
    report.append(f"**Generated by {BRAND}**")
    report.append(f"")
    report.append(f"## Overview")
    report.append(f"")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Nodes | {stats['node_count']} |")
    report.append(f"| Total Edges | {stats['edge_count']} |")
    report.append(f"| Average Degree | {stats['avg_degree']:.2f} |")
    report.append(f"| Max Degree | {stats['max_degree']} |")
    report.append(f"| Min Degree | {stats['min_degree']} |")
    report.append(f"| Isolated Nodes | {stats['isolated_nodes']} |")
    report.append(f"")
    report.append(f"## Node Types")
    report.append(f"")
    report.append(f"| Type | Count |")
    report.append(f"|------|-------|")
    for node_type, count in sorted(stats['node_types'].items()):
        report.append(f"| {node_type} | {count} |")
    report.append(f"")
    report.append(f"## Edge Types")
    report.append(f"")
    report.append(f"| Type | Count |")
    report.append(f"|------|-------|")
    for edge_type, count in sorted(stats['edge_types'].items()):
        report.append(f"| {edge_type} | {count} |")
    report.append(f"")
    report.append(f"---")
    report.append(f"*{BRAND} - Knowledge Graph Generator*")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description=f"Generate knowledge graph - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    python {Path(__file__).name} --verbose
    python {Path(__file__).name} --output-dir ./output

{BRAND} - Knowledge Graph Generator
"""
    )
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    print(f"=== {BRAND} Knowledge Graph Generator ===")
    print()
    
    output_dir = Path(args.output_dir) if args.output_dir else PROJECT_ROOT / "output" / "graph"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    graph = KnowledgeGraph()
    
    print("Loading entities...")
    errors = load_entities(ENTITIES_DIR, graph, args.verbose)
    if errors:
        for error in errors:
            print(f"  Error: {error}")
    
    print(f"Loaded {len(graph.nodes)} nodes")
    print()
    
    print("Loading relationships...")
    errors = load_relationships(RELATIONSHIPS_DIR, graph, args.verbose)
    if errors:
        for error in errors:
            print(f"  Error: {error}")
    
    print(f"Loaded {len(graph.edges)} edges")
    print()
    
    stats = graph.get_statistics()
    
    print("Exporting graph...")
    graphml_path = output_dir / "knowledge_graph.graphml"
    export_graphml(graph, graphml_path)
    print(f"  GraphML: {graphml_path}")
    
    json_path = output_dir / "knowledge_graph.json"
    export_json_graph(graph, json_path)
    print(f"  JSON: {json_path}")
    
    report_path = output_dir / "graph_statistics.md"
    report = generate_statistics_report(stats)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Report: {report_path}")
    print()
    
    print(report)
    print()
    print(f"{BRAND} Knowledge Graph Generation: COMPLETE")
    sys.exit(0)


if __name__ == "__main__":
    main()
