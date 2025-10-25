import argparse
import sys
import os

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

def main():
    try:
        parser = parse_arguments()
        args = parser.parse_args()
        print(f"package: {args.package}")
        print(f"repo: {args.repo}")
        print(f"mode: {args.mode}")
        print(f"version: {args.version}")
        print(f"output file: {args.output}")
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