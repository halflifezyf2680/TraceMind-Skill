from __future__ import annotations

import argparse
import time

from _tracemind_db import bootstrap_project, connect, print_rows, project_root


def create(args: argparse.Namespace) -> None:
    suffix = f"{time.time_ns() & 0xfffff:x}"
    hook_id = f"hook_{suffix}"
    expires_at = None
    if args.expires_in_hours > 0:
        expires_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + args.expires_in_hours * 3600))
    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        conn.execute(
            """
            INSERT INTO pending_hooks(hook_id, description, priority, tag, status, related_task_id, expires_at, summary)
            VALUES (?, ?, ?, ?, 'open', ?, ?, ?)
            """,
            (hook_id, args.description, args.priority, args.tag, args.task_id, expires_at, f"#{suffix}"),
        )
    print(f"task hook created: {hook_id}")
    print(f"description: {args.description}")


def list_hooks(args: argparse.Namespace) -> None:
    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        rows = conn.execute(
            "SELECT * FROM pending_hooks WHERE status = ? ORDER BY created_at DESC",
            (args.status,),
        ).fetchall()
    print_rows(
        f"Task hooks {args.status}",
        rows,
        lambda r: f"- {r['hook_id']} [{r['priority']}] {r['description']} result={r['result_summary'] or ''}",
    )


def release(args: argparse.Namespace) -> None:
    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        conn.execute(
            "UPDATE pending_hooks SET status = 'closed', result_summary = ? WHERE hook_id = ?",
            (args.result_summary, args.hook_id),
        )
    print(f"task hook released: {args.hook_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create, list, or release TraceMind task hooks.")
    sub = parser.add_subparsers(dest="command", required=True)

    create_parser = sub.add_parser("create")
    create_parser.add_argument("description")
    create_parser.add_argument("--root", default=".")
    create_parser.add_argument("--priority", default="medium", choices=["high", "medium", "low"])
    create_parser.add_argument("--tag", default="")
    create_parser.add_argument("--task-id", default="")
    create_parser.add_argument("--expires-in-hours", type=int, default=0)
    create_parser.set_defaults(func=create)

    list_parser = sub.add_parser("list")
    list_parser.add_argument("--root", default=".")
    list_parser.add_argument("--status", default="open", choices=["open", "closed"])
    list_parser.set_defaults(func=list_hooks)

    release_parser = sub.add_parser("release")
    release_parser.add_argument("hook_id")
    release_parser.add_argument("--root", default=".")
    release_parser.add_argument("--result-summary", default="")
    release_parser.set_defaults(func=release)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
