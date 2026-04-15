#!/usr/bin/env python3
# Timestamp: 2025-12-20
# File: /home/ywatanabe/proj/scitex-code/src/scitex/fsb/_tables/_latex/_editor/_app.py

"""Flask application for LaTeX error editor.

``flask`` is an optional third-party dependency used exclusively by the
interactive LaTeX editor (``LaTeXEditor`` / ``launch_editor``). Importing
it at module load leaks ``ModuleNotFoundError: No module named 'flask'``
through the ``scitex.io.bundle`` eager-import chain, which in turn
breaks the top-level public API ``import scitex.io`` on any install
without ``flask`` -- see ywatanabe1989/todo#441.

To keep ``import scitex.io`` side-effect-free, the flask import now
lives inside ``LaTeXEditor.__init__`` (and the few methods that need
the module-level ``request`` / ``jsonify`` names). Merely importing
this module, ``scitex.io``, or any parent package no longer requires
``flask``; only constructing a ``LaTeXEditor`` or calling
``launch_editor`` does.
"""

import json
import socket
import subprocess
import tempfile
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .._validator import ValidationResult, validate_latex

if TYPE_CHECKING:
    from scitex.io.bundle import FTS


# HTML template with CodeMirror editor
EDITOR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LaTeX Editor - FTS</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/monokai.min.css">
    <style>
        :root {
            --bg-primary: #1e1e1e;
            --bg-secondary: #252526;
            --bg-tertiary: #2d2d30;
            --text-primary: #d4d4d4;
            --text-secondary: #808080;
            --accent: #569cd6;
            --error: #f44747;
            --warning: #ffcc00;
            --success: #4ec9b0;
            --border: #3c3c3c;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background: var(--bg-secondary);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }

        header h1 {
            font-size: 16px;
            font-weight: 500;
        }

        .controls {
            display: flex;
            gap: 10px;
        }

        button {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
        }

        button:hover {
            background: var(--accent);
            color: #fff;
        }

        button.primary {
            background: var(--accent);
            color: #fff;
            border-color: var(--accent);
        }

        button.primary:hover {
            background: #4a8bc9;
        }

        .main-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        .editor-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            border-right: 1px solid var(--border);
        }

        .CodeMirror {
            flex: 1;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 14px;
            line-height: 1.6;
        }

        .error-panel {
            width: 350px;
            background: var(--bg-secondary);
            display: flex;
            flex-direction: column;
        }

        .error-panel h2 {
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 500;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border);
        }

        .error-list {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }

        .error-item {
            padding: 10px 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .error-item:hover {
            background: var(--bg-tertiary);
        }

        .error-item.error {
            border-left: 3px solid var(--error);
        }

        .error-item.warning {
            border-left: 3px solid var(--warning);
        }

        .error-item.info {
            border-left: 3px solid var(--accent);
        }

        .error-code {
            display: inline-block;
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin-right: 8px;
        }

        .error-location {
            color: var(--text-secondary);
            font-size: 12px;
            margin-top: 4px;
        }

        .error-message {
            font-size: 13px;
            margin-top: 4px;
        }

        .error-suggestion {
            color: var(--success);
            font-size: 12px;
            margin-top: 6px;
        }

        .no-errors {
            padding: 20px;
            text-align: center;
            color: var(--success);
        }

        .status-bar {
            background: var(--bg-secondary);
            padding: 6px 16px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            border-top: 1px solid var(--border);
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .status-dot.valid {
            background: var(--success);
        }

        .status-dot.invalid {
            background: var(--error);
        }

        .cm-error-line {
            background: rgba(244, 71, 71, 0.15) !important;
        }

        .cm-warning-line {
            background: rgba(255, 204, 0, 0.1) !important;
        }

        /* Loading spinner */
        .loading {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg-secondary);
            padding: 20px 40px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }

        .loading.active {
            display: block;
        }
    </style>
</head>
<body>
    <header>
        <h1>LaTeX Editor - {{ bundle_name }}</h1>
        <div class="controls">
            <button onclick="validateCode()">Validate</button>
            <button onclick="compilePreview()">Compile Preview</button>
            <button class="primary" onclick="saveCode()">Save</button>
        </div>
    </header>

    <div class="main-container">
        <div class="editor-panel">
            <textarea id="latex-editor">{{ latex_code }}</textarea>
        </div>

        <div class="error-panel">
            <h2>Issues <span id="issue-count">({{ error_count }})</span></h2>
            <div class="error-list" id="error-list">
                {% if errors %}
                    {% for error in errors %}
                    <div class="error-item {{ error.severity.value }}"
                         onclick="goToLine({{ error.line }}, {{ error.column }})">
                        <span class="error-code">{{ error.code }}</span>
                        <span class="error-severity">{{ error.severity.value }}</span>
                        <div class="error-location">Line {{ error.line }}, Col {{ error.column }}</div>
                        <div class="error-message">{{ error.message }}</div>
                        {% if error.suggestion %}
                        <div class="error-suggestion">Fix: {{ error.suggestion }}</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="no-errors">No issues found</div>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="status-bar">
        <div class="status-item">
            <span class="status-dot {{ 'valid' if is_valid else 'invalid' }}"></span>
            <span id="status-text">{{ 'Valid' if is_valid else 'Has issues' }}</span>
        </div>
        <div class="status-item">
            <span id="cursor-pos">Line 1, Col 1</span>
        </div>
    </div>

    <div class="loading" id="loading">Processing...</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/stex/stex.min.js"></script>
    <script>
        let editor;
        let lineWidgets = [];

        document.addEventListener('DOMContentLoaded', function() {
            editor = CodeMirror.fromTextArea(document.getElementById('latex-editor'), {
                mode: 'stex',
                theme: 'monokai',
                lineNumbers: true,
                lineWrapping: true,
                indentUnit: 4,
                tabSize: 4,
                indentWithTabs: false,
                matchBrackets: true,
                autoCloseBrackets: true
            });

            editor.on('cursorActivity', function() {
                const pos = editor.getCursor();
                document.getElementById('cursor-pos').textContent =
                    `Line ${pos.line + 1}, Col ${pos.ch + 1}`;
            });

            // Highlight initial errors
            highlightErrors({{ errors_json|safe }});
        });

        function goToLine(line, col) {
            editor.setCursor(line - 1, col - 1);
            editor.focus();
        }

        function highlightErrors(errors) {
            // Clear previous highlights
            lineWidgets.forEach(w => w.clear());
            lineWidgets = [];

            errors.forEach(error => {
                if (error.line > 0) {
                    const className = error.severity === 'error' ? 'cm-error-line' : 'cm-warning-line';
                    const handle = editor.addLineClass(error.line - 1, 'background', className);
                    lineWidgets.push({
                        clear: () => editor.removeLineClass(handle, 'background', className)
                    });
                }
            });
        }

        function showLoading(show) {
            document.getElementById('loading').classList.toggle('active', show);
        }

        async function validateCode() {
            showLoading(true);
            try {
                const response = await fetch('/validate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        code: editor.getValue(),
                        level: 'semantic'
                    })
                });
                const data = await response.json();
                updateErrors(data.errors);
                updateStatus(data.is_valid);
            } catch (e) {
                console.error('Validation failed:', e);
            }
            showLoading(false);
        }

        async function saveCode() {
            showLoading(true);
            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        code: editor.getValue()
                    })
                });
                const data = await response.json();
                if (data.success) {
                    alert('Saved successfully!');
                } else {
                    alert('Save failed: ' + data.error);
                }
            } catch (e) {
                alert('Save failed: ' + e.message);
            }
            showLoading(false);
        }

        async function compilePreview() {
            showLoading(true);
            try {
                const response = await fetch('/compile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        code: editor.getValue()
                    })
                });
                const data = await response.json();
                if (data.success) {
                    window.open('/preview', '_blank');
                } else {
                    updateErrors(data.errors || []);
                    alert('Compilation failed. See errors panel.');
                }
            } catch (e) {
                alert('Compilation failed: ' + e.message);
            }
            showLoading(false);
        }

        function updateErrors(errors) {
            const list = document.getElementById('error-list');
            const count = document.getElementById('issue-count');

            count.textContent = `(${errors.length})`;

            if (errors.length === 0) {
                list.innerHTML = '<div class="no-errors">No issues found</div>';
            } else {
                list.innerHTML = errors.map(e => `
                    <div class="error-item ${e.severity}" onclick="goToLine(${e.line}, ${e.column})">
                        <span class="error-code">${e.code}</span>
                        <span class="error-severity">${e.severity}</span>
                        <div class="error-location">Line ${e.line}, Col ${e.column}</div>
                        <div class="error-message">${e.message}</div>
                        ${e.suggestion ? `<div class="error-suggestion">Fix: ${e.suggestion}</div>` : ''}
                    </div>
                `).join('');
            }

            highlightErrors(errors);
        }

        function updateStatus(isValid) {
            const dot = document.querySelector('.status-dot');
            const text = document.getElementById('status-text');

            dot.className = 'status-dot ' + (isValid ? 'valid' : 'invalid');
            text.textContent = isValid ? 'Valid' : 'Has issues';
        }
    </script>
</body>
</html>
"""


class LaTeXEditor:
    """Flask-based LaTeX editor with error highlighting."""

    def __init__(
        self,
        latex_code: str,
        bundle: Optional["FTS"] = None,
        output_path: Optional[Path] = None,
    ):
        """Initialize editor.

        Args:
            latex_code: Initial LaTeX code
            bundle: Associated FTS bundle
            output_path: Where to save edits
        """
        # Lazy flask import so ``import scitex.io`` does not require
        # flask. See module docstring and ywatanabe1989/todo#441.
        from flask import Flask  # noqa: PLC0415

        self.latex_code = latex_code
        self.bundle = bundle
        self.output_path = output_path
        self.app = Flask(__name__)
        self._setup_routes()
        self._validation_result: Optional[ValidationResult] = None
        self._compiled_pdf: Optional[Path] = None

    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        # Lazy flask imports so ``import scitex.io`` does not require
        # flask. See module docstring and ywatanabe1989/todo#441.
        from flask import (  # noqa: PLC0415
            jsonify,
            render_template_string,
            request,
        )

        @self.app.route("/")
        def index():
            # Validate code
            self._validation_result = validate_latex(self.latex_code, level="semantic")

            errors = self._validation_result.all_issues
            errors_json = json.dumps(
                [
                    {
                        "line": e.line,
                        "column": e.column,
                        "message": e.message,
                        "severity": e.severity.value,
                        "code": e.code,
                        "suggestion": e.suggestion,
                    }
                    for e in errors
                ]
            )

            bundle_name = "Untitled"
            if self.bundle:
                bundle_name = self.bundle.node.name or self.bundle.node.id

            return render_template_string(
                EDITOR_TEMPLATE,
                latex_code=self.latex_code,
                errors=errors,
                errors_json=errors_json,
                error_count=len(errors),
                is_valid=self._validation_result.is_valid,
                bundle_name=bundle_name,
            )

        @self.app.route("/validate", methods=["POST"])
        def validate():
            data = request.get_json()
            code = data.get("code", "")
            level = data.get("level", "semantic")

            result = validate_latex(code, level=level)
            self.latex_code = code

            return jsonify(
                {
                    "is_valid": result.is_valid,
                    "errors": [
                        {
                            "line": e.line,
                            "column": e.column,
                            "message": e.message,
                            "severity": e.severity.value,
                            "code": e.code,
                            "suggestion": e.suggestion,
                        }
                        for e in result.all_issues
                    ],
                }
            )

        @self.app.route("/save", methods=["POST"])
        def save():
            data = request.get_json()
            code = data.get("code", "")

            try:
                if self.output_path:
                    self.output_path.write_text(code, encoding="utf-8")
                    self.latex_code = code
                    return jsonify({"success": True})
                elif self.bundle:
                    # Save to bundle exports
                    exports_dir = self.bundle.path / "exports"
                    exports_dir.mkdir(exist_ok=True)
                    tex_path = exports_dir / f"{self.bundle.node.id}.tex"
                    tex_path.write_text(code, encoding="utf-8")
                    self.latex_code = code
                    return jsonify({"success": True, "path": str(tex_path)})
                else:
                    return jsonify(
                        {"success": False, "error": "No output path configured"}
                    )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/compile", methods=["POST"])
        def compile():
            data = request.get_json()
            code = data.get("code", "")

            # Wrap in document if needed
            if "\\documentclass" not in code:
                code = _wrap_in_document(code)

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tex_path = Path(tmpdir) / "document.tex"
                    tex_path.write_text(code, encoding="utf-8")

                    proc = subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
                        cwd=tmpdir,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    pdf_path = Path(tmpdir) / "document.pdf"
                    if pdf_path.exists():
                        # Copy to temp location accessible by preview route
                        import shutil

                        self._compiled_pdf = (
                            Path(tempfile.gettempdir()) / "fsb_preview.pdf"
                        )
                        shutil.copy(pdf_path, self._compiled_pdf)
                        return jsonify({"success": True})
                    else:
                        # Parse errors
                        result = validate_latex(code, level="compile")
                        return jsonify(
                            {
                                "success": False,
                                "errors": [
                                    {
                                        "line": e.line,
                                        "column": e.column,
                                        "message": e.message,
                                        "severity": e.severity.value,
                                        "code": e.code,
                                        "suggestion": e.suggestion,
                                    }
                                    for e in result.all_issues
                                ],
                            }
                        )

            except FileNotFoundError:
                return jsonify({"success": False, "error": "pdflatex not found"})
            except subprocess.TimeoutExpired:
                return jsonify({"success": False, "error": "Compilation timed out"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/preview")
        def preview():
            if self._compiled_pdf and self._compiled_pdf.exists():
                from flask import send_file

                return send_file(self._compiled_pdf, mimetype="application/pdf")
            return "No preview available", 404

        @self.app.route("/shutdown", methods=["POST"])
        def shutdown():
            func = request.environ.get("werkzeug.server.shutdown")
            if func:
                func()
            return "Shutting down..."

    def run(self, port: int = 5051, open_browser: bool = True) -> None:
        """Run the editor server.

        Args:
            port: Port to run on
            open_browser: Whether to open browser automatically
        """
        # Find available port
        port = _find_available_port(port)

        url = f"http://127.0.0.1:{port}"
        print(f"LaTeX Editor running at {url}")

        if open_browser:
            webbrowser.open(url)

        self.app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def _find_available_port(start_port: int = 5051) -> int:
    """Find an available port.

    Args:
        start_port: Port to start searching from

    Returns:
        Available port number
    """
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")


def _wrap_in_document(content: str) -> str:
    """Wrap content in a minimal LaTeX document.

    Args:
        content: LaTeX content

    Returns:
        Complete document string
    """
    return f"""\\documentclass{{article}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{amsmath}}
\\begin{{document}}
{content}
\\end{{document}}
"""


def launch_editor(
    latex_code: str,
    bundle: Optional["FTS"] = None,
    output_path: Optional[Path] = None,
    port: int = 5051,
    open_browser: bool = True,
) -> None:
    """Launch the LaTeX editor.

    Args:
        latex_code: LaTeX code to edit
        bundle: Associated FTS bundle
        output_path: Where to save edits
        port: Port to run on
        open_browser: Whether to open browser
    """
    editor = LaTeXEditor(latex_code, bundle, output_path)
    editor.run(port=port, open_browser=open_browser)


__all__ = ["LaTeXEditor", "launch_editor"]

# EOF
