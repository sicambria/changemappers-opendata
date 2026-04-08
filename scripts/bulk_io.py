#!/usr/bin/env python3
"""
Bulk Import/Export CLI Tool for changemappers.org

Converts between JSON, CSV, GraphML, and Neo4j formats for knowledge graph data.

Usage:
    python bulk_io.py export --format csv --output ./output/
    python bulk_io.py import --format json --input ./data.json
    python bulk_io.py convert --from json --to neo4j --input ./data.json --output ./neo4j/
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

BRAND = "changemappers.org"
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ENTITIES_DIR = DATA_DIR / "entities"
RELATIONSHIPS_DIR = DATA_DIR / "relationships"


def load_json(file_path: Path) -> tuple[Optional[Any], List[str]]:
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


def save_json(data: Any, file_path: Path, indent: int = 2) -> List[str]:
    errors = []
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        errors.append(f"{file_path} - Error saving file: {str(e)}")
    return errors


class GraphData:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.node_types: Dict[str, str] = {}
        self.edge_types: Dict[str, int] = defaultdict(int)

    def add_node(self, node_id: str, node_type: str, properties: Optional[Dict] = None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "properties": properties or {}
            }
            self.node_types[node_id] = node_type

    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: Optional[Dict] = None):
        edge = {
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "properties": properties or {}
        }
        self.edges.append(edge)
        self.edge_types[edge_type] += 1

    def get_statistics(self) -> Dict:
        degrees = defaultdict(int)
        for edge in self.edges:
            degrees[edge["source"]] += 1
            degrees[edge["target"]] += 1

        degree_values = list(degrees.values()) if degrees else [0]

        type_counts = defaultdict(int)
        for node_type in self.node_types.values():
            type_counts[node_type] += 1

        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": dict(type_counts),
            "edge_types": dict(self.edge_types),
            "avg_degree": sum(degree_values) / len(degree_values) if degree_values else 0,
            "max_degree": max(degree_values) if degree_values else 0,
            "min_degree": min(degree_values) if degree_values else 0,
            "isolated_nodes": len(self.nodes) - len(degrees)
        }


def load_entities(entities_dir: Path, graph: GraphData, verbose: bool = False) -> List[str]:
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


def load_relationships(relationships_dir: Path, graph: GraphData, verbose: bool = False) -> List[str]:
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


def export_csv(graph: GraphData, output_dir: Path) -> List[str]:
    errors = []
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_file = output_dir / "nodes.csv"
    edges_file = output_dir / "edges.csv"

    all_node_props = set()
    for node in graph.nodes.values():
        all_node_props.update(node.get("properties", {}).keys())

    node_fieldnames = ["id", "type"] + sorted(all_node_props)

    try:
        with open(nodes_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=node_fieldnames, extrasaction="ignore")
            writer.writeheader()
            for node in graph.nodes.values():
                row = {"id": node["id"], "type": node["type"]}
                row.update(node.get("properties", {}))
                for k, v in row.items():
                    if isinstance(v, (dict, list)):
                        row[k] = json.dumps(v)
                writer.writerow(row)
    except Exception as e:
        errors.append(f"Error writing {nodes_file}: {e}")

    all_edge_props = set()
    for edge in graph.edges:
        all_edge_props.update(edge.get("properties", {}).keys())

    edge_fieldnames = ["source", "target", "type"] + sorted(all_edge_props)

    try:
        with open(edges_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=edge_fieldnames, extrasaction="ignore")
            writer.writeheader()
            for edge in graph.edges:
                row = {"source": edge["source"], "target": edge["target"], "type": edge["type"]}
                row.update(edge.get("properties", {}))
                for k, v in row.items():
                    if isinstance(v, (dict, list)):
                        row[k] = json.dumps(v)
                writer.writerow(row)
    except Exception as e:
        errors.append(f"Error writing {edges_file}: {e}")

    return errors


def export_graphml(graph: GraphData, output_path: Path) -> List[str]:
    errors = []
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<graphml xmlns="http://graphml.graphdrawing.ml/xmlns">')
        lines.append('  <key id="type" for="node" attr.name="type" attr.type="string"/>')
        lines.append('  <key id="label" for="node" attr.name="label" attr.type="string"/>')
        lines.append('  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>')
        lines.append('  <key id="etype" for="edge" attr.name="type" attr.type="string"/>')
        lines.append('  <graph id="G" edgedefault="directed">')

        for node_id, node_data in graph.nodes.items():
            node_type = node_data.get("type", "unknown")
            label = node_data.get("properties", {}).get("name", node_id)
            lines.append(f'    <node id="{node_id}">')
            lines.append(f'      <data key="type">{node_type}</data>')
            lines.append(f'      <data key="label">{label}</data>')
            lines.append('    </node>')

        for i, edge in enumerate(graph.edges):
            weight = edge.get("properties", {}).get("confidence", 1.0)
            lines.append(f'    <edge id="e{i}" source="{edge["source"]}" target="{edge["target"]}">')
            lines.append(f'      <data key="etype">{edge["type"]}</data>')
            lines.append(f'      <data key="weight">{weight}</data>')
            lines.append('    </edge>')

        lines.append('  </graph>')
        lines.append('</graphml>')

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        errors.append(f"Error writing GraphML: {e}")

    return errors


def export_neo4j(graph: GraphData, output_dir: Path) -> List[str]:
    errors = []
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_file = output_dir / "nodes.csv"
    edges_file = output_dir / "relationships.csv"

    try:
        with open(nodes_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([":ID", "name:STRING", "type:STRING", "labels:STRING[]"])
            for node_id, node_data in graph.nodes.items():
                name = node_data.get("properties", {}).get("name", node_id)
                node_type = node_data.get("type", "unknown")
                labels = ";".join([node_type, "Entity"])
                writer.writerow([node_id, name, node_type, labels])
    except Exception as e:
        errors.append(f"Error writing Neo4j nodes: {e}")

    try:
        with open(edges_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([":START_ID", ":END_ID", ":TYPE", "weight:FLOAT"])
            for edge in graph.edges:
                weight = edge.get("properties", {}).get("confidence", 1.0)
                writer.writerow([edge["source"], edge["target"], edge["type"].upper(), weight])
    except Exception as e:
        errors.append(f"Error writing Neo4j relationships: {e}")

    return errors


def export_json_graph(graph: GraphData, output_path: Path) -> List[str]:
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
    return save_json(graph_data, output_path)


def import_csv_nodes(file_path: Path, graph: GraphData, verbose: bool = False) -> List[str]:
    errors = []
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_id = row.get("id")
                node_type = row.get("type", "unknown")
                if not node_id:
                    continue
                properties = {k: v for k, v in row.items() if k not in ("id", "type")}
                graph.add_node(node_id, node_type, properties)
                if verbose:
                    print(f"  Imported node: {node_id}")
    except Exception as e:
        errors.append(f"Error importing CSV nodes: {e}")
    return errors


def import_csv_edges(file_path: Path, graph: GraphData, verbose: bool = False) -> List[str]:
    errors = []
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                source_id = row.get("source")
                target_id = row.get("target")
                edge_type = row.get("type", "RELATED_TO")
                if not source_id or not target_id:
                    continue
                properties = {k: v for k, v in row.items() if k not in ("source", "target", "type")}
                graph.add_edge(source_id, target_id, edge_type, properties)
                if verbose:
                    print(f"  Imported edge: {source_id} -> {target_id}")
    except Exception as e:
        errors.append(f"Error importing CSV edges: {e}")
    return errors


def cmd_export(args):
    print(f"=== {BRAND} Bulk Export ===")
    print()

    graph = GraphData()
    
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

    output_dir = Path(args.output) if args.output else PROJECT_ROOT / "output" / "export"
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = args.format.lower()
    print(f"Exporting to {fmt.upper()} format...")

    if fmt == "csv":
        errors = export_csv(graph, output_dir)
    elif fmt == "graphml":
        errors = export_graphml(graph, output_dir / "knowledge_graph.graphml")
    elif fmt == "neo4j":
        errors = export_neo4j(graph, output_dir)
    elif fmt == "json":
        errors = export_json_graph(graph, output_dir / "knowledge_graph.json")
    else:
        print(f"Unknown format: {fmt}")
        sys.exit(1)

    if errors:
        for error in errors:
            print(f"  Error: {error}")
        sys.exit(1)

    print(f"Output written to: {output_dir}")
    print()

    stats = graph.get_statistics()
    print(f"Exported {stats['node_count']} nodes and {stats['edge_count']} edges")
    print(f"{BRAND} Bulk Export: COMPLETE")


def cmd_import(args):
    print(f"=== {BRAND} Bulk Import ===")
    print()

    input_dir = Path(args.input) if args.input else PROJECT_ROOT / "input"
    graph = GraphData()

    fmt = args.format.lower()
    print(f"Importing from {fmt.upper()} format...")

    if fmt == "csv":
        nodes_file = input_dir / "nodes.csv"
        edges_file = input_dir / "edges.csv"
        if nodes_file.exists():
            errors = import_csv_nodes(nodes_file, graph, args.verbose)
            if errors:
                for error in errors:
                    print(f"  Error: {error}")
        if edges_file.exists():
            errors = import_csv_edges(edges_file, graph, args.verbose)
            if errors:
                for error in errors:
                    print(f"  Error: {error}")
    elif fmt == "json":
        data, errors = load_json(Path(args.input))
        if errors:
            for error in errors:
                print(f"  Error: {error}")
            sys.exit(1)
        if data:
            for node in data.get("nodes", []):
                graph.add_node(node["id"], node.get("type", "unknown"), node.get("properties"))
            for edge in data.get("edges", []):
                graph.add_edge(edge["source"], edge["target"], edge.get("type", "RELATED_TO"), edge.get("properties"))
    else:
        print(f"Unknown format: {fmt}")
        sys.exit(1)

    print(f"Imported {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    print(f"{BRAND} Bulk Import: COMPLETE")


def cmd_convert(args):
    print(f"=== {BRAND} Format Conversion ===")
    print()

    graph = GraphData()
    input_path = Path(args.input)
    output_dir = Path(args.output) if args.output else PROJECT_ROOT / "output" / "converted"
    output_dir.mkdir(parents=True, exist_ok=True)

    input_format = args.frm.lower()
    output_format = args.to.lower()

    print(f"Converting {input_format.upper()} to {output_format.upper()}...")

    if input_format == "json":
        data, errors = load_json(input_path)
        if errors:
            for error in errors:
                print(f"  Error: {error}")
            sys.exit(1)
        if data:
            for node in data.get("nodes", []):
                graph.add_node(node["id"], node.get("type", "unknown"), node.get("properties"))
            for edge in data.get("edges", []):
                graph.add_edge(edge["source"], edge["target"], edge.get("type", "RELATED_TO"), edge.get("properties"))
    elif input_format == "csv":
        nodes_file = input_path.parent / "nodes.csv"
        edges_file = input_path.parent / "edges.csv"
        if nodes_file.exists():
            import_csv_nodes(nodes_file, graph, args.verbose)
        if edges_file.exists():
            import_csv_edges(edges_file, graph, args.verbose)
    else:
        print(f"Unknown input format: {input_format}")
        sys.exit(1)

    print(f"Loaded {len(graph.nodes)} nodes and {len(graph.edges)} edges")

    if output_format == "csv":
        errors = export_csv(graph, output_dir)
    elif output_format == "graphml":
        errors = export_graphml(graph, output_dir / "knowledge_graph.graphml")
    elif output_format == "neo4j":
        errors = export_neo4j(graph, output_dir)
    elif output_format == "json":
        errors = export_json_graph(graph, output_dir / "knowledge_graph.json")
    else:
        print(f"Unknown output format: {output_format}")
        sys.exit(1)

    if errors:
        for error in errors:
            print(f"  Error: {error}")
        sys.exit(1)

    print(f"Converted to: {output_dir}")
    print(f"{BRAND} Format Conversion: COMPLETE")


def cmd_info(args):
    print(f"=== {BRAND} Data Info ===")
    print()

    graph = GraphData()

    print("Loading entities...")
    load_entities(ENTITIES_DIR, graph, False)
    print(f"Loaded {len(graph.nodes)} nodes")
    print()

    print("Loading relationships...")
    load_relationships(RELATIONSHIPS_DIR, graph, False)
    print(f"Loaded {len(graph.edges)} edges")
    print()

    stats = graph.get_statistics()
    print("=== Graph Statistics ===")
    print(f"Nodes: {stats['node_count']}")
    print(f"Edges: {stats['edge_count']}")
    print(f"Avg Degree: {stats['avg_degree']:.2f}")
    print(f"Max Degree: {stats['max_degree']}")
    print(f"Isolated Nodes: {stats['isolated_nodes']}")
    print()
    print("Node Types:")
    for t, c in sorted(stats['node_types'].items()):
        print(f"  {t}: {c}")
    print()
    print("Edge Types:")
    for t, c in sorted(stats['edge_types'].items()):
        print(f"  {t}: {c}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Bulk Import/Export CLI - {BRAND}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    export_parser = subparsers.add_parser("export", help="Export data to various formats")
    export_parser.add_argument("--format", "-f", required=True, choices=["json", "csv", "graphml", "neo4j"], help="Output format")
    export_parser.add_argument("--output", "-o", help="Output directory")
    export_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    import_parser = subparsers.add_parser("import", help="Import data from various formats")
    import_parser.add_argument("--format", "-f", required=True, choices=["json", "csv"], help="Input format")
    import_parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    import_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    convert_parser = subparsers.add_parser("convert", help="Convert between formats")
    convert_parser.add_argument("--from", dest="frm", required=True, choices=["json", "csv"], help="Source format")
    convert_parser.add_argument("--to", dest="to", required=True, choices=["json", "csv", "graphml", "neo4j"], help="Target format")
    convert_parser.add_argument("--input", "-i", required=True, help="Input file")
    convert_parser.add_argument("--output", "-o", help="Output directory")
    convert_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    info_parser = subparsers.add_parser("info", help="Show data information and statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "export":
        cmd_export(args)
    elif args.command == "import":
        cmd_import(args)
    elif args.command == "convert":
        cmd_convert(args)
    elif args.command == "info":
        cmd_info(args)


if __name__ == "__main__":
    main()
