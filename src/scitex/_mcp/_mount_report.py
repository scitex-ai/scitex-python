"""Construction diagnostics only; never import peers or execute their tools."""


def begin_report(server, entries, enabled):
    """Record namespace selection before the bounded resolver runs.

    Mounted entries are filled by the main-thread coordinator. The snapshot
    distinguishes opt-outs, unresolved peers and mount errors without guessing
    from the presence of an unrelated compatibility alias.
    """
    peers = []
    report = {}
    for _owner, import_name, namespace in entries:
        if enabled(namespace):
            peers.append((import_name, namespace))
            report[namespace] = {
                "state": "unavailable",
                "reason": "No peer server resolved",
            }
        else:
            report[namespace] = {"state": "disabled"}
    server._scitex_peer_mount_report = report
    return peers, report
