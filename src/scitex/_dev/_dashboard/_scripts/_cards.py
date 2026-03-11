#!/usr/bin/env python3
# Timestamp: 2026-02-05
# File: scitex/_dev/_dashboard/_scripts/_cards.py

"""Package card rendering functions for dashboard JavaScript."""


def get_cards_js() -> str:
    """Return JavaScript for package card rendering."""
    return """
function renderWorktreeStatus(gitInfo) {
    if (!gitInfo || gitInfo.dirty === undefined) return '';
    const parts = [];
    if (gitInfo.dirty) {
        parts.push('<span class="wt-dirty">dirty</span>');
    } else {
        parts.push('<span class="wt-clean">clean</span>');
    }
    if (gitInfo.ahead > 0) parts.push('<span class="wt-ahead">ahead:' + gitInfo.ahead + '</span>');
    if (gitInfo.behind > 0) parts.push('<span class="wt-behind">behind:' + gitInfo.behind + '</span>');
    return '<div class="version-item"><span class="key">worktree</span><span class="value">' + parts.join(', ') + '</span></div>';
}

function renderHostWorktreeStatus(h, loading) {
    if (loading) return '';
    if (h.git_dirty === undefined) return '';
    const parts = [];
    if (h.git_dirty) {
        parts.push('<span class="wt-dirty">dirty</span>');
    } else {
        parts.push('<span class="wt-clean">clean</span>');
    }
    if (h.git_ahead > 0) parts.push('<span class="wt-ahead">ahead:' + h.git_ahead + '</span>');
    if (h.git_behind > 0) parts.push('<span class="wt-behind">behind:' + h.git_behind + '</span>');
    return '<div class="version-item"><span class="key">worktree</span><span class="value">' + parts.join(', ') + '</span></div>';
}

function getEffectiveStatus(name, info) {
    const rtdData = cachedData.rtd || {};
    const hostData = cachedData.hosts || {};
    let status = info.status;

    if (status === 'ok') {
        // Check RTD
        const rtdLatest = rtdData['latest'] && rtdData['latest'][name];
        const rtdStable = rtdData['stable'] && rtdData['stable'][name];
        if ((rtdLatest && rtdLatest.status === 'failing') ||
            (rtdStable && rtdStable.status === 'failing') ||
            (rtdLatest && rtdLatest.status === 'not_found')) {
            status = 'mismatch';
        }

        // Check host versions (NAS, etc.) against LOCAL
        const localTag = info.git && info.git.latest_tag ? info.git.latest_tag.replace(/^v/, '') : null;
        const localToml = info.local && info.local.pyproject_toml;
        Object.entries(hostData).forEach(([hostName, hostInfo]) => {
            if (hostName.startsWith('_')) return;
            const pkgInfo = hostInfo[name];
            if (pkgInfo) {
                const hostTag = pkgInfo.git_tag ? pkgInfo.git_tag.replace(/^v/, '') : null;
                const hostToml = pkgInfo.toml;
                const hostInstalled = pkgInfo.installed;
                // Mismatch if host tag differs from local tag
                if (localTag && hostTag && localTag !== hostTag) {
                    status = 'mismatch';
                }
                // Mismatch if host toml differs from local toml
                if (localToml && hostToml && localToml !== hostToml) {
                    status = 'mismatch';
                }
                // Mismatch if host installed differs from host toml
                if (hostToml && hostInstalled && hostToml !== hostInstalled) {
                    status = 'mismatch';
                }
            }
        });
    }
    return status;
}

function getSourceStatuses(name, info, hostVersions, remoteVersions, rtdStatus) {
    const statuses = {};
    const local = info.local || {};
    const git = info.git || {};
    const remote = info.remote || {};
    const hostData = cachedData.hosts || {};
    const hostsLoading = !hostData || Object.keys(hostData).filter(k => !k.startsWith('_')).length === 0;
    const remotesLoading = !cachedData.remotes || Object.keys(cachedData.remotes).filter(k => !k.startsWith('_')).length === 0;
    const rtdLoading = !cachedData.rtd || Object.keys(cachedData.rtd).length === 0;

    const localToml = local.pyproject_toml;
    const localInstalled = local.installed;
    const localTag = git.latest_tag ? git.latest_tag.replace(/^v/, '') : null;

    // LOCAL status
    if (localToml && localInstalled) {
        statuses.local = (localToml === localInstalled) ? 'ok' : 'warn';
    } else if (localToml || localInstalled) {
        statuses.local = 'warn';
    } else {
        statuses.local = 'na';
    }
    // Downgrade local status if worktree is dirty or behind
    if (statuses.local === 'ok') {
        const gitInfo = info.git || {};
        if (gitInfo.dirty) statuses.local = 'warn';
        if (gitInfo.behind > 0) statuses.local = 'error';
    }

    // HOST statuses (NAS, etc.)
    hostVersions.forEach(h => {
        if (hostsLoading) {
            statuses[h.name] = 'loading';
        } else if (h.error || h.status === 'error' || h.status === 'not_installed') {
            statuses[h.name] = 'error';
        } else {
            const hostTag = h.git_tag ? h.git_tag.replace(/^v/, '') : null;
            // Compare host with local
            if (localTag && hostTag && localTag !== hostTag) {
                statuses[h.name] = 'error';
            } else if (localToml && h.toml && localToml !== h.toml) {
                statuses[h.name] = 'error';
            } else if (h.installed && h.toml && h.installed !== h.toml) {
                statuses[h.name] = 'warn';
            } else if (h.installed || h.toml) {
                statuses[h.name] = 'ok';
            } else {
                statuses[h.name] = 'na';
            }
            // Downgrade host status if worktree dirty or behind
            if (statuses[h.name] === 'ok') {
                if (h.git_dirty) statuses[h.name] = 'warn';
                if (h.git_behind > 0) statuses[h.name] = 'error';
            }
        }
    });

    // PYPI status
    if (remote.pypi) {
        statuses.pypi = (localToml && remote.pypi === localToml) ? 'ok' : (localToml ? 'warn' : 'ok');
    } else {
        statuses.pypi = 'na';
    }

    // GITHUB status
    if (remotesLoading) {
        statuses.github = 'loading';
    } else if (remoteVersions.length > 0) {
        const ghTag = remoteVersions[0].latest_tag;
        if (ghTag) {
            const ghVer = ghTag.replace(/^v/, '');
            statuses.github = (localToml && ghVer === localToml) ? 'ok' : (localToml ? 'warn' : 'ok');
        } else {
            statuses.github = remoteVersions[0].error ? 'error' : 'na';
        }
    } else {
        statuses.github = 'na';
    }

    // RTD status
    if (rtdLoading) {
        statuses.rtd = 'loading';
    } else if (rtdStatus && Object.keys(rtdStatus).length > 0) {
        const rtdLatest = rtdStatus['latest'];
        const rtdStable = rtdStatus['stable'];
        if ((rtdLatest && rtdLatest.status === 'failing') || (rtdStable && rtdStable.status === 'failing')) {
            statuses.rtd = 'error';
        } else if (rtdLatest && rtdLatest.status === 'not_found') {
            statuses.rtd = 'na';
        } else if ((rtdLatest && rtdLatest.status === 'passing') || (rtdStable && rtdStable.status === 'passing')) {
            statuses.rtd = 'ok';
        } else {
            statuses.rtd = 'warn';
        }
    } else {
        statuses.rtd = 'na';
    }

    return statuses;
}

function renderSourceBadges(sourceStatuses) {
    // Build order dynamically: local, then all hosts, then pypi/github/rtd
    const hostKeys = Object.keys(sourceStatuses).filter(k => !['local', 'pypi', 'github', 'rtd'].includes(k));
    const order = ['local', ...hostKeys, 'pypi', 'github', 'rtd'];
    const labels = { local: 'Local', pypi: 'PyPI', github: 'GitHub', rtd: 'RTD' };

    let html = '<span class="source-badges">';
    order.forEach(key => {
        if (sourceStatuses[key] !== undefined) {
            const st = sourceStatuses[key];
            const cls = st === 'ok' ? 'src-ok' : st === 'warn' ? 'src-warn' : st === 'error' ? 'src-error' : st === 'loading' ? 'src-loading' : 'src-na';
            const label = labels[key] || key.toUpperCase();
            html += `<span class="source-badge ${cls}" title="${key.toUpperCase()}: ${st}">${label}</span>`;
        }
    });
    html += '</span>';
    return html;
}

function renderPackageCard(name, info, local, git, remote, hostVersions, remoteVersions, rtdStatus) {
    const pypiUrl = `https://pypi.org/project/${name}/`;
    const githubUrl = `https://github.com/ywatanabe1989/${name}`;
    const rtdUrl = `https://${name === 'scitex' ? 'scitex-python' : name}.readthedocs.io/`;

    let allIssues = [...(info.issues || [])];
    let effectiveStatus = getEffectiveStatus(name, info);

    // Add host-related issues
    const localTag = git.latest_tag ? git.latest_tag.replace(/^v/, '') : null;
    const localToml = local.pyproject_toml;
    hostVersions.forEach(h => {
        const hostTag = h.git_tag ? h.git_tag.replace(/^v/, '') : null;
        if (localTag && hostTag && localTag !== hostTag) {
            allIssues.push(`${h.name.toUpperCase()} tag (${hostTag}) != LOCAL tag (${localTag})`);
        }
        if (localToml && h.toml && localToml !== h.toml) {
            allIssues.push(`${h.name.toUpperCase()} toml (${h.toml}) != LOCAL toml (${localToml})`);
        }
    });

    // RTD issues
    if (rtdStatus && Object.keys(rtdStatus).length > 0) {
        const rtdLatest = rtdStatus['latest'];
        const rtdStable = rtdStatus['stable'];
        if (rtdLatest && rtdLatest.status === 'failing') allIssues.push('RTD latest build failing');
        if (rtdStable && rtdStable.status === 'failing') allIssues.push('RTD stable build failing');
        if (rtdLatest && rtdLatest.status === 'not_found') allIssues.push('RTD project not found');
    }

    const tooltipText = allIssues.length > 0 ? allIssues.join('&#10;') : '';
    const tooltipAttr = tooltipText ? `title="${tooltipText}"` : '';

    const hostMeta = (cachedData.hosts && cachedData.hosts._meta) || {};
    const sourceStatuses = getSourceStatuses(name, info, hostVersions, remoteVersions, rtdStatus);
    const sourceBadgesHtml = renderSourceBadges(sourceStatuses);

    let html = `
        <div class="package-card collapsed">
            <div class="package-header" onclick="toggleCard(this)">
                <span class="fold-icon">▶</span>
                <a href="${githubUrl}" target="_blank" class="package-name" onclick="event.stopPropagation()">${name}</a>
                <span class="status-badge status-${effectiveStatus}" ${tooltipAttr}>${effectiveStatus}</span>
                ${sourceBadgesHtml}
                <span class="quick-links">
                    <a href="${pypiUrl}" target="_blank" title="PyPI" onclick="event.stopPropagation()">📦</a>
                    <a href="${githubUrl}" target="_blank" title="GitHub" onclick="event.stopPropagation()">🐙</a>
                    <a href="${rtdUrl}" target="_blank" title="Docs" onclick="event.stopPropagation()">📖</a>
                </span>
            </div>
            <div class="package-body">
                <div class="version-grid">
                    <div class="version-section">
                        <h4>LOCAL <span class="host-ip">(127.0.0.1)</span></h4>
                        <div class="version-item"><span class="key">toml</span><span class="value">${local.pyproject_toml || '-'}</span></div>
                        <div class="version-item"><span class="key">installed</span><span class="value">${local.installed || '-'}</span></div>
                        <div class="version-item"><span class="key">tag</span><span class="value">${git.latest_tag || '-'}</span></div>
                        <div class="version-item"><span class="key">branch</span><span class="value">${git.branch || '-'}${git.short_hash ? ' (' + git.short_hash + ')' : ''}</span></div>
                        ${renderWorktreeStatus(git)}
                    </div>`;

    // Host versions (NAS, etc.)
    const expectedHosts = [...document.querySelectorAll('#hostFilters input:checked')].map(el => el.value);
    const hostsLoading = !cachedData.hosts || Object.keys(cachedData.hosts).filter(k => !k.startsWith('_')).length === 0;

    expectedHosts.forEach(hostName => {
        const h = hostVersions.find(hv => hv.name === hostName) || {};
        const meta = hostMeta[hostName] || {};
        const ipDisplay = meta.hostname ? `<span class="host-ip">(${meta.hostname})</span>` : '';
        const loadingClass = hostsLoading ? ' loading-cell' : '';

        html += `<div class="version-section${loadingClass}"><h4>${hostName.toUpperCase()} ${ipDisplay}</h4>`;
        html += `<div class="version-item"><span class="key">toml</span><span class="value">${hostsLoading ? '...' : (h.toml || '-')}</span></div>`;
        html += `<div class="version-item"><span class="key">installed</span><span class="value">${hostsLoading ? '...' : (h.installed || h.error || '-')}</span></div>`;
        html += `<div class="version-item"><span class="key">tag</span><span class="value">${hostsLoading ? '...' : (h.git_tag || '-')}</span></div>`;
        html += `<div class="version-item"><span class="key">branch</span><span class="value">${hostsLoading ? '...' : ((h.git_branch || '-') + (h.git_hash ? ' (' + h.git_hash + ')' : ''))}</span></div>`;
        html += renderHostWorktreeStatus(h, hostsLoading);
        html += `</div>`;
    });

    html += `
                    <div class="version-section">
                        <h4><a href="https://pypi.org/project/${name}/" target="_blank">PYPI</a></h4>
                        <div class="version-item"><span class="key">published</span><span class="value">${remote.pypi || '-'}</span></div>
                    </div>`;

    if (remoteVersions.length > 0) {
        html += `<div class="version-section"><h4><a href="${githubUrl}" target="_blank">GITHUB</a></h4>`;
        remoteVersions.forEach(r => {
            html += `<div class="version-item"><span class="key">${r.name}</span><span class="value">${r.latest_tag || r.error || '-'}</span></div>`;
        });
        html += `</div>`;
    }

    if (rtdStatus && Object.keys(rtdStatus).length > 0) {
        html += `<div class="version-section"><h4><a href="${rtdUrl}" target="_blank">RTD</a></h4>`;
        Object.entries(rtdStatus).forEach(([version, data]) => {
            const statusClass = data.status === 'passing' ? 'rtd-passing' : (data.status === 'failing' ? 'rtd-failing' : 'rtd-unknown');
            const statusIcon = data.status === 'passing' ? '✓' : (data.status === 'failing' ? '✗' : '?');
            const link = data.url ? `<a href="${data.url}" target="_blank">${statusIcon}</a>` : statusIcon;
            html += `<div class="version-item"><span class="key">${version}</span><span class="value ${statusClass}">${link} ${data.status || '-'}</span></div>`;
        });
        html += `</div>`;
    }

    html += `</div>`;

    if (allIssues.length > 0) {
        html += `<div class="issues"><h4>Issues</h4><ul>`;
        allIssues.forEach(i => { html += `<li>${i}</li>`; });
        html += `</ul></div>`;
    }

    html += `</div></div>`;
    return html;
}
"""


# EOF
