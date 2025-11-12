import argparse
import sys
import os
import urllib.request
import tarfile
import io
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def parse_arguments():
    parser = argparse.ArgumentParser(description="A minimal CLI application for visualizing a dependency graph")
    parser.add_argument(
        '--package',
        required=True,
        help='Name of the package (required)'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='URL or path to the repository (required)'
    )
    parser.add_argument(
        '--mode',
        required=False,
        default="remote",
        choices=['local', 'remote', 'test'],
        help='Repository working mode {local, remote, or test} P.S. (default: remote)'
    )
    parser.add_argument(
        '--version',
        required=False,
        default='latest',
        help='Package version (default: latest)'
    )
    parser.add_argument(
        '--output',
        required=False,
        default="graph.png",
        help='The name of the file containing the graph image (default: graph.png)'
    )
    parser.add_argument(
        '--print-order',
        action='store_true',
        help='Print the load order of dependencies (dependencies first)'
    )
    return parser

def fetch_apkindex(repo, mode):
    if mode == 'remote':
        apkindex_path = f"{repo}/APKINDEX.tar.gz"
        try:
            with urllib.request.urlopen(apkindex_path) as response:
                return response.read()
        except Exception as e:
            raise Exception(f"Failed to fetch APKINDEX: {str(e)}")
    elif mode == 'local':
        apkindex_path = os.path.join(repo, 'APKINDEX.tar.gz')
        try:
            with open(apkindex_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to fetch APKINDEX: {str(e)}")
    elif mode == 'test':
        try:
            with open(repo, 'rb') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to fetch test file: {str(e)}")

def parse_apkindex(data, mode):
    if mode != 'test':
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
                for member in tar.getmembers():
                    if member.name == 'APKINDEX':
                        apkindex_file = tar.extractfile(member)
                        apkindex_content = apkindex_file.read().decode('utf-8')
                        break
                else:
                    raise Exception("APKINDEX file not found in archive")
        except Exception as e:
            raise Exception(f"Failed to parse tar: {str(e)}")
    else:
        apkindex_content = data.decode('utf-8')
    all_entries = defaultdict(list)
    current_package = None
    current_version = None
    dependencies = []
    for line in apkindex_content.splitlines():
        if not line:
            if current_package:
                all_entries[current_package].append((current_version, dependencies))
            current_package = None
            current_version = None
            dependencies = []
            continue
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        value = value.strip()
        if key == 'P':
            if current_package:
                all_entries[current_package].append((current_version, dependencies))
            current_package = value
            current_version = None
            dependencies = []
        elif key == 'V':
            current_version = value
        elif key == 'D':
            dependencies = [dep.strip().split('>')[0].split('<')[0].split('=')[0] for dep in value.split() if dep.strip()]
    if current_package:
        all_entries[current_package].append((current_version, dependencies))
    return all_entries

def get_deps(pkg, ver, all_entries):
    entries = all_entries.get(pkg, [])
    if not entries:
        raise Exception(f"Package {pkg} not found")
    selected_ver = None
    if ver == 'latest':
        vers = [v for v, d in entries if v is not None]
        if vers:
            selected_ver = max(vers)
        else:
            selected_ver = None
    else:
        selected_ver = ver
    for v, d in entries:
        if v == selected_ver:
            return d
    raise Exception(f"Version {ver} for {pkg} not found")

def build_graph_recursive(level, visited, G, all_entries):
    next_level = []
    for pkg in level:
        if pkg in visited:
            continue
        visited.add(pkg)
        deps = get_deps(pkg, 'latest', all_entries)
        for dep in deps:
            G.add_edge(pkg, dep)
            if dep not in visited:
                next_level.append(dep)
    if next_level:
        build_graph_recursive(next_level, visited, G, all_entries)

def main():
    try:
        parser = parse_arguments()
        args = parser.parse_args()
        print(f"package: {args.package}")
        print(f"repo: {args.repo}")
        print(f"mode: {args.mode}")
        print(f"version: {args.version}")
        print(f"output file: {args.output}")
        apkindex_data = fetch_apkindex(args.repo, args.mode)
        all_entries = parse_apkindex(apkindex_data, args.mode)
        root_deps = get_deps(args.package, args.version, all_entries)
        print("\nDirect dependencies:")
        if root_deps:
            for dep in root_deps:
                print(dep)
        else:
            print("No dependencies found")
        G = nx.DiGraph()
        visited = set()
        root = args.package
        G.add_node(root)
        visited.add(root)
        initial_level = []
        for dep in root_deps:
            G.add_edge(root, dep)
            initial_level.append(dep)
        build_graph_recursive(initial_level, visited, G, all_entries)
        cycles = list(nx.simple_cycles(G))
        if cycles:
            print("Warning: Cyclic dependencies detected.")
            for cycle in cycles:
                print("Cycle: " + " -> ".join(map(str, cycle)) + " -> " + str(cycle[0]))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', arrows=True)
        plt.title(f"Dependency Graph for {args.package}")
        plt.savefig(args.output)
        plt.close()
        print(f"Graph saved to {args.output}")
        if args.print_order:
            print("\nComputing load order...")
            if cycles:
                print("Cannot compute load order due to cyclic dependencies.")
            else:
                try:
                    topo_order = list(nx.topological_sort(G))
                    load_order = topo_order[::-1]
                    print("\nLoad order (dependencies first):")
                    for pkg in load_order:
                        print(pkg)
                except nx.NetworkXUnfeasible as e:
                    print(f"Error: {str(e)}")
    except SystemExit:
        print("Error: Invalid command line arguments.")
        print("Please check the help list below:")
        parser.print_help()
        sys.exit(1)
    except Exception as e:
        print(f"error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()