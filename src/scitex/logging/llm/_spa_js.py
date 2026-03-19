#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_spa_js.py

"""JavaScript for the Claude Code Sessions SPA."""

from __future__ import annotations

JS = r"""
const DATA = JSON.parse(document.getElementById('app-data').textContent);
const app = document.getElementById('app');
const bc = document.getElementById('breadcrumb');
let currentFilter = 'all';

function esc(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = String(s);
  return d.innerHTML;
}
function fmtTok(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
  return String(n);
}
function fmtDate(iso) {
  if (!iso) return '';
  return String(iso).slice(0, 16).replace('T', ' ');
}
function shortPath(p) {
  const parts = p.split('/');
  if (parts.length > 3) return '.../' + parts.slice(-2).join('/');
  return p;
}
function toast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 2000);
}
function copyText(text) {
  navigator.clipboard.writeText(text).then(() => toast('Copied!')).catch(() => toast('Copy failed'));
}
function exportHTML() {
  const blob = new Blob(['<!DOCTYPE html>' + document.documentElement.outerHTML], {type:'text/html'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'claude-sessions-' + new Date().toISOString().slice(0,10) + '.html';
  a.click();
  URL.revokeObjectURL(a.href);
}
function exportScripts(proj, sid) {
  const s = findSession(proj, sid);
  if (!s) return;
  const scripts = s.actions.filter(a => a.script && a.tool_name === 'Bash').map(a => a.script);
  const blob = new Blob([scripts.join('\n\n')], {type:'text/x-shellscript'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = (s.slug || 'session') + '-scripts.sh';
  a.click();
}
function findSession(proj, sid) {
  const p = DATA.projects[proj];
  if (!p) return null;
  return p.sessions.find(s => s.id === sid) || null;
}
function setBreadcrumb(parts) {
  bc.innerHTML = parts.map((p, i) => {
    if (i === parts.length - 1) return '<span>' + esc(p.label) + '</span>';
    return '<a href="' + p.href + '">' + esc(p.label) + '</a><span class="sep">/</span>';
  }).join('');
}
function filterCurrent() {
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('[data-filter]').forEach(el => {
    const text = el.getAttribute('data-filter').toLowerCase();
    el.classList.toggle('hidden', q && !text.includes(q));
  });
}

function renderProjects() {
  setBreadcrumb([{label: 'Projects', href: '#projects'}]);
  const projs = Object.entries(DATA.projects);
  let totalSessions = 0, totalTokens = 0;
  projs.forEach(([_, p]) => {
    totalSessions += p.sessions.length;
    p.sessions.forEach(s => { totalTokens += (s.stats?.tokens || 0); });
  });
  let h = '<div class="stats-bar">';
  h += '<div class="stat"><div class="stat-label">Projects</div><div class="stat-value">' + projs.length + '</div></div>';
  h += '<div class="stat"><div class="stat-label">Sessions</div><div class="stat-value">' + totalSessions + '</div></div>';
  h += '<div class="stat"><div class="stat-label">Total Tokens</div><div class="stat-value">' + fmtTok(totalTokens) + '</div></div>';
  h += '</div>';
  const sorted = projs.sort((a,b) => (b[1].sessions[0]?.first_ts||'').localeCompare(a[1].sessions[0]?.first_ts||''));
  sorted.forEach(([path, proj]) => {
    const n = proj.sessions.length;
    const last = proj.sessions[0];
    h += '<a href="#project/' + encodeURIComponent(path) + '" style="text-decoration:none">';
    h += '<div class="card" data-filter="' + esc(path) + '">';
    h += '<div class="row"><div><div class="card-title">' + esc(shortPath(path)) + '</div>';
    h += '<div class="card-meta">' + esc(path) + '</div></div>';
    h += '<div class="card-right"><span class="badge badge-blue">' + n + ' sessions</span>';
    if (last?.git_branch) h += '<span class="badge badge-green">' + esc(last.git_branch) + '</span>';
    h += '</div></div>';
    if (last?.first_ts) h += '<div class="card-meta" style="margin-top:4px">Last: ' + fmtDate(last.first_ts) + '</div>';
    h += '</div></a>';
  });
  if (!projs.length) h += '<div class="empty">No sessions found</div>';
  app.innerHTML = h;
}

function renderProject(path) {
  const proj = DATA.projects[path];
  if (!proj) { app.innerHTML = '<div class="empty">Project not found</div>'; return; }
  setBreadcrumb([{label:'Projects',href:'#projects'},{label:shortPath(path),href:'#project/'+encodeURIComponent(path)}]);
  let h = '<div style="margin-bottom:16px"><div style="font-size:1.1em;font-weight:600;color:#58a6ff">' + esc(path) + '</div>';
  h += '<div class="card-meta">' + proj.sessions.length + ' sessions</div></div>';
  proj.sessions.forEach(s => {
    const ep = encodeURIComponent(path);
    h += '<div class="session-row" data-filter="' + esc(s.slug+' '+s.git_branch) + '">';
    h += '<div class="row"><div><div style="font-weight:600">' + esc(s.slug) + '</div>';
    h += '<div class="card-meta">' + esc(s.id.slice(0,12)) + ' · ' + esc(s.git_branch) + ' · ' + fmtDate(s.first_ts) + '</div>';
    h += '</div><div class="card-right">';
    h += '<span class="badge badge-blue">' + (s.stats?.entries||0) + '</span>';
    h += '<span class="badge badge-yellow">' + fmtTok(s.stats?.tokens||0) + '</span>';
    h += '<a href="#session/'+ep+'/'+s.id+'" class="btn btn-primary btn-sm">Chat</a>';
    h += '<a href="#actions/'+ep+'/'+s.id+'" class="btn btn-sm">Actions</a>';
    h += '</div></div></div>';
  });
  app.innerHTML = h;
}

function renderSession(path, sid) {
  const s = findSession(path, sid);
  if (!s) { app.innerHTML = '<div class="empty">Session not found</div>'; return; }
  const ep = encodeURIComponent(path);
  setBreadcrumb([{label:'Projects',href:'#projects'},{label:shortPath(path),href:'#project/'+ep},{label:s.slug,href:'#session/'+ep+'/'+sid}]);
  let h = '<div class="row" style="margin-bottom:16px"><div>';
  h += '<div style="font-size:1.1em;font-weight:600">' + esc(s.slug) + '</div>';
  h += '<div class="card-meta">' + esc(s.git_branch) + ' · ' + (s.stats?.entries||0) + ' entries · ' + fmtTok(s.stats?.tokens||0) + ' tokens</div>';
  h += '</div><div style="display:flex;gap:6px">';
  h += '<a href="#actions/'+ep+'/'+sid+'" class="btn btn-sm">Actions</a>';
  h += '<button onclick="copyText(location.href)" class="btn btn-sm">Share</button>';
  h += '<button onclick="exportHTML()" class="btn btn-sm">Export</button>';
  h += '</div></div>';
  // Build tool result lookup: tool_use_id -> {stdout, stderr}
  const resultMap = {};
  (s.entries||[]).forEach(e => {
    if (e.tool_result && e.tool_result.tool_use_id) {
      resultMap[e.tool_result.tool_use_id] = e.tool_result;
    }
  });
  (s.entries || []).forEach(e => {
    // Skip user entries that are pure tool results (shown inline with tool call)
    if (e.type === 'user' && !e.text && e.tool_result) return;
    if (e.type === 'system') {
      if (e.text) { h += '<div class="chat-entry chat-system"><div class="chat-role chat-role-system">SYSTEM</div><div class="chat-text">' + esc(e.text).slice(0,500) + '</div></div>'; }
      return;
    }
    const isUser = e.type === 'user';
    const cls = isUser ? 'chat-user' : 'chat-assistant';
    const roleCls = isUser ? 'chat-role-user' : 'chat-role-assistant';
    const label = isUser ? 'USER' : 'ASSISTANT' + (e.model ? ' ('+esc(e.model)+')' : '');
    h += '<div class="chat-entry '+cls+'"><div class="chat-role '+roleCls+'">'+label+'</div>';
    if (e.text) {
      const txt = e.text.length > 800 ? e.text.slice(0,800) + '\n... (truncated)' : e.text;
      h += '<div class="chat-text">' + esc(txt) + '</div>';
    }
    if (e.tool_calls) {
      e.tool_calls.forEach(tc => {
        const desc = tc.input?.description || tc.input?.file_path || tc.input?.command?.slice(0,60) || tc.input?.pattern || '';
        const inp = Object.entries(tc.input||{}).map(([k,v])=>esc(k)+': '+esc(String(v).slice(0,300))).join('\n');
        h += '<div class="tool-card"><div class="tool-header" onclick="this.nextElementSibling.classList.toggle(\'open\')">';
        h += '<span class="tool-name">' + esc(tc.name) + '</span>';
        if (desc) h += '<span style="color:#8b949e;font-size:0.8em;margin-left:8px">' + esc(String(desc).slice(0,60)) + '</span>';
        h += '<span>&#9654;</span></div>';
        h += '<div class="tool-body"><pre>' + inp + '</pre>';
        // Inline the tool result stdout/stderr
        const tr = resultMap[tc.id];
        if (tr) {
          const out = (tr.stdout||'').slice(0,800);
          if (out) { h += '<div class="output-block" style="margin-top:6px"><div style="color:#3fb950;font-size:0.75em;font-weight:600">stdout</div><pre>' + esc(out) + (tr.stdout.length>800?'\n...':'') + '</pre></div>'; }
          if (tr.stderr) { h += '<div class="error-block" style="margin-top:4px"><div style="color:#f85149;font-size:0.75em;font-weight:600">stderr</div><pre>' + esc(tr.stderr.slice(0,500)) + '</pre></div>'; }
        }
        h += '</div></div>';
      });
    }
    h += '</div>';
  });
  app.innerHTML = h + '<div id="toast" class="toast"></div>';
}

function renderActions(path, sid) {
  const s = findSession(path, sid);
  if (!s) { app.innerHTML = '<div class="empty">Session not found</div>'; return; }
  const ep = encodeURIComponent(path);
  setBreadcrumb([{label:'Projects',href:'#projects'},{label:shortPath(path),href:'#project/'+ep},{label:s.slug+' (Actions)',href:'#actions/'+ep+'/'+sid}]);
  const tools = {};
  (s.actions||[]).forEach(a => { tools[a.tool_name] = (tools[a.tool_name]||0) + 1; });
  let h = '<div class="row" style="margin-bottom:12px"><div>';
  h += '<div style="font-size:1.1em;font-weight:600">' + esc(s.slug) + ' — Actions</div>';
  h += '<div class="card-meta">' + (s.actions?.length||0) + ' actions</div>';
  h += '</div><div style="display:flex;gap:6px">';
  h += '<a href="#session/'+ep+'/'+sid+'" class="btn btn-sm btn-primary">Chat</a>';
  h += '<button onclick="exportScripts(\''+esc(path).replace(/'/g,"\\'")+'\',\''+sid+'\')" class="btn btn-sm">Export Scripts</button>';
  h += '<button onclick="copyText(location.href)" class="btn btn-sm">Share</button>';
  h += '</div></div>';
  h += '<div class="filter-bar">';
  h += '<button class="filter-btn active" onclick="setFilter(this,\'all\')">All ('+(s.actions?.length||0)+')</button>';
  Object.entries(tools).sort((a,b)=>b[1]-a[1]).forEach(([name,count]) => {
    h += '<button class="filter-btn" onclick="setFilter(this,\''+esc(name)+'\')">' + esc(name) + ' (' + count + ')</button>';
  });
  h += '</div><div id="actions-list">';
  (s.actions||[]).forEach(a => {
    const desc = a.description || (a.command ? a.command.slice(0,80) : a.file_path || a.tool_name);
    h += '<div class="action-row" data-tool="'+esc(a.tool_name)+'" data-filter="'+esc(a.tool_name+' '+desc)+'">';
    h += '<div class="action-header" onclick="this.nextElementSibling.classList.toggle(\'open\')">';
    h += '<div class="action-left"><span class="action-idx">#'+a.index+'</span>';
    h += '<span class="action-tool">'+esc(a.tool_name)+'</span>';
    h += '<span class="action-desc">'+esc(desc)+'</span></div>';
    h += '<button class="btn btn-sm" onclick="event.stopPropagation();copyText('+JSON.stringify(JSON.stringify(a.script||''))+')">Copy</button>';
    h += '</div><div class="action-body">';
    if (a.command) h += '<div class="card-meta">Command:</div><pre>'+esc(a.command.slice(0,500))+'</pre>';
    if (a.stdout) h += '<div class="output-block"><pre>'+esc(a.stdout.slice(0,800))+(a.stdout.length>800?'\n...':'')+'</pre></div>';
    if (a.stderr) h += '<div class="error-block"><pre>'+esc(a.stderr.slice(0,500))+'</pre></div>';
    h += '</div></div>';
  });
  h += '</div>';
  app.innerHTML = h + '<div id="toast" class="toast"></div>';
}

function setFilter(btn, tool) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.action-row').forEach(el => {
    el.classList.toggle('hidden', tool !== 'all' && el.getAttribute('data-tool') !== tool);
  });
}

function route() {
  const hash = location.hash.slice(1) || 'projects';
  const parts = hash.split('/');
  const view = parts[0];
  document.getElementById('search').value = '';
  if (view === 'projects') renderProjects();
  else if (view === 'project') renderProject(decodeURIComponent(parts.slice(1).join('/')));
  else if (view === 'session') {
    const sid = parts[parts.length-1];
    renderSession(decodeURIComponent(parts.slice(1,-1).join('/')), sid);
  } else if (view === 'actions') {
    const sid = parts[parts.length-1];
    renderActions(decodeURIComponent(parts.slice(1,-1).join('/')), sid);
  } else renderProjects();
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', route);
route();
"""

# EOF
