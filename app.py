# app.py - Advanced Argparse Generator with Inline # Comments
import ast
import os
import subprocess
import sys
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
PERSISTENT_FILE = os.path.join(app.config['UPLOAD_FOLDER'], "current_script.py")

# ------------------- Extract Help from # Comments -------------------
def extract_help_from_comments(source_lines, node):
    """Extract help text from # comments next to parameters and following lines."""
    helps = {}
    current_param = None
    current_help = []

    # Find the parameter lines within the function
    for i, arg in enumerate(node.args.args):
        if arg.arg in ('self', 'cls'):
            continue

        param_name = arg.arg
        line_no = arg.lineno - 1  # 0-indexed

        # Look at the line where parameter is declared
        if line_no < len(source_lines):
            line = source_lines[line_no]
            comment = line.split('#', 1)[-1].strip() if '#' in line else ""
            if comment:
                current_help = [comment]
                current_param = param_name
            else:
                current_help = []
                current_param = None

        # Look at next lines until next parameter or def end
        next_param_line = node.args.args[i+1].lineno - 1 if i+1 < len(node.args.args) else node.end_lineno
        for j in range(line_no + 1, next_param_line):
            if j >= len(source_lines):
                break
            next_line = source_lines[j].strip()
            if next_line.startswith('#'):
                comment = next_line[1:].strip()
                if current_param == param_name:
                    current_help.append(comment)
            else:
                break  # stop at first non-comment line

        if current_help:
            helps[param_name] = "\n".join(current_help)

    return helps

# ------------------- Fallback to Docstring -------------------
def extract_help_from_docstring(docstring):
    helps = {}
    if not docstring:
        return helps
    in_args = False
    for line in docstring.split('\n'):
        line = line.strip()
        if line in ("Args:", "Arguments:"):
            in_args = True
            continue
        if in_args and ':' in line:
            if not any(line.startswith(x) for x in ["Returns:", "Raises:"]):
                param, desc = line.split(':', 1)
                param = param.strip().split()[0]
                helps[param] = desc.strip()
        elif in_args and line:
            in_args = False
    return helps

# ------------------- AST Visitors -------------------
class FuncVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
    def visit_FunctionDef(self, node):
        args = [a.arg for a in node.args.args if a.arg not in ('self', 'cls')]
        self.functions.append({"name": node.name, "args": args, "node": node})
        self.generic_visit(node)

# ------------------- Build Parser Code -------------------
def build_parser_code(func_node, source_lines):
    # 1. Try inline # comments first
    helps = extract_help_from_comments(source_lines, func_node)
    
    # 2. Fallback to docstring
    if not helps:
        doc = ast.get_docstring(func_node) or ""
        helps = extract_help_from_docstring(doc)

    lines = [
        "import argparse",
        "import sys",
        "",
        f"parser = argparse.ArgumentParser(description='Auto-generated for {func_node.name}()')",
        ""
    ]

    default_start = len(func_node.args.args) - len(func_node.args.defaults)

    for i, arg in enumerate(func_node.args.args):
        name = arg.arg
        if name in ("self", "cls"):
            continue

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

        arg_line = f"parser.add_argument('--{name}', '-{short}'"

        if typ and action != "store_true":
            arg_line += f", type={typ}"
        if action:
            arg_line += f", action='{action}'"

        if help_text:
            arg_line += f", help='{help_text}'"
        else:
            arg_line += ", help=''"

        if i >= default_start and func_node.args.defaults:
            default = ast.unparse(func_node.args.defaults[i - default_start])
            arg_line += f", default={default}"
        else:
            arg_line += ", required=True"

        arg_line += ")"
        lines.append(arg_line)

    lines += ["", "args = parser.parse_args()", "print(args)"]
    return "\n".join(lines)

# ------------------- HTML Template (same beautiful GUI) -------------------
HTML = """<!DOCTYPE html>
<html><head><title>Argparse Generator (# Comments Supported)</title>
<style>
    body{font-family:system-ui;background:#f0f4f8;margin:0;padding:20px;}
    .container{max-width:1000px;margin:0 auto;background:white;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.1);overflow:hidden;}
    header{background:#9b59b6;color:white;padding:25px;text-align:center;}
    h1{margin:0;font-size:28px;}
    .content{padding:30px;}
    .upload-box{border:3px dashed #9b59b6;padding:30px;border-radius:12px;background:#f8f3ff;text-align:center;}
    input,button{margin:10px 0;padding:12px;font-size:16px;border-radius:8px;width:100%;border:1px solid #ddd;}
    button{background:#9b59b6;color:white;border:none;cursor:pointer;font-weight:bold;}
    button:hover{background:#8e44ad;}
    .btn-help{background:#27ae60;}
    .btn-help:hover{background:#219a52;}
    .functions{max-height:300px;overflow-y:auto;background:#f8f9fa;padding:15px;border-radius:8px;margin:20px 0;}
    .func-item{padding:12px;margin:8px 0;background:white;border:1px solid #ddd;border-radius:8px;cursor:pointer;}
    .func-item:hover{background:#e8daef;border-color:#9b59b6;}
    pre{background:#2c3e50;color:#f1c40f;padding:20px;border-radius:8px;overflow-x:auto;}
    .status{padding:12px;margin:10px 0;border-radius:8px;}
    .success{background:#d5f4e0;color:#1e7e34;}
    .error{background:#fce4e4;color:#c53030;}
</style></head><body>
<div class="container">
<header><h1>Argparse Generator</h1><p>Supports # comments &amp; docstrings</p></header>
<div class="content">

{% if message %}<div class="status success">{{ message }}</div>{% endif %}
{% if error %}<div class="status error">{{ error }}</div>{% endif %}

<form method="post" enctype="multipart/form-data">
    <div class="upload-box">
        <h3>Upload Python File (saved permanently)</h3>
        <input type="file" name="file" accept=".py">
        <button type="submit" name="action" value="upload">Upload &amp; Save</button>
    </div>
</form>

{% if functions %}
<h3>Select Function:</h3>
<div class="functions">
{% for f in functions %}
<div class="func-item" onclick="document.getElementById('method').value='{{ f.name }}'">
    <strong>{{ f.name }}()</strong><br>
    <small>{{ f.args|join(', ') or 'no arguments' }}</small>
</div>
{% endfor %}
</div>

<form method="post">
    <input type="text" id="method" name="method" placeholder="Function name" value="{{ selected|default('') }}" required>
    <br><br>
    <button type="submit" name="action" value="generate">Generate Code</button>
    <button type="submit" class="btn-help" name="action" value="help">Show --help</button>
</form>
{% endif %}

{% if result %}
<h3>{{ "Generated Parser Code" if not is_help else "--help Output" }}</h3>
<pre>{{ result }}</pre>
{% endif %}

</div>
</div>
</body></html>"""

# ------------------- Routes -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    file_exists = os.path.exists(PERSISTENT_FILE)
    functions = []

    if file_exists:
        with open(PERSISTENT_FILE, "r", encoding="utf-8") as f:
            source = f.read()
            source_lines = source.splitlines()
            tree = ast.parse(source)
            visitor = FuncVisitor()
            visitor.visit(tree)
            functions = [{"name": f["name"], "args": f["args"]} for f in visitor.functions]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "upload":
            if "file" not in request.files or not request.files["file"].filename.endswith(".py"):
                return render_template_string(HTML, error="Invalid file", functions=functions)
            request.files["file"].save(PERSISTENT_FILE)
            return render_template_string(HTML, message="File saved!", functions=functions)

        method = request.form.get("method")
        if not method or not file_exists:
            return render_template_string(HTML, error="No file or method", functions=functions)

        with open(PERSISTENT_FILE, "r", encoding="utf-8") as f:
            source = f.read()
            source_lines = source.splitlines()

        tree = ast.parse(source)
        visitor = FuncVisitor()
        visitor.visit(tree)
        func_node = next((f["node"] for f in visitor.functions if f["name"] == method), None)

        if not func_node:
            return render_template_string(HTML, error=f"Function '{method}' not found", functions=functions, selected=method)

        code = build_parser_code(func_node, source_lines)

        if action == "help":
            result = subprocess.run([sys.executable, "-c", code, "--help"], capture_output=True, text=True, timeout=10)
            output = result.stdout or result.stderr
            return render_template_string(HTML, result=output, is_help=True, functions=functions, selected=method)

        return render_template_string(HTML, result=code, functions=functions, selected=method)

    return render_template_string(HTML, functions=functions)

# ------------------- Run -------------------
if __name__ == "__main__":
    print("Argparse Generator with # Comment Support")
    print("http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)