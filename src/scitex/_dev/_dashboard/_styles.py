#!/usr/bin/env python3
# Timestamp: 2026-02-02
# File: scitex/_dev/_dashboard/_styles.py

"""CSS styles for the dashboard."""


def get_css() -> str:
    """Return dashboard CSS."""
    return """
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    --text-primary: #eee;
    --text-secondary: #aaa;
    --accent: #e94560;
    --success: #4ade80;
    --warning: #fbbf24;
    --error: #f87171;
    --info: #60a5fa;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    padding: 20px;
}
.container { max-width: 1400px; margin: 0 auto; }
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding: 20px;
    background: var(--bg-secondary);
    border-radius: 10px;
}
h1 { font-size: 1.8rem; color: var(--accent); }
.actions { display: flex; gap: 10px; }
button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}
.btn-primary { background: var(--accent); color: white; }
.btn-primary:hover { background: #c9184a; }
.btn-secondary { background: var(--bg-card); color: var(--text-primary); }
.btn-secondary:hover { background: #1a4d80; }
.filters {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
    padding: 20px;
    background: var(--bg-secondary);
    border-radius: 10px;
}
.filter-group { display: flex; flex-direction: column; gap: 10px; }
.filter-group h3 {
    font-size: 0.9rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
}
.filter-options { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-options label {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 10px;
    background: var(--bg-card);
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}
.filter-options label:hover { background: #1a4d80; }
.filter-options input[type="checkbox"],
.filter-options input[type="radio"] { accent-color: var(--accent); }
.summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}
.summary-card {
    padding: 20px;
    background: var(--bg-secondary);
    border-radius: 10px;
    text-align: center;
}
.summary-card .number { font-size: 2rem; font-weight: bold; }
.summary-card .label { font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px; }
.summary-card.ok .number { color: var(--success); }
.summary-card.unreleased .number { color: var(--warning); }
.summary-card.mismatch .number { color: var(--error); }
.summary-card.total .number { color: var(--info); }
.packages { display: grid; gap: 20px; }
.package-card { background: var(--bg-secondary); border-radius: 10px; overflow: hidden; }
.package-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: var(--bg-card);
}
.package-name { font-size: 1.1rem; font-weight: bold; }
.status-badge {
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
}
.status-ok { background: rgba(74, 222, 128, 0.2); color: var(--success); }
.status-unreleased { background: rgba(251, 191, 36, 0.2); color: var(--warning); }
.status-mismatch { background: rgba(248, 113, 113, 0.2); color: var(--error); }
.status-outdated { background: rgba(167, 139, 250, 0.2); color: #a78bfa; }
.status-unavailable { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }
.status-error { background: rgba(248, 113, 113, 0.2); color: var(--error); }
.package-body { padding: 20px; }
.version-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}
.version-section { padding: 10px; background: var(--bg-primary); border-radius: 5px; }
.version-section h4 {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-bottom: 8px;
    text-transform: uppercase;
}
.host-ip {
    font-size: 0.7rem;
    color: var(--text-secondary);
    opacity: 0.7;
    font-weight: normal;
    text-transform: none;
}
.version-item { display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.9rem; }
.version-item .key { color: var(--text-secondary); }
.version-item .value { font-family: monospace; }
.issues {
    margin-top: 15px;
    padding: 10px;
    background: rgba(248, 113, 113, 0.1);
    border-radius: 5px;
    border-left: 3px solid var(--error);
}
.issues h4 { font-size: 0.8rem; color: var(--error); margin-bottom: 5px; }
.issues ul { list-style: none; font-size: 0.85rem; color: var(--text-secondary); }
.issues li::before { content: "!"; margin-right: 8px; color: var(--error); }
.loading {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--bg-secondary);
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    z-index: 1000;
}
.loading.active { display: block; }
.spinner {
    border: 4px solid var(--bg-card);
    border-top: 4px solid var(--accent);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
}
.overlay.active { display: block; }
.last-updated { font-size: 0.8rem; color: var(--text-secondary); }
.loading-section { opacity: 0.5; position: relative; }
.loading-section::after {
    content: "⟳";
    position: absolute;
    right: 5px;
    top: -20px;
    font-size: 1rem;
    animation: spin 1s linear infinite;
    color: var(--accent);
}
.just-updated {
    animation: flash-green 0.5s ease;
}
@keyframes flash-green {
    0% { background: rgba(74, 222, 128, 0.3); }
    100% { background: transparent; }
}
.rtd-passing { color: var(--success); }
.rtd-failing { color: var(--error); }
.rtd-unknown { color: var(--warning); }
.rtd-passing a, .rtd-failing a, .rtd-unknown a {
    color: inherit;
    text-decoration: none;
}
.rtd-passing a:hover, .rtd-failing a:hover, .rtd-unknown a:hover {
    text-decoration: underline;
}
/* Collapsible cards */
.package-card .package-header {
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}
.package-card .fold-icon {
    transition: transform 0.2s ease;
    font-size: 0.8rem;
    color: var(--text-secondary);
}
.package-card:not(.collapsed) .fold-icon {
    transform: rotate(90deg);
}
.package-card.collapsed .package-body {
    display: none;
}
.package-card .package-name {
    color: var(--accent);
    text-decoration: none;
    font-weight: bold;
}
.package-card .package-name:hover {
    text-decoration: underline;
}
.package-card .quick-links {
    margin-left: auto;
    display: flex;
    gap: 8px;
    font-size: 1rem;
}
.package-card .quick-links a {
    text-decoration: none;
    opacity: 0.7;
    transition: opacity 0.2s;
}
.package-card .quick-links a:hover {
    opacity: 1;
}
/* Collapsible filters */
.filters.collapsed .filter-group {
    display: none;
}
.filters-toggle {
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px;
    margin: -20px -20px 15px -20px;
    background: var(--bg-card);
    border-radius: 10px 10px 0 0;
    color: var(--text-secondary);
    font-size: 0.9rem;
}
.filters-toggle .fold-icon {
    transition: transform 0.2s ease;
}
.filters:not(.collapsed) .filters-toggle .fold-icon {
    transform: rotate(90deg);
}
.expand-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}
.expand-controls button {
    padding: 5px 12px;
    font-size: 0.8rem;
}
/* Section header links */
.version-section h4 a {
    color: var(--text-secondary);
    text-decoration: none;
}
.version-section h4 a:hover {
    color: var(--accent);
    text-decoration: underline;
}
/* Source mini-badges */
.source-badges {
    display: flex;
    gap: 4px;
    margin-left: 8px;
}
.source-badge {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 0.6rem;
    font-weight: bold;
    opacity: 0.9;
}
.source-badge.src-ok { background: rgba(74, 222, 128, 0.25); color: var(--success); }
.source-badge.src-warn { background: rgba(251, 191, 36, 0.25); color: var(--warning); }
.source-badge.src-error { background: rgba(248, 113, 113, 0.25); color: var(--error); }
.source-badge.src-loading { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }
.source-badge.src-na { background: rgba(156, 163, 175, 0.15); color: #6b7280; }
/* Loading indicator in cells */
.loading-cell {
    opacity: 0.6;
}
.loading-cell .value {
    color: var(--text-secondary);
    font-style: italic;
}
/* Worktree status indicators */
.wt-clean { color: var(--success); font-weight: bold; }
.wt-dirty { color: var(--error); font-weight: bold; }
.wt-ahead { color: var(--warning); }
.wt-behind { color: var(--error); }
"""


# EOF
