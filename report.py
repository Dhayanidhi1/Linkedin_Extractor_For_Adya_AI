import os
import json
import pandas as pd
from jinja2 import Template
from config import OUTPUT_DIR
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Keyword Intelligence Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --surface2: #1c2230;
            --border: #30363d;
            --accent: #0a84ff;
            --accent2: #6e40c9;
            --text: #e6edf3;
            --text-muted: #8b949e;
            --green: #3fb950;
            --orange: #d29922;
            --red: #f85149;
            --card-shadow: 0 4px 20px rgba(0,0,0,0.4);
            --glow: 0 0 20px rgba(10,132,255,0.15);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }

        /* ── HEADER ── */
        .header {
            background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%);
            border-bottom: 1px solid var(--border);
            padding: 28px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            flex-wrap: wrap;
        }
        .header-brand { display: flex; align-items: center; gap: 14px; }
        .header-logo {
            width: 44px; height: 44px;
            background: linear-gradient(135deg, #0a66c2, #0a84ff);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; font-weight: 800; color: #fff;
            box-shadow: 0 4px 15px rgba(10,102,194,0.5);
        }
        .header-title { font-size: 1.4rem; font-weight: 700; color: var(--text); }
        .header-sub { font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }
        .header-meta {
            font-size: 0.8rem; color: var(--text-muted);
            background: var(--surface);
            padding: 8px 14px; border-radius: 8px;
            border: 1px solid var(--border);
        }
        .header-meta span { color: var(--accent); font-weight: 600; }

        .btn-info {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(10,132,255,0.3);
        }
        .btn-info:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(10,132,255,0.4); opacity: 0.9; }

        .footer-cta {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
            padding: 40px 20px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            margin-top: 60px;
            text-align: center;
        }
        .footer-cta h3 { font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; }
        .footer-cta p { color: var(--text-muted); margin-bottom: 12px; }

        /* ── MAIN LAYOUT ── */
        .main { max-width: 1300px; margin: 0 auto; padding: 32px 24px; }

        /* ── STAT CARDS ── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 22px 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stat-card:hover { transform: translateY(-3px); box-shadow: var(--glow); }
        .stat-card::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
        }
        .stat-icon { font-size: 1.6rem; margin-bottom: 10px; }
        .stat-value { font-size: 2.1rem; font-weight: 800; color: var(--accent); line-height: 1; }
        .stat-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; margin-top: 6px; }

        /* ── SECTION TITLE ── */
        .section-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 16px; flex-wrap: wrap; gap: 12px;
        }
        .section-title {
            font-size: 1.1rem; font-weight: 700;
            display: flex; align-items: center; gap: 8px;
            color: var(--text);
        }
        .section-title::before {
            content: '';
            display: inline-block;
            width: 4px; height: 18px;
            background: linear-gradient(180deg, var(--accent), var(--accent2));
            border-radius: 2px;
        }

        /* ── FILTER CONTROLS ── */
        .controls-row {
            display: flex; align-items: center; gap: 12px;
            flex-wrap: wrap; margin-bottom: 24px;
        }
        .filter-label { font-size: 0.82rem; color: var(--text-muted); font-weight: 500; white-space: nowrap; }
        .day-filters { display: flex; gap: 8px; flex-wrap: wrap; }
        .day-btn {
            padding: 7px 16px;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: var(--surface2);
            color: var(--text-muted);
            font-size: 0.82rem; font-weight: 600;
            cursor: pointer;
            transition: all 0.18s;
            font-family: 'Inter', sans-serif;
        }
        .day-btn:hover { border-color: var(--accent); color: var(--accent); }
        .day-btn.active {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-color: transparent;
            color: #fff;
            box-shadow: 0 2px 12px rgba(10,132,255,0.4);
        }

        .search-wrap { position: relative; flex: 1; min-width: 220px; }
        .search-input {
            width: 100%;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 9px 14px 9px 36px;
            color: var(--text);
            font-size: 0.88rem;
            font-family: 'Inter', sans-serif;
            outline: none;
            transition: border-color 0.2s;
        }
        .search-input:focus { border-color: var(--accent); }
        .search-input::placeholder { color: var(--text-muted); }
        .search-icon {
            position: absolute; left: 11px; top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted); font-size: 0.95rem;
            pointer-events: none;
        }

        .type-filters { display: flex; gap: 8px; flex-wrap: wrap; }
        .type-btn {
            padding: 7px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--surface2);
            color: var(--text-muted);
            font-size: 0.8rem; font-weight: 600;
            cursor: pointer;
            transition: all 0.18s;
            font-family: 'Inter', sans-serif;
        }
        .type-btn:hover, .type-btn.active { border-color: var(--accent); color: var(--accent); background: rgba(10,132,255,0.08); }

        /* ── POST CARDS ── */
        .posts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 16px;
        }
        .post-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
            display: flex; flex-direction: column; gap: 12px;
        }
        .post-card:hover {
            transform: translateY(-3px);
            border-color: rgba(10,132,255,0.4);
            box-shadow: var(--glow);
        }
        .post-card.hidden { display: none; }

        .post-header { display: flex; align-items: flex-start; gap: 12px; }
        .post-avatar {
            width: 40px; height: 40px; border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 1rem; color: #fff;
            flex-shrink: 0;
        }
        .post-author-name {
            font-weight: 600; font-size: 0.92rem; color: var(--text);
            line-height: 1.3;
        }
        .post-date { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }

        .post-content {
            font-size: 0.86rem; color: #cdd9e5;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 5;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .post-content.expanded { -webkit-line-clamp: unset; }

        .post-expand {
            font-size: 0.78rem; color: var(--accent);
            cursor: pointer; font-weight: 600;
            background: none; border: none;
            padding: 0; text-align: left;
            font-family: 'Inter', sans-serif;
        }
        .post-expand:hover { text-decoration: underline; }

        .post-footer {
            display: flex; align-items: center; justify-content: space-between;
            border-top: 1px solid var(--border); padding-top: 12px;
            flex-wrap: wrap; gap: 8px;
        }
        .engagement-stats { display: flex; gap: 14px; }
        .eng-item {
            display: flex; align-items: center; gap: 5px;
            font-size: 0.78rem; color: var(--text-muted);
        }
        .eng-item .icon { font-size: 0.85rem; }

        .post-badges { display: flex; gap: 6px; flex-wrap: wrap; }
        .badge {
            padding: 3px 9px;
            border-radius: 12px;
            font-size: 0.68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.4px;
        }
        .badge-original { background: rgba(63,185,80,0.15); color: var(--green); border: 1px solid rgba(63,185,80,0.3); }
        .badge-repost { background: rgba(210,153,34,0.15); color: var(--orange); border: 1px solid rgba(210,153,34,0.3); }
        .badge-article { background: rgba(110,64,201,0.15); color: #b392f0; border: 1px solid rgba(110,64,201,0.3); }
        .badge-kw {
            background: rgba(10,132,255,0.12);
            color: var(--accent);
            border: 1px solid rgba(10,132,255,0.25);
            font-size: 0.65rem;
        }

        .post-link {
            display: inline-flex; align-items: center; gap: 5px;
            padding: 6px 14px; border-radius: 8px;
            background: rgba(10,132,255,0.1);
            border: 1px solid rgba(10,132,255,0.25);
            color: var(--accent); font-size: 0.78rem; font-weight: 600;
            text-decoration: none; transition: all 0.18s;
        }
        .post-link:hover { background: rgba(10,132,255,0.2); }

        /* ── TOP AUTHORS TABLE ── */
        .authors-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }
        .authors-table th {
            font-size: 0.75rem; color: var(--text-muted);
            text-transform: uppercase; letter-spacing: 0.8px;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            text-align: left; font-weight: 600;
        }
        .authors-table td {
            padding: 12px 14px;
            font-size: 0.87rem; color: var(--text);
            border-bottom: 1px solid rgba(48,54,61,0.5);
        }
        .authors-table tr:hover td { background: var(--surface2); }
        .author-rank {
            font-size: 0.78rem; font-weight: 700;
            color: var(--text-muted); width: 36px;
        }
        .author-bar-wrap { display: flex; align-items: center; gap: 10px; }
        .author-bar {
            height: 6px; border-radius: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            min-width: 4px; transition: width 0.5s ease;
        }
        .author-count {
            font-size: 0.78rem; font-weight: 700;
            color: var(--accent); white-space: nowrap;
        }

        /* ── LAYOUT SECTIONS ── */
        .two-col { display: grid; grid-template-columns: 1fr 1.4fr; gap: 20px; margin-bottom: 28px; }
        @media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 22px;
        }

        /* ── PAGINATION ── */
        .pagination {
            display: flex; align-items: center; justify-content: center;
            gap: 8px; margin-top: 24px; flex-wrap: wrap;
        }
        .page-btn {
            padding: 7px 14px; border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--surface2);
            color: var(--text-muted); font-size: 0.82rem; font-weight: 600;
            cursor: pointer; transition: all 0.18s;
            font-family: 'Inter', sans-serif;
        }
        .page-btn:hover { border-color: var(--accent); color: var(--accent); }
        .page-btn.active { background: var(--accent); border-color: var(--accent); color: #fff; }
        .page-btn:disabled { opacity: 0.3; cursor: not-allowed; }

        /* ── EMPTY STATE ── */
        .empty-state {
            text-align: center; padding: 60px 20px;
            color: var(--text-muted);
        }
        .empty-state .icon { font-size: 3rem; margin-bottom: 12px; }

        /* ── KEYWORD LEGEND ── */
        .kw-legend { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
        .kw-tag {
            padding: 6px 14px; border-radius: 20px;
            background: rgba(10,132,255,0.1);
            border: 1px solid rgba(10,132,255,0.25);
            color: var(--accent); font-size: 0.8rem; font-weight: 600;
        }

        /* ── SORT ── */
        .sort-select {
            padding: 7px 12px;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-muted);
            font-size: 0.82rem;
            font-family: 'Inter', sans-serif;
            cursor: pointer; outline: none;
        }
        .sort-select:focus { border-color: var(--accent); }

        /* ── RESULTS COUNT ── */
        .results-count {
            font-size: 0.82rem; color: var(--text-muted);
            padding: 4px 0;
        }
        .results-count span { color: var(--accent); font-weight: 700; }

        /* ── FOOTER ── */
        .footer {
            text-align: center; padding: 32px;
            border-top: 1px solid var(--border);
            color: var(--text-muted); font-size: 0.8rem;
            margin-top: 40px;
        }
        .footer a { color: var(--accent); text-decoration: none; }
    </style>
</head>
<body>

<div class="header">
    <div class="header-brand">
        <div class="header-logo">in</div>
        <div>
            <div class="header-title">LinkedIn Intelligence Report</div>
            <div class="header-sub">Keyword monitoring dashboard</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <div class="header-meta">
            Generated: <span>{{ date_generated }}</span>
        </div>
        <a href="../index.html" class="btn-info">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            LinkedIn Info
        </a>
    </div>
</div>

<div class="main">

    <!-- KEYWORD TAGS -->
    <div class="kw-legend">
        {% for kw in keywords %}
        <div class="kw-tag">🔍 {{ kw }}</div>
        {% endfor %}
    </div>

    <!-- STAT CARDS -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">📄</div>
            <div class="stat-value">{{ total_posts }}</div>
            <div class="stat-label">Total Posts</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">👤</div>
            <div class="stat-value">{{ unique_authors }}</div>
            <div class="stat-label">Unique Authors</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">❤️</div>
            <div class="stat-value">{{ total_likes }}</div>
            <div class="stat-label">Total Likes</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-value">{{ total_comments }}</div>
            <div class="stat-label">Total Comments</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🔁</div>
            <div class="stat-value">{{ total_reposts }}</div>
            <div class="stat-label">Total Reposts</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-value">{{ total_engagements }}</div>
            <div class="stat-label">Total Engagements</div>
        </div>
    </div>

    <!-- TWO-COL: FILTERS + AUTHORS -->
    <div class="two-col">

        <!-- FILTER CARD -->
        <div class="card">
            <div class="section-title" style="margin-bottom:18px;">🎛️ Filter Posts</div>

            <div style="margin-bottom:14px;">
                <div class="filter-label" style="margin-bottom:8px;">📅 Show Posts From Last</div>
                <div class="day-filters" id="dayFilters">
                    <button class="day-btn active" data-days="all">All Time</button>
                    <button class="day-btn" data-days="1">1 Day</button>
                    <button class="day-btn" data-days="3">3 Days</button>
                    <button class="day-btn" data-days="7">7 Days</button>
                    <button class="day-btn" data-days="14">2 Weeks</button>
                    <button class="day-btn" data-days="30">1 Month</button>
                    <button class="day-btn" data-days="90">3 Months</button>
                    <button class="day-btn" data-days="180">6 Months</button>
                </div>
            </div>

            <div style="margin-bottom:14px;">
                <div class="filter-label" style="margin-bottom:8px;">📂 Post Type</div>
                <div class="type-filters" id="typeFilters">
                    <button class="type-btn active" data-type="all">All</button>
                    <button class="type-btn" data-type="original">Original</button>
                    <button class="type-btn" data-type="repost">Repost</button>
                    <button class="type-btn" data-type="article">Article</button>
                </div>
            </div>

            <div>
                <div class="filter-label" style="margin-bottom:8px;">🗂️ Sort By</div>
                <select class="sort-select" id="sortSelect">
                    <option value="default">Default (Newest First)</option>
                    <option value="likes">Most Liked</option>
                    <option value="comments">Most Comments</option>
                    <option value="reposts">Most Reposts</option>
                    <option value="engagement">Highest Engagement</option>
                </select>
            </div>
        </div>

        <!-- TOP AUTHORS -->
        <div class="card">
            <div class="section-title" style="margin-bottom:16px;">🏆 Top Authors</div>
            <table class="authors-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Author</th>
                        <th>Posts</th>
                    </tr>
                </thead>
                <tbody>
                    {% for author, count in top_authors %}
                    <tr>
                        <td class="author-rank">#{{ loop.index }}</td>
                        <td>
                            <div style="font-weight:600;">{{ author }}</div>
                            <div class="author-bar-wrap" style="margin-top:5px;">
                                <div class="author-bar" style="width:{{ [count * 12, 180] | min }}px"></div>
                            </div>
                        </td>
                        <td><span class="author-count">{{ count }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- POSTS SECTION -->
    <div class="section-header">
        <div class="section-title">📋 Posts</div>
        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <div class="results-count">Showing <span id="visibleCount">{{ total_posts }}</span> of {{ total_posts }} posts</div>
            <div class="search-wrap">
                <span class="search-icon">🔍</span>
                <input type="text" class="search-input" id="searchInput" placeholder="Search posts or authors…">
            </div>
        </div>
    </div>

    <div class="posts-grid" id="postsGrid">
        {% for post in all_posts %}
        <div class="post-card"
             data-days="{{ post.days_old }}"
             data-type="{{ post.post_type }}"
             data-likes="{{ post.likes }}"
             data-comments="{{ post.comments }}"
             data-reposts="{{ post.reposts }}"
             data-engagement="{{ post.likes + post.comments + post.reposts }}"
             data-text="{{ post.post_text | lower }}"
             data-author="{{ post.author_name | lower }}">

            <div class="post-header">
                <div class="post-avatar">{{ post.author_name[0] | upper if post.author_name else '?' }}</div>
                <div>
                    <div class="post-author-name">{{ post.author_name if post.author_name else 'Unknown Author' }}</div>
                    <div class="post-date">{{ post.date_posted }}</div>
                </div>
            </div>

            <div class="post-content" id="content-{{ loop.index }}">{{ post.post_text }}</div>
            <button class="post-expand" onclick="toggleExpand('content-{{ loop.index }}', this)">Show more</button>

            <div class="post-footer">
                <div style="display:flex;flex-direction:column;gap:8px;">
                    <div class="engagement-stats">
                        <div class="eng-item"><span class="icon">❤️</span> {{ post.likes }}</div>
                        <div class="eng-item"><span class="icon">💬</span> {{ post.comments }}</div>
                        <div class="eng-item"><span class="icon">🔁</span> {{ post.reposts }}</div>
                    </div>
                    <div class="post-badges">
                        <span class="badge badge-{{ post.post_type }}">{{ post.post_type }}</span>
                        {% for kw in post.matched_keywords %}
                        <span class="badge badge-kw">{{ kw }}</span>
                        {% endfor %}
                    </div>
                </div>
                {% if post.post_url %}
                <a href="{{ post.post_url }}" target="_blank" class="post-link">↗ View</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="emptyState" class="empty-state" style="display:none;">
        <div class="icon">🔎</div>
        <div>No posts match your current filters.</div>
        <div style="margin-top:8px; font-size:0.82rem;">Try adjusting the date range or search term.</div>
    </div>

    <div class="pagination" id="pagination"></div>

    <div class="footer-cta">
        <h3>LinkedIn Tracker Information</h3>
        <p>Curious about how this project works or want to know more about the developer?</p>
        <a href="../landing_page.html" class="btn-info" style="padding: 12px 28px; font-size: 1rem; border-radius: 12px;">
            View Project Details & Developer Info
        </a>
    </div>

</div>

<div class="footer">
    LinkedIn Intelligence Report &mdash; Generated by <a href="#">LinkedIn Scraper</a> &bull; {{ date_generated }}
</div>

<script>
    // ── DATA ──
    const POSTS_PER_PAGE = 30;
    let currentPage = 1;
    let activeDay = 'all';
    let activeType = 'all';
    let sortBy = 'default';
    let searchTerm = '';

    // ── DOM ──
    const grid = document.getElementById('postsGrid');
    const allCards = [...grid.querySelectorAll('.post-card')];
    const emptyState = document.getElementById('emptyState');
    const visibleCount = document.getElementById('visibleCount');

    // Assign original indices for stable sort
    allCards.forEach((c, i) => c.dataset.origIndex = i);

    function applyFilters() {
        const filtered = allCards.filter(card => {
            const days = card.dataset.days;
            const type = card.dataset.type;
            const text = card.dataset.text;
            const author = card.dataset.author;

            if (activeDay !== 'all') {
                if (days === 'unknown') return false;
                if (parseInt(days) > parseInt(activeDay)) return false;
            }
            if (activeType !== 'all' && type !== activeType) return false;
            if (searchTerm && !text.includes(searchTerm) && !author.includes(searchTerm)) return false;
            return true;
        });

        // Sort
        filtered.sort((a, b) => {
            if (sortBy === 'likes') return parseInt(b.dataset.likes) - parseInt(a.dataset.likes);
            if (sortBy === 'comments') return parseInt(b.dataset.comments) - parseInt(a.dataset.comments);
            if (sortBy === 'reposts') return parseInt(b.dataset.reposts) - parseInt(a.dataset.reposts);
            if (sortBy === 'engagement') return parseInt(b.dataset.engagement) - parseInt(a.dataset.engagement);
            return parseInt(a.dataset.origIndex) - parseInt(b.dataset.origIndex);
        });

        // Pagination
        const totalPages = Math.ceil(filtered.length / POSTS_PER_PAGE);
        if (currentPage > totalPages) currentPage = 1;

        const pageStart = (currentPage - 1) * POSTS_PER_PAGE;
        const pageCards = filtered.slice(pageStart, pageStart + POSTS_PER_PAGE);

        // Show/hide
        allCards.forEach(c => { c.classList.add('hidden'); grid.appendChild(c); });
        pageCards.forEach(c => { c.classList.remove('hidden'); grid.appendChild(c); });

        visibleCount.textContent = filtered.length;
        emptyState.style.display = filtered.length === 0 ? 'block' : 'none';

        renderPagination(totalPages);
    }

    function renderPagination(totalPages) {
        const container = document.getElementById('pagination');
        container.innerHTML = '';
        if (totalPages <= 1) return;

        const makeBtn = (label, page, disabled = false, active = false) => {
            const btn = document.createElement('button');
            btn.className = 'page-btn' + (active ? ' active' : '');
            btn.textContent = label;
            btn.disabled = disabled;
            btn.onclick = () => { currentPage = page; applyFilters(); window.scrollTo({top: 0, behavior: 'smooth'}); };
            return btn;
        };

        container.appendChild(makeBtn('‹ Prev', currentPage - 1, currentPage === 1));

        const start = Math.max(1, currentPage - 2);
        const end = Math.min(totalPages, currentPage + 2);
        for (let p = start; p <= end; p++) {
            container.appendChild(makeBtn(p, p, false, p === currentPage));
        }

        container.appendChild(makeBtn('Next ›', currentPage + 1, currentPage === totalPages));
    }

    // ── DAY FILTER ──
    document.getElementById('dayFilters').querySelectorAll('.day-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeDay = btn.dataset.days;
            currentPage = 1;
            applyFilters();
        });
    });

    // ── TYPE FILTER ──
    document.getElementById('typeFilters').querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeType = btn.dataset.type;
            currentPage = 1;
            applyFilters();
        });
    });

    // ── SORT ──
    document.getElementById('sortSelect').addEventListener('change', e => {
        sortBy = e.target.value;
        currentPage = 1;
        applyFilters();
    });

    // ── SEARCH ──
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', e => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchTerm = e.target.value.toLowerCase().trim();
            currentPage = 1;
            applyFilters();
        }, 250);
    });

    // ── EXPAND ──
    function toggleExpand(id, btn) {
        const el = document.getElementById(id);
        el.classList.toggle('expanded');
        btn.textContent = el.classList.contains('expanded') ? 'Show less' : 'Show more';
    }

    // ── INIT ──
    applyFilters();
</script>

</body>
</html>
"""

def parse_days_old(date_str):
    """Convert LinkedIn relative date strings like '1d', '2w', '3mo' to number of days."""
    if not date_str:
        return 9999
    date_str = str(date_str).strip().lower()
    import re
    # Try patterns like "1d", "2w", "3mo", "1 day ago", "2 weeks ago"
    patterns = [
        (r'(\d+)\s*d', 1),
        (r'(\d+)\s*w', 7),
        (r'(\d+)\s*mo', 30),
        (r'(\d+)\s*m(?!o)', 30),
        (r'(\d+)\s*y', 365),
        (r'(\d+)\s*h', 0),
        (r'(\d+)\s*hr', 0),
        (r'just now|now|today', None),
    ]
    for pattern, mult in patterns:
        if pattern.startswith('just'):
            if re.search(pattern, date_str):
                return 0
        else:
            m = re.search(pattern, date_str)
            if m and mult is not None:
                return int(m.group(1)) * mult
            elif m and mult == 0:
                return 0
    return 9999  # unknown

def generate_report(json_path):
    if not os.path.exists(json_path):
        print("[REPORT] JSON file not found. Cannot generate report.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
        df = pd.DataFrame(posts_data)
    except Exception as e:
        print(f"[REPORT] Failed to load JSON: {e}")
        return

    if df.empty:
        print("[REPORT] Dataset is empty.")
        return

    for col in ['likes', 'comments', 'reposts']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Fix doubled author names (e.g., "John DoeJohn Doe" → "John Doe")
    def fix_author(name):
        if not name:
            return ''
        name = str(name).strip()
        half = len(name) // 2
        if len(name) % 2 == 0 and name[:half] == name[half:]:
            return name[:half]
        return name

    if 'author_name' in df.columns:
        df['author_name'] = df['author_name'].apply(fix_author)

    # Compute days_old
    if 'date_posted' in df.columns:
        df['days_old'] = df['date_posted'].apply(parse_days_old)
    else:
        df['days_old'] = 9999

    # Replace 9999 with "unknown" for template
    df['days_old_str'] = df['days_old'].apply(lambda x: 'unknown' if x == 9999 else x)

    # Extract matched_keywords list safely
    def safe_kw(v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return [v] if v else []
        return []

    if 'matched_keywords' in df.columns:
        df['matched_keywords'] = df['matched_keywords'].apply(safe_kw)
    else:
        df['matched_keywords'] = [[]] * len(df)

    # Stats
    total_posts = len(df)
    unique_authors = df['author_name'].nunique()
    total_likes = int(df['likes'].sum())
    total_comments = int(df['comments'].sum())
    total_reposts = int(df['reposts'].sum())
    total_engagements = total_likes + total_comments + total_reposts

    top_authors = df['author_name'].value_counts().head(10)
    top_authors_list = [(auth, cnt) for auth, cnt in top_authors.items() if auth]

    # Collect all unique keywords seen
    all_kws = set()
    for kws in df['matched_keywords']:
        for k in kws:
            all_kws.add(k)
    keywords = sorted(all_kws) or ['Shayak Mazumder', 'Adya AI']

    # Build posts for template
    all_posts = []
    for _, row in df.iterrows():
        all_posts.append({
            'author_name': row.get('author_name', ''),
            'author_profile_url': row.get('author_profile_url', ''),
            'post_text': row.get('post_text', ''),
            'date_posted': row.get('date_posted', ''),
            'days_old': row.get('days_old_str', 'unknown'),
            'likes': int(row.get('likes', 0)),
            'comments': int(row.get('comments', 0)),
            'reposts': int(row.get('reposts', 0)),
            'post_url': row.get('post_url', ''),
            'post_type': row.get('post_type', 'original'),
            'matched_keywords': row.get('matched_keywords', []),
        })

    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        date_generated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_posts=total_posts,
        unique_authors=unique_authors,
        total_likes=total_likes,
        total_comments=total_comments,
        total_reposts=total_reposts,
        total_engagements=total_engagements,
        top_authors=top_authors_list,
        all_posts=all_posts,
        keywords=keywords,
    )

    report_path = os.path.join(OUTPUT_DIR, "linkedin_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[REPORT] HTML Report generated: {report_path}")
