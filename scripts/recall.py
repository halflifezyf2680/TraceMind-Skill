from __future__ import annotations

import argparse

from _tracemind_db import bootstrap_project, connect, exact_score, expand_fuzzy_keywords, like_filter, like_score, print_rows, project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Recall TraceMind memo history only.")
    parser.add_argument("keywords")
    parser.add_argument("--root", default=".")
    parser.add_argument("--category", default="")
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()

    root = project_root(args.root)
    bootstrap_project(root)

    # SQLite direct query with programmatic cascade
    with connect(root) as conn:
        base_words = args.keywords.split()
        expanded_words = expand_fuzzy_keywords(conn, base_words) if base_words else []
        
        params: list[str | int] = []
        
        # 1. Compute match score
        query = "SELECT *, ("
        if base_words:
            query += exact_score(["content", "entity", "act", "path", "category"], args.keywords, params)
        else:
            query += "0"
        query += ") as exact_match, ("
        if expanded_words:
            query += like_score(["content", "entity", "act", "path", "category"], expanded_words, params)
        else:
            query += "0"
        query += ") as match_score FROM memos WHERE 1=1"
        
        # 2. Filter conditions
        if args.category:
            query += " AND category = ?"
            params.append(args.category)
        query += like_filter(["content", "entity", "act", "path", "category"], expanded_words, params)
        
        # 3. Strict out ordering: exact_match DESC, match_score DESC
        query += " ORDER BY exact_match DESC, match_score DESC, timestamp DESC, id DESC LIMIT ?"
        params.append(args.limit)

        rows = conn.execute(query, params).fetchall()
        
    num_words = len(args.keywords.split())
    if rows and num_words > 0:
        has_exact = any(r['exact_match'] > 0 for r in rows)
        max_score = max((r['match_score'] for r in rows), default=0)

        if has_exact:
            # Keep only exact matches or all-words matches
            rows = [r for r in rows if r['exact_match'] > 0 or r['match_score'] >= num_words]
        elif max_score >= num_words:
            # Keep only all-words matches
            rows = [r for r in rows if r['match_score'] >= num_words]
        # else: keep all (partial match fallback, max 15)
    print_rows(
        "System recall memo history",
        rows,
        lambda r: f"- [{r['id']}] {r['timestamp']} ({r['category']}) {r['entity']} {r['act']}: {r['content']}",
    )


if __name__ == "__main__":
    main()
