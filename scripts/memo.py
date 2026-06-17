from __future__ import annotations

import argparse

from _tracemind_db import (
    append_dev_log_archive,
    bootstrap_project,
    connect,
    like_filter,
    like_score,
    print_rows,
    project_root,
    session_id,
    sync_dev_log,
)


def add(args: argparse.Namespace) -> None:
    root = project_root(args.root)
    bootstrap_project(root)
    
    # SQLite direct write
    sid = session_id()
    with connect(root) as conn:
        conn.execute("INSERT OR IGNORE INTO sessions(id) VALUES (?)", (sid,))
        cur = conn.execute(
            """
            INSERT INTO memos(category, entity, act, path, content, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (args.category, args.entity, args.act, args.path, args.content, sid),
        )
        row = conn.execute("SELECT * FROM memos WHERE id = ?", (cur.lastrowid,)).fetchone()
        dev_log = sync_dev_log(root, conn)
        archive = append_dev_log_archive(root, row)
    print(f"memo recorded: id={cur.lastrowid} session={sid}")
    print(f"dev log synced: {dev_log}")
    print(f"archive appended: {archive}")


def search(args: argparse.Namespace) -> None:
    root = project_root(args.root)
    bootstrap_project(root)
    
    # SQLite filter search with programmatic cascade
    params: list[str | int] = []
    
    # 1. Compute match score
    query = "SELECT *, ("
    if args.keywords.split():
        query += like_score(["content", "entity", "act", "path", "category"], args.keywords.split(), params)
    else:
        query += "0"
    query += ") as match_score FROM memos WHERE 1=1"
    
    # 2. Filter conditions
    if args.category:
        query += " AND category = ?"
        params.append(args.category)
    if args.entity:
        query += " AND entity LIKE ?"
        params.append(f"%{args.entity}%")
    if args.path:
        query += " AND path LIKE ?"
        params.append(f"%{args.path}%")
    query += like_filter(["content", "entity", "act", "path", "category"], args.keywords.split(), params)
    
    # 3. Strict out ordering: match_score DESC
    query += " ORDER BY match_score DESC, timestamp DESC, id DESC LIMIT ?"
    params.append(args.limit)
    with connect(root) as conn:
        rows = conn.execute(query, params).fetchall()
    print_rows(
        "Memo results",
        rows,
        lambda r: f"- [{r['id']}] {r['timestamp']} ({r['category']}) {r['entity']} {r['act']}: {r['content']}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Record or search TraceMind memo timeline events.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_parser = sub.add_parser("add")
    add_parser.add_argument("content")
    add_parser.add_argument("--root", default=".")
    add_parser.add_argument("--category", default="开发")
    add_parser.add_argument("--entity", default="System")
    add_parser.add_argument("--act", default="Manual Entry")
    add_parser.add_argument("--path", default="-")
    add_parser.set_defaults(func=add)

    search_parser = sub.add_parser("search")
    search_parser.add_argument("keywords")
    search_parser.add_argument("--root", default=".")
    search_parser.add_argument("--category", default="")
    search_parser.add_argument("--entity", default="")
    search_parser.add_argument("--path", default="")
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.set_defaults(func=search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
