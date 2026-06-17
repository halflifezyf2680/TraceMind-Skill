from __future__ import annotations

import argparse

from _tracemind_db import (
    bootstrap_project,
    add_context_args,
    connect,
    context_from_args,
    json_payload,
    like_filter,
    like_score,
    now_text,
    print_rows,
    project_root,
    sync_trace_mind_facts,
)


def add(args: argparse.Namespace) -> None:
    ctx = context_from_args(args)
    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        cur = conn.execute(
            """
            INSERT INTO known_facts(type, summarize, scope, keywords, confidence, status, source_type, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (args.type, args.fact, ctx.scope(), ctx.keywords(), 0.45, "candidate", "manual", ctx.task_id),
        )
    print(f"known fact recorded: id={cur.lastrowid} type={args.type}")


def status(args: argparse.Namespace) -> None:
    root = project_root(args.root)
    bootstrap_project(root)
    params: list[str | int] = []
    
    query = "SELECT *, ("
    if args.keywords.split():
        query += like_score(["type", "summarize", "scope", "keywords"], args.keywords.split(), params)
    else:
        query += "0"
    query += ") as match_score FROM known_facts WHERE status != 'archived'"
    
    query += like_filter(["type", "summarize", "scope", "keywords"], args.keywords.split(), params)
    query += " ORDER BY match_score DESC, confidence DESC, updated_at DESC LIMIT ?"
    params.append(args.limit)
    with connect(root) as conn:
        rows = conn.execute(query, params).fetchall()
    print_rows(
        "Known facts",
        rows,
        lambda r: f"- [{r['id']}] {r['status']} conf={r['confidence']:.2f} {r['type']}: {r['summarize']}",
    )


def before(args: argparse.Namespace) -> None:
    ctx = context_from_args(args)
    root = project_root(args.root)
    bootstrap_project(root)
    params: list[str | int] = []
    
    query = "SELECT *, ("
    if ctx.keywords().split():
        query += like_score(["type", "summarize", "scope", "keywords"], ctx.keywords().split(), params)
    else:
        query += "0"
    query += ") as match_score FROM known_facts WHERE status NOT IN ('rejected', 'archived', 'superseded')"
    
    query += like_filter(["type", "summarize", "scope", "keywords"], ctx.keywords().split(), params)
    query += " ORDER BY match_score DESC, confidence DESC, updated_at DESC LIMIT ?"
    params.append(args.limit)
    with connect(root) as conn:
        rows = conn.execute(query, params).fetchall()
        for row in rows:
            conn.execute("UPDATE known_facts SET hit_count = hit_count + 1, updated_at = ? WHERE id = ?", (now_text(), row["id"]))
            conn.execute(
                """
                INSERT INTO known_fact_events(event_type, fact_id, task_id, phase, context_signature, payload_json)
                VALUES ('exposure', ?, ?, ?, ?, ?)
                """,
                (row["id"], ctx.task_id, ctx.phase, ctx.keywords()[:240], json_payload({"mode": "before_action"})),
            )
    print_rows(
        "Relevant known facts",
        rows,
        lambda r: f"- [fact_id={r['id']} confidence={r['confidence']:.2f}] {r['summarize']}",
    )
    if not rows:
        print("Strategy: no matching fact; add reusable observations after the action.")
    else:
        print("Strategy: follow relevant facts, then run remember.py after-action.")


def apply_outcome(conn, fact_id: int, adopted: bool, result: str) -> None:
    if adopted and result == "success":
        conn.execute(
            """
            UPDATE known_facts
            SET confidence = confidence + (0.40 * (1.0 - confidence)),
                support_count = support_count + 1,
                adopt_count = adopt_count + 1,
                updated_at = ?
            WHERE id = ?
            """,
            (now_text(), fact_id),
        )
    else:
        conn.execute(
            """
            UPDATE known_facts
            SET confidence = confidence - (0.20 * confidence),
                reject_count = reject_count + 1,
                adopt_count = adopt_count + 1,
                updated_at = ?
            WHERE id = ?
            """,
            (now_text(), fact_id),
        )


def after(args: argparse.Namespace) -> None:
    ctx = context_from_args(args)
    result = args.result.lower()
    adopted = [int(x) for x in args.adopted.split(",") if x.strip()]
    rejected = [int(x) for x in args.rejected.split(",") if x.strip()]
    observations = [x.strip() for x in args.observe.split("||") if x.strip()]
    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        for fact_id in adopted:
            apply_outcome(conn, fact_id, True, result)
        for fact_id in rejected:
            apply_outcome(conn, fact_id, False, "corrected")
        for obs in observations:
            fact_type = "pitfall" if result in {"failure", "corrected"} else "success_pattern"
            conn.execute(
                """
                INSERT INTO known_facts(type, summarize, scope, keywords, confidence, status, source_type, source_id)
                VALUES (?, ?, ?, ?, ?, 'candidate', 'observation', ?)
                """,
                (fact_type, obs, ctx.scope(), ctx.keywords(), 0.45, ctx.task_id),
            )
        synced_rules = sync_trace_mind_facts(root, conn)
    print(f"known fact outcome updated: adopted={len(adopted)} rejected={len(rejected)} observations={len(observations)}")
    print(f"rules synced: {synced_rules}")


def maintain(args: argparse.Namespace) -> None:
    root = project_root(args.root)
    bootstrap_project(root)
    with connect(root) as conn:
        rows = conn.execute("SELECT status, COUNT(*) AS count FROM known_facts GROUP BY status ORDER BY status").fetchall()
    print_rows("Known fact maintenance snapshot", rows, lambda r: f"- {r['status']}: {r['count']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Remember or evolve reusable TraceMind known facts.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_parser = sub.add_parser("add")
    add_parser.add_argument("fact")
    add_parser.add_argument("--root", default=".")
    add_parser.add_argument("--type", default="rule")
    add_context_args(add_parser)
    add_parser.set_defaults(func=add)

    before_parser = sub.add_parser("before-action")
    before_parser.add_argument("--root", default=".")
    before_parser.add_argument("--limit", type=int, default=3)
    add_context_args(before_parser)
    before_parser.set_defaults(func=before)

    after_parser = sub.add_parser("after-action")
    after_parser.add_argument("--root", default=".")
    after_parser.add_argument("--result", default="neutral", choices=["success", "failure", "corrected", "neutral"])
    after_parser.add_argument("--adopted", default="", help="Comma-separated fact IDs.")
    after_parser.add_argument("--rejected", default="", help="Comma-separated fact IDs.")
    after_parser.add_argument("--observe", default="", help="Reusable observations separated by ||.")
    add_context_args(after_parser)
    after_parser.set_defaults(func=after)

    status_parser = sub.add_parser("status")
    status_parser.add_argument("keywords", nargs="?", default="")
    status_parser.add_argument("--root", default=".")
    status_parser.add_argument("--limit", type=int, default=10)
    status_parser.set_defaults(func=status)

    maintain_parser = sub.add_parser("maintain")
    maintain_parser.add_argument("--root", default=".")
    maintain_parser.set_defaults(func=maintain)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
