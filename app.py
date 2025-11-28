# app.py - With Download Button + # Comment Help + Persistent File
import ast
import os
import subprocess
import sys
from flask import Flask, request, render_template_string, send_file, jsonify
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
PERSISTENT_FILE = os.path.join(app.config['UPLOAD_FOLDER'], "current_script.py")

# ------------------- Help Extraction from # Comments -------------------
def extract_help_from_comments(source_lines, node):
    helps = {}
    current_param = None
    current_help = []

    for i, arg in enumerate(node.args.args):
        if arg.arg in ('self', 'cls'):
            continue
        param_name = arg.arg
        line_no = arg.lineno - 1

        if line_no >= len(source_lines):
            continue
        line = source_lines[line_no]
        comment = line.split('#', 1)[-1].strip() if '#' in line else ""
        if comment:
            current_help = [comment]
            current_param = param_name
        else:
            current_help = []
            current_param = None

        next_line = node.args.args[i+1].lineno - 1 if i+1 < len(node.args.args) else node.end_lineno
        for j in range(line_no + 1, next_line):
            if j >= len(source_lines):
                break
            next_line_text = source_lines[j].strip()
            if next_line_text.startswith('#'):
                current_help.append(next_line_text[1:].strip())
            else:
                break

        if current_help:
            helps[param_name] = "\n".join(current_help)

    return helps

def extract_help_from_docstring(doc):
    helps = {}
    if not doc: return helps
    in_args = False
    for line in doc.split('\n'):
        line = line.strip()
        if line in ("Args:", "Arguments:"): in_args = True; continue
        if in_args and ':' in line and not any(line.startswith(x) for x in ["Returns:", "Raises:"]):
            param, desc = line.split(':', 1)
            helps[param.strip().split()[0]] = desc.strip()
        elif in_args and line: in_args = False
    return helps

# ------------------- Build Parser -------------------
def build_parser_code(func_node, source_lines):
    helps = extract_help_from_comments(source_lines, func_node)
    if not helps:
        helps = extract_help_from_docstring(ast.get_docstring(func_node) or "")

    lines = [
        "#!/usr/bin/env python3",
        '"""Auto-generated argparse parser"""',
        "import argparse",
        "import sys",
        "",
        f"def parse_args():",
        "    parser = argparse.ArgumentParser(",
        f"        description='Auto-generated parser for {func_node.name}()'",
        "    )",
        ""
    ]

    default_start = len(func_node.args.args) - len(func_node.args.defaults)

    for i, arg in enumerate(func_node.args.args):
        name = arg.arg
        if name in ("self", "cls"): continue

        ann = ast.unparse(arg.annotation) if arg.annotation else None
        typ = "str"
        action = None
        if ann:
            a = ann.lower()
            if "int" in a: typ = "int"
            elif "float" in a: typ = "float"
            elif "bool" in a: typ = None; action = "store_true"
            elif "list" in a: typ = "str"; action = "append"

        help_text = helps.get(name, "").replace("'", "\\'").replace('"', '\\"')
        short = name[0]

        arg_line = f"    parser.add_argument('--{name}', '-{short}'"

        if typ and action != "store_true":
            arg_line += f", type={typ}"
        if action:
            arg_line += f", action='{action}'"

        if help_text:
            arg_line += f", help=\"{help_text}\""
        else:
            arg_line += f", help=''{''}"

        if i >= default_start and func_node.args.defaults:
            default = ast.unparse(func_node.args.defaults[i - default_start])
            arg_line += f", default={default}"
        else:
            arg_line += ", required=True"

        arg_line += ")"
        lines.append(arg_line)

    lines += [
        "",
        "    args = parser.parse_args()",
        "    return args",
        "",
        "if __name__ == '__main__':",
        "    args = parse_args()",
        "    print('Parsed args:', args)",
    ]
    return "\n".join(lines)

# ------------------- HTML with Download Button -------------------
HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Argparse Generator + Download</title>
    <meta charset="utf-8">
    <style>
        body {font-family: system-ui; background: #f5f7fa; margin:0; padding:20px;}
        .container {max-width: 1100px; margin: auto; background:white; border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,0.1); overflow:hidden;}
        header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:30px; text-align:center;}
        h1 {margin:0; font-size:32px;}
        .content {padding:30px;}
        .upload-box {border:3px dashed #764ba2; padding:30px; border-radius:12px; background:#f8f4ff; text-align:center;}
        input, button {padding:14px; margin:10px 0; font-size:16px; border-radius:10px; width:100%; border:1px solid #ddd;}
        button {background:#667eea; color:white; border:none; cursor:pointer; font-weight:bold;}
        button:hover {background:#5a6fd8;}
        .btn-success {background:#27ae60;}
        .btn-success:hover {background:#219a52;}
        .btn-download {background:#e74c3c;}
        .btn-download:hover {background:#c0392b;}
        .functions {max-height:320px; overflow-y:auto; background:#f9f9ff; padding:15px; border-radius:10px; margin:20px 0;}
        .func-item {padding:12px; margin:8px 0; background:white; border:1px solid #ddd; border-radius:10px; cursor:pointer; transition:0.2s;}
        .func-item:hover {background:#e8e6ff; border-color:#667eea; transform:scale(1.02);}
        pre {background:#2c3e50; color:#1abc9c; padding:20px; border-radius:10px; overflow-x:auto; font-size:14px;}
        .result-actions {display:flex; gap:15px; margin:20px 0;}
        .status {padding:15px; border-radius:10px; margin:15px 0;}
        .success {background:#d4edda; color:#155724;}
        .error {background:#f8d7da; color:#721c24;}
        footer {text-align:center; padding:20px; color:#95a5a6; font-size:14px;}
    </style>
</head>
<body>
<div class="container">
<header><h1>Argparse Generator</h1><p>Download ready-to-use parser.py</p></header>
<div class="content">

{% if message %}<div class="status success">{{ message }}</div>{% endif %}
{% if error %}<div class="status error">{{ error }}</div>{% endif %}

<form method="post" enctype="multipart/form-data">
    <div class="upload-box">
        <h3>Upload Python File (saved permanently)</h3>
        <input type="file" name="file" accept=".py">
        <button type="submit" name="action" value="upload">Upload & Save</button>
    </div>
</form>

{% if functions %}
<h3>Select Function:</h3>
<div class="functions">
{% for f in functions %}
<div class="func-item" onclick="document.getElementById('method').value='{{ f.name }}'">
    <strong>{{ f.name }}()</strong><br>
    <small>{{ f.args|join(', ') or 'no args' }}</small>
</div>
{% endfor %}
</div>

<form method="post">
    <input type="text" id="method" name="method" placeholder="Enter function name" value="{{ selected|default('') }}" required>
    <br><br>
    <button type="submit" name="action" value="generate">Generate Parser</button>
    <button type="submit" class="btn-success" name="action" value="help">Show --help</button>
</form>
{% endif %}

{% if result and not is_help %}
<h3>Generated Parser Code</h3>
<div class="result-actions">
    <form method="post">
        <input type="hidden" name="method" value="{{ selected }}">
        <button type="submit" name="action" value="download" class="btn-download">
            Download as parser_{{ selected }}.py
        </button>
    </form>
</div>
<pre>{{ result }}</pre>
{% elif result and is_help %}
<h3>Terminal --help Output</h3>
<pre>{{ result }}</pre>
{% endif %}

</div>
<footer>
    File: <code>{{ "current_script.py" if file_exists else "none" }}</code> • 
    Functions found: {{ functions|length if functions else 0 }}
</footer>
</div>
</body>
</html>"""

# ------------------- Routes -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    file_exists = os.path.exists(PERSISTENT_FILE)
    functions = []

    if file_exists:
        with open(PERSISTENT_FILE, "r", encoding="utf-8") as f:
            source = f.read()
            tree = ast.parse(source)
            visitor = type('v', (), {'functions': []})()
            def visit(node):
                if isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args if a.arg not in ('self', 'cls')]
                    visitor.functions.append({"name": node.name, "args": args})
                for child in ast.iter_child_nodes(node):
                    visit(child)
            visit(tree)
            functions = visitor.functions

    if request.method == "POST":
        action = request.form.get("action")

        if action == "upload":
            file = request.files["file"]
            if not file or not file.filename.endswith(".py"):
                return render_template_string(HTML, error="Invalid file", functions=functions)
            file.save(PERSISTENT_FILE)
            return render_template_string(HTML, message="File uploaded & saved!", functions=functions, file_exists=True)

        method = request.form.get("method", "").strip()
        if not method or not file_exists:
            return render_template_string(HTML, error="No method or file", functions=functions)

        with open(PERSISTENT_FILE, "r", encoding="utf-8") as f:
            source = f.read()
            source_lines = source.splitlines()

        tree = ast.parse(source)
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == method:
                func_node = node
                break

        if not func_node:
            return render_template_string(HTML, error=f"Function '{method}' not found", functions=functions, selected=method)

        code = build_parser_code(func_node, source_lines)

        if action == "download":
            buffer = BytesIO(code.encode('utf-8'))
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"parser_{method}.py",
                mimetype="text/x-python"
            )

        if action == "help":
            result = subprocess.run([sys.executable, "-c", code, "--help"], capture_output=True, text=True, timeout=10)
            output = result.stdout or result.stderr
            return render_template_string(HTML, result=output, is_help=True, functions=functions, selected=method, file_exists=True)

        return render_template_string(HTML, result=code, functions=functions, selected=method, file_exists=True)

    return render_template_string(HTML, functions=functions, file_exists=file_exists)

# ------------------- Run -------------------
if __name__ == "__main__":
    print("Argparse Generator with DOWNLOAD button!")
    print("http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)