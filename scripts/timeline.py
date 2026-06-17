from __future__ import annotations

import argparse
import json
import html as html_module
from datetime import datetime
from pathlib import Path

from _tracemind_db import bootstrap_project, connect, escape, project_root

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__PROJECT_NAME__ · TraceMind Timeline</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'sans-serif'], mono: ['JetBrains Mono', 'monospace'] },
                    colors: {
                        slate: { 850: '#1e293b', 950: '#020617' }
                    }
                }
            }
        }
    </script>
    <script>
        // Init Theme
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }
    </script>
    <style>
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        @media (prefers-color-scheme: dark) {
            ::-webkit-scrollbar-thumb { background: #475569; }
        }
        .timeline-line {
            position: absolute; left: 24px; top: 32px; bottom: -24px; width: 2px;
            background: #e2e8f0;
        }
        .dark .timeline-line { background: #334155; }
    </style>
</head>
<body class="bg-gray-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen py-10 px-4 md:px-0 transition-colors duration-300">

    <div class="max-w-3xl mx-auto">
        <!-- Header -->
        <div class="mb-12 px-2">
            <!-- Row 1: Title + Actions -->
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h1 class="text-2xl font-bold tracking-tight">__PROJECT_NAME__</h1>
                    <p class="text-slate-500 dark:text-slate-400 text-sm mt-1">Timeline of decisions and changes in __PROJECT_NAME__</p>
                </div>
                <!-- Actions -->
                <div class="flex items-center gap-2 bg-white dark:bg-slate-900 p-1 rounded-full border border-slate-200 dark:border-slate-800 shadow-sm">
                    <button onclick="window.location.reload()" title="Refresh Data" class="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    </button>
                    <div class="w-px h-4 bg-slate-200 dark:bg-slate-700"></div>
                    <button onclick="toggleTheme()" title="Toggle Theme" class="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
                        <!-- Sun -->
                        <svg class="w-4 h-4 dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                        <!-- Moon -->
                        <svg class="w-4 h-4 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
                    </button>
                </div>
            </div>

            <!-- Row 2: Filters -->
            <div class="flex flex-wrap items-center gap-3">
                <!-- Category Filters -->
                <div id="filters" class="flex flex-wrap items-center gap-2">
                    <button onclick="filterByCategory('all')" id="btn-cat-all" class="cat-btn px-3 py-1 rounded-full text-xs font-bold border border-slate-300 dark:border-slate-700 bg-slate-800 text-white transition-all shadow-sm">
                        ALL
                    </button>
                </div>

                <div class="w-px h-6 bg-slate-200 dark:bg-slate-700"></div>

                <!-- Time Range Filters -->
                <div class="flex items-center gap-2">
                    <button onclick="filterByTime('3d')" id="btn-3d" class="time-btn px-3 py-1 rounded-full text-xs font-bold border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 transition-all shadow-sm opacity-60 hover:opacity-100">
                        3天
                    </button>
                    <button onclick="filterByTime('7d')" id="btn-7d" class="time-btn px-3 py-1 rounded-full text-xs font-bold border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 transition-all shadow-sm opacity-60 hover:opacity-100">
                        7天
                    </button>
                    <button onclick="filterByTime('1m')" id="btn-1m" class="time-btn px-3 py-1 rounded-full text-xs font-bold border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 transition-all shadow-sm opacity-60 hover:opacity-100">
                        一个月
                    </button>
                    <button onclick="filterByTime('all')" id="btn-time-all" class="time-btn px-3 py-1 rounded-full text-xs font-bold border border-slate-300 dark:border-slate-700 bg-slate-800 text-white transition-all shadow-sm">
                        全部
                    </button>
                </div>

                <!-- Search Bar -->
                <input type="text" id="searchInput" placeholder="搜索内容..." oninput="handleSearch(this.value)"
                       class="flex-1 min-w-[140px] px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all">
            </div>
        </div>

        <!-- Timeline Container -->
        <div id="timeline-feed" class="space-y-0 relative">
            <!-- Items injected here -->
        </div>
    </div>

    <script>
        const rawData = __DATA_PLACEHOLDER__;
        rawData.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));

        let currentCategory = 'all';
        let currentTimeRange = 'all';
        let currentSearch = '';

        const palette = {
            '决策': { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-600 dark:text-red-400', border: 'border-red-200 dark:border-red-800', dot: 'bg-red-500', hover: 'hover:bg-red-50 dark:hover:bg-red-900/10' },
            '开发': { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-600 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800', dot: 'bg-blue-500', hover: 'hover:bg-blue-50 dark:hover:bg-blue-900/10' },
            '重构': { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-600 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800', dot: 'bg-amber-500', hover: 'hover:bg-amber-50 dark:hover:bg-amber-900/10' },
            '修复': { bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-600 dark:text-emerald-400', border: 'border-emerald-200 dark:border-emerald-800', dot: 'bg-emerald-500', hover: 'hover:bg-emerald-50 dark:hover:bg-emerald-900/10' },
            '文档': { bg: 'bg-purple-100 dark:bg-purple-900/30', text: 'text-purple-600 dark:text-purple-400', border: 'border-purple-200 dark:border-purple-800', dot: 'bg-purple-500', hover: 'hover:bg-purple-50 dark:hover:bg-purple-900/10' },
            '修改': { bg: 'bg-slate-100 dark:bg-slate-800/50', text: 'text-slate-600 dark:text-slate-400', border: 'border-slate-200 dark:border-slate-700', dot: 'bg-slate-400', hover: 'hover:bg-slate-50 dark:hover:bg-slate-900/10' },
            '调研': { bg: 'bg-teal-100 dark:bg-teal-900/30', text: 'text-teal-600 dark:text-teal-400', border: 'border-teal-200 dark:border-teal-800', dot: 'bg-teal-500', hover: 'hover:bg-teal-50 dark:hover:bg-teal-900/10' },
            '设计': { bg: 'bg-indigo-100 dark:bg-indigo-900/30', text: 'text-indigo-600 dark:text-indigo-400', border: 'border-indigo-200 dark:border-indigo-800', dot: 'bg-indigo-500', hover: 'hover:bg-indigo-50 dark:hover:bg-indigo-900/10' },
            '立项': { bg: 'bg-pink-100 dark:bg-pink-900/30', text: 'text-pink-600 dark:text-pink-400', border: 'border-pink-200 dark:border-pink-800', dot: 'bg-pink-500', hover: 'hover:bg-pink-50 dark:hover:bg-pink-900/10' },
            '测试': { bg: 'bg-cyan-100 dark:bg-cyan-900/30', text: 'text-cyan-600 dark:text-cyan-400', border: 'border-cyan-200 dark:border-cyan-800', dot: 'bg-cyan-500', hover: 'hover:bg-cyan-50 dark:hover:bg-cyan-900/10' },
            '其他': { bg: 'bg-gray-100 dark:bg-gray-800/50', text: 'text-gray-600 dark:text-gray-400', border: 'border-gray-200 dark:border-gray-700', dot: 'bg-gray-400', hover: 'hover:bg-gray-50 dark:hover:bg-gray-900/10' }
        };

        const container = document.getElementById('timeline-feed');
        const filterContainer = document.getElementById('filters');
        const counts = {};

        rawData.forEach(item => {
            let c = item.category;
            if(!palette[c]) c = '其他';
            counts[c] = (counts[c] || 0) + 1;
        });

        Object.keys(palette).forEach(cat => {
            if (!counts[cat]) return;
            const style = palette[cat];
            const btn = document.createElement('button');
            btn.className = "cat-btn px-3 py-1 rounded-full text-xs font-bold border transition-all opacity-60 hover:opacity-100 flex items-center gap-1.5 " + style.border + " " + style.bg + " " + style.text;
            btn.innerHTML = '<span class="w-1.5 h-1.5 rounded-full ' + style.dot + '"></span>' + cat + ' ' + counts[cat];
            btn.onclick = () => filterByCategory(cat, btn);
            filterContainer.appendChild(btn);
        });

        let currentDate = '';
        rawData.forEach((item, index) => {
            let cat = item.category;
            if (!palette[cat]) cat = '其他';
            const style = palette[cat];
            
            const dateObj = new Date(item.timestamp);
            const dateStr = dateObj.toLocaleDateString();
            const timeStr = dateObj.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

            if (dateStr !== currentDate) {
                currentDate = dateStr;
                const dateHeader = document.createElement('div');
                dateHeader.className = "date-header relative pl-14 py-4";
                dateHeader.innerHTML = '<div class="absolute left-6 top-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-slate-200 dark:bg-slate-700 rounded-full border-4 border-white dark:border-slate-950 z-10"></div><span class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono sticky top-4 bg-gray-50 dark:bg-slate-950 px-2 z-20">' + dateStr + '</span>';
                container.appendChild(dateHeader);
            }

            const div = document.createElement('div');
            div.setAttribute('data-category', cat);
            div.setAttribute('data-timestamp', item.timestamp);
            div.setAttribute('data-content', item.content || '');
            div.setAttribute('data-entity', item.entity || '');
            div.setAttribute('data-act', item.act || '');
            div.setAttribute('data-path', item.path || '');
            div.className = "timeline-item relative pl-14 py-3 group hover:bg-white dark:hover:bg-slate-900/50 -mx-4 px-4 rounded-xl transition-colors duration-200";
            div.innerHTML = '<div class="timeline-line group-hover:bg-slate-300 dark:group-hover:bg-slate-600 transition-colors"></div>' +
                '<div class="absolute left-6 top-6 -translate-x-1/2 -translate-y-1/2 w-4 h-4 ' + style.dot + ' rounded-full border-2 border-white dark:border-slate-950 shadow-sm z-10 group-hover:scale-125 transition-transform duration-200"></div>' +
                '<div class="flex flex-col sm:flex-row sm:items-start gap-1 sm:gap-4">' +
                '<div class="min-w-[50px] text-xs font-mono text-slate-400 pt-0.5">' + timeStr + '</div>' +
                '<div class="flex-1">' +
                '<div class="flex items-center gap-2 mb-1 flex-wrap">' +
                '<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border ' + style.bg + ' ' + style.text + ' ' + style.border + '">' + cat + '</span>' +
                '<h3 class="font-bold text-sm text-slate-800 dark:text-slate-100 break-all">' + item.entity + '</h3>' +
                '</div>' +
                '<p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">' + item.content + '</p>' +
                (item.path && item.path !== '-' ? '<div class="mt-1 text-xs text-slate-400 dark:text-slate-500 font-mono">📁 ' + item.path + '</div>' : '') +
                (item.act ? '<div class="mt-1.5 text-xs ' + style.text + ' flex items-center gap-1 opacity-75 font-mono">👉 ' + item.act + '</div>' : '') +
                '</div>' +
                '</div>';
            container.appendChild(div);
        });

        function filterByCategory(targetCat, btnEl) {
            currentCategory = targetCat;
            document.querySelectorAll('.cat-btn').forEach(b => {
                b.classList.add('opacity-60');
                b.classList.remove('ring-2', 'ring-offset-1', 'ring-indigo-500', 'bg-slate-800', 'text-white');
            });

            if (targetCat === 'all') {
                const b = document.getElementById('btn-cat-all');
                b.classList.remove('opacity-60');
                b.classList.add('bg-slate-800', 'text-white');
            } else {
                btnEl.classList.remove('opacity-60');
                btnEl.classList.add('ring-2', 'ring-offset-1', 'ring-indigo-500');
            }
            applyFilters();
        }

        function filterByTime(range) {
            currentTimeRange = range;
            document.querySelectorAll('.time-btn').forEach(b => {
                b.classList.add('opacity-60');
                b.classList.remove('bg-slate-800', 'text-white');
                b.classList.add('bg-white', 'dark:bg-slate-900', 'text-slate-600', 'dark:text-slate-400');
            });

            const activeBtn = document.getElementById(range === 'all' ? 'btn-time-all' : 'btn-' + range);
            activeBtn.classList.remove('opacity-60', 'bg-white', 'dark:bg-slate-900', 'text-slate-600', 'dark:text-slate-400');
            activeBtn.classList.add('bg-slate-800', 'text-white');
            applyFilters();
        }

        function handleSearch(query) {
            currentSearch = query.toLowerCase();
            applyFilters();
        }

        function applyFilters() {
            const now = new Date();
            let cutoffTime = null;

            if (currentTimeRange === '3d') {
                cutoffTime = new Date(now - 3 * 24 * 60 * 60 * 1000);
            } else if (currentTimeRange === '7d') {
                cutoffTime = new Date(now - 7 * 24 * 60 * 60 * 1000);
            } else if (currentTimeRange === '1m') {
                cutoffTime = new Date(now - 30 * 24 * 60 * 60 * 1000);
            }

            const items = document.querySelectorAll('.timeline-item');
            items.forEach(item => {
                const category = item.getAttribute('data-category');
                const timestamp = item.getAttribute('data-timestamp');
                const content = item.getAttribute('data-content');
                const entity = item.getAttribute('data-entity');
                const act = item.getAttribute('data-act');
                const path = item.getAttribute('data-path');

                const categoryMatch = currentCategory === 'all' || category === currentCategory;

                let timeMatch = true;
                if (cutoffTime && timestamp) {
                    timeMatch = new Date(timestamp) >= cutoffTime;
                }

                let searchMatch = true;
                if (currentSearch) {
                    const searchText = (category + ' ' + content + ' ' + entity + ' ' + act + ' ' + path).toLowerCase();
                    searchMatch = searchText.includes(currentSearch);
                }

                item.style.display = (categoryMatch && timeMatch && searchMatch) ? 'block' : 'none';
            });

            document.querySelectorAll('.date-header').forEach(header => {
                let hasVisible = false;
                let next = header.nextElementSibling;
                while(next && !next.classList.contains('date-header')) {
                    if(next.style.display !== 'none') {
                        hasVisible = true;
                        break;
                    }
                    next = next.nextElementSibling;
                }
                header.style.display = hasVisible ? 'block' : 'none';
            });
        }

        function toggleTheme() {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.theme = 'light';
            } else {
                document.documentElement.classList.add('dark');
                localStorage.theme = 'dark';
            }
        }
    </script>
</body>
</html>
"""

def main() -> None:
    parser = argparse.ArgumentParser(description="Render TraceMind memo history as project_timeline.html.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    root = project_root(args.root)
    bootstrap_project(root)

    with connect(root) as conn:
        rows = conn.execute("SELECT * FROM memos ORDER BY timestamp DESC, id DESC LIMIT ?", (args.limit,)).fetchall()

    def normalize_ts(ts: str | None) -> str:
        ts = (ts or '').strip()
        if not ts:
            return '1970-01-01T00:00:00Z'
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'):
            try:
                return datetime.strptime(ts, fmt).isoformat() + 'Z'
            except Exception:
                pass
        return ts

    data = []
    for row in rows:
        d = {
            'id': row['id'],
            'category': row['category'],
            'entity': row['entity'],
            'act': row['act'],
            'path': row['path'],
            'content': row['content'],
            'timestamp': normalize_ts(row['timestamp'])
        }
        data.append(d)

    project_name = html_module.escape(root.name or "Project")
    html_content = HTML_TEMPLATE.replace("__PROJECT_NAME__", project_name)
    html_content = html_content.replace("__DATA_PLACEHOLDER__", json.dumps(data, ensure_ascii=False))

    output = root / "project_timeline.html"
    output.write_text(html_content, encoding="utf-8")
    print(f"timeline generated: {output}")


if __name__ == "__main__":
    main()

