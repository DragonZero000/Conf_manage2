import argparse
import sys
import os
import urllib.request
import tarfile
import io


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
        choices=['local', 'remote'],
        help='Repository working mode {local or remote} P.S. (default: remote)'
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
    return parser

def fetch_apkindex(repo, mode):
    apkindex_path = os.path.join(repo, 'APKINDEX.tar.gz') if mode == 'local' else f"{repo}/APKINDEX.tar.gz"
    try:
        if mode == 'remote':
            with urllib.request.urlopen(apkindex_path) as response:
                return response.read()
        else:
            with open(apkindex_path, 'rb') as f:
                return f.read()
    except Exception as e:
        raise Exception(f"Failed to fetch APKINDEX: {str(e)}")

def parse_apkindex(data, package_name, package_version):
    dependencies = []
    current_package = None
    found = False
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        for member in tar.getmembers():
            if member.name == 'APKINDEX':
                apkindex_file = tar.extractfile(member)
                apkindex_content = apkindex_file.read().decode('utf-8')
                break
        else:
            raise Exception("APKINDEX file not found in archive")
    for line in apkindex_content.splitlines():
        if not line:
            if current_package and found:
                break
            current_package = None
            continue
        key, value = line.split(':', 1) if ':' in line else (line, '')
        if key == 'P':
            current_package = value
        elif key == 'V' and current_package == package_name:
            if package_version == 'latest' or value == package_version:
                found = True
        elif key == 'D' and current_package == package_name and found:
            dependencies = [dep.split('>')[0].split('<')[0].split('=')[0] for dep in value.split()]
    if not found:
        raise Exception(f"Package {package_name} with version {package_version} not found")
    return dependencies

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
        dependencies = parse_apkindex(apkindex_data, args.package, args.version)
        print("\nDirect dependencies:")
        if dependencies:
            for dep in dependencies:
                print(dep)
        else:
            print("No dependencies found")
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