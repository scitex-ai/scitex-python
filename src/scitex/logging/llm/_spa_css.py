#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_spa_css.py

"""CSS for the Claude Code Sessions SPA."""

from __future__ import annotations

CSS = """\
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,monospace;
  background:#0d1117;color:#c9d1d9;min-height:100vh}
a{color:#58a6ff;text-decoration:none}
a:hover{text-decoration:underline}
#chrome{position:sticky;top:0;z-index:100;background:#0d1117;border-bottom:1px solid #21262d}
#topbar{display:flex;justify-content:space-between;align-items:center;padding:12px 24px}
.logo{color:#58a6ff;font-size:1.2em;font-weight:700}
#topbar-right{display:flex;gap:8px;align-items:center}
#search{background:#161b22;border:1px solid #30363d;color:#c9d1d9;padding:6px 12px;
  border-radius:6px;font-size:0.85em;width:200px}
#breadcrumb{padding:4px 24px 8px;font-size:0.8em;color:#8b949e}
#breadcrumb a{color:#8b949e}
#breadcrumb .sep{margin:0 6px}
#app{padding:24px;max-width:1000px;margin:0 auto}
.btn{padding:6px 14px;border-radius:6px;border:1px solid #30363d;background:#21262d;
  color:#c9d1d9;font-size:0.8em;cursor:pointer;font-family:inherit}
.btn:hover{background:#30363d}
.btn-primary{border-color:#58a6ff;color:#58a6ff}
.btn-primary:hover{background:#0d2847}
.btn-sm{padding:3px 8px;font-size:0.75em}
.stats-bar{display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap}
.stat{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:10px 14px}
.stat-label{color:#8b949e;font-size:0.7em}
.stat-value{font-size:1.2em;font-weight:700}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px 18px;
  margin-bottom:10px;cursor:pointer;transition:border-color 0.15s}
.card:hover{border-color:#58a6ff}
.card-title{font-weight:600;margin-bottom:4px}
.card-meta{color:#8b949e;font-size:0.8em}
.card-right{display:flex;gap:8px;align-items:center}
.badge{padding:2px 8px;border-radius:10px;font-size:0.7em;font-weight:600}
.badge-blue{background:#1f3a5f;color:#58a6ff}
.badge-yellow{background:#2a1f0b;color:#d29922}
.badge-green{background:#0d2818;color:#3fb950}
.row{display:flex;justify-content:space-between;align-items:center}
.session-row{background:#161b22;border:1px solid #30363d;border-radius:8px;
  padding:12px 16px;margin-bottom:8px}
.session-row:hover{border-color:#58a6ff}
.chat-entry{margin-bottom:14px;max-width:85%}
.chat-user{margin-left:auto;background:#0d2847;border:1px solid #1f3a5f;
  border-radius:12px 12px 4px 12px;padding:10px 14px}
.chat-assistant{background:#161b22;border:1px solid #30363d;
  border-radius:12px 12px 12px 4px;padding:10px 14px}
.chat-system{background:#1a1206;border:1px solid #3d2e0a;border-radius:8px;
  padding:8px 12px;font-size:0.85em;max-width:100%;margin:0 auto}
.chat-role{font-size:0.7em;font-weight:600;text-transform:uppercase;margin-bottom:4px}
.chat-role-user{color:#58a6ff}
.chat-role-assistant{color:#8b949e}
.chat-role-system{color:#d29922}
.chat-text{white-space:pre-wrap;word-break:break-word;line-height:1.5;font-size:0.9em}
.tool-card{background:#1c2128;border:1px solid #30363d;border-radius:6px;margin:8px 0;
  overflow:hidden}
.tool-header{padding:6px 10px;background:#21262d;cursor:pointer;font-size:0.8em;
  display:flex;justify-content:space-between;align-items:center}
.tool-header:hover{background:#282e36}
.tool-name{color:#f0883e;font-weight:600}
.tool-body{display:none;padding:8px 10px;font-size:0.75em}
.tool-body.open{display:block}
.tool-body pre{background:#0d1117;padding:6px;border-radius:4px;overflow-x:auto;
  white-space:pre-wrap;word-break:break-word}
.tool-result-card{background:#0d2818;border:1px solid #238636;border-radius:6px;
  margin:8px 0;padding:8px 10px;font-size:0.8em}
.tool-result-card pre{white-space:pre-wrap;word-break:break-word}
.tool-result-label{color:#3fb950;font-weight:600;font-size:0.75em;margin-bottom:2px}
.action-row{background:#161b22;border:1px solid #30363d;border-radius:8px;
  margin-bottom:8px;overflow:hidden}
.action-header{padding:10px 14px;display:flex;justify-content:space-between;
  align-items:center;cursor:pointer}
.action-header:hover{background:#1c2128}
.action-left{display:flex;gap:10px;align-items:center;flex:1;min-width:0}
.action-idx{color:#8b949e;font-size:0.75em;min-width:30px}
.action-tool{color:#f0883e;font-weight:600;font-size:0.85em;min-width:60px}
.action-desc{color:#c9d1d9;font-size:0.8em;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;flex:1}
.action-body{display:none;border-top:1px solid #21262d;padding:10px 14px}
.action-body.open{display:block}
.action-body pre{background:#0d1117;padding:8px;border-radius:4px;overflow-x:auto;
  white-space:pre-wrap;word-break:break-word;font-size:0.8em}
.output-block{background:#0d2818;border-left:3px solid #238636;padding:8px;
  border-radius:0 4px 4px 0;margin:4px 0}
.error-block{background:#2d1117;border-left:3px solid #da3633;padding:8px;
  border-radius:0 4px 4px 0;margin:4px 0}
.filter-bar{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}
.filter-btn{padding:4px 12px;border-radius:14px;border:1px solid #30363d;background:#161b22;
  color:#8b949e;cursor:pointer;font-size:0.75em}
.filter-btn.active{border-color:#58a6ff;color:#58a6ff;background:#0d2847}
.toast{position:fixed;bottom:24px;right:24px;background:#238636;color:#fff;padding:10px 18px;
  border-radius:8px;font-size:0.85em;display:none;z-index:200}
.empty{text-align:center;color:#8b949e;padding:40px}
.hidden{display:none!important}
"""

# EOF
