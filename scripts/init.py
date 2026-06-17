from __future__ import annotations

import argparse

from _tracemind_db import bootstrap_project, connect, db_path, project_root, sync_dev_log


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize TraceMind storage in the current project.")
    parser.add_argument("--root", default=".", help="Project root. Default: current directory.")
    args = parser.parse_args()

    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        dev_log_path = sync_dev_log(root, conn)
    print(f"TraceMind initialized: {root}")
    print(f"Database: {db_path(root)}")
    print(f"Dev log: {dev_log_path}")

if __name__ == "__main__":
    main()
