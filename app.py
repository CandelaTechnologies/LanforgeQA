# app.py - Final Version: parse_args() AFTER class
import ast
import os
import subprocess
import sys
from flask import Flask, request, render_template_string, send_file
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
PERSISTENT_FILE = os.path.join(app.config['UPLOAD_FOLDER'], "current_script.py")

# ------------------- Help from # Comments -------------------
def extract_help_from_comments(source_lines, node):
    helps = {}
    for i, arg in enumerate(node.args.args):
        if arg.arg in ('self', 'cls'): continue
        param = arg.arg
        line_no = arg.lineno - 1
        if line_no >= len(source_lines): continue

        comment_lines = []
        line = source_lines[line_no]
        if '#' in line:
            comment_lines.append(line.split('#', 1)[1].strip())

        end_line = node.args.args[i+1].lineno - 1 if i+1 < len(node.args.args) else node.body[0].lineno - 1
        for j in range(line_no + 1, end_line):
            if j >= len(source_lines): break
            txt = source_lines[j].strip()
            if txt.startswith('#'):
                comment_lines.append(txt[1:].strip())
            else:
                break
        if comment_lines:
            helps[param] = "\n".join(comment_lines)
    return helps

# ------------------- Build Final Script: Class First, Then parse_args() -------------------
def build_full_script(func_node, source_lines, func_name):
    helps = extract_help_from_comments(source_lines, func_node)
    if not helps:
        doc = ast.get_docstring(func_node) or ""
        for line in doc.split('\n'):
            line = line.strip()
            if ':' in line and not any(line.startswith(x) for x in ["Returns:", "Raises:"]):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    param = parts[0].strip().split()[-1]
                    helps[param] = parts[1].strip()

    class_name = "".join(word.capitalize() for word in func_name.split('_'))
    params = [a.arg for a in func_node.args.args if a.arg not in ('self', 'cls')]

    lines = [
        "#!/usr/bin/env python3",
        f'"""Auto-generated wrapper for {func_name}()"""',
        "import argparse",
        "",
        "",
        f"class {class_name}:",
        f"    \"\"\"Parameter holder and caller for {func_name}()\"\"\"",
        "",
        "    def __init__(self, **kwargs):",
        "        \"\"\"Initialize with parsed arguments\"\"\"",
        "        for key, value in kwargs.items():",
        "            setattr(self, key, value)",
        "",
        f"    def run(self):",
        f"        \"\"\"Execute the original {func_name}() function\"\"\"",
        "        from current_script import " + func_name,
        "",
        "        " + func_name + "("
    ]

    # Add function call parameters
    for i, param in enumerate(params):
        lines.append(f"            {param}=self.{param}," + ("" if i == len(params)-1 else ""))
    if params:
        lines[-1] = lines[-1].rstrip(",")
    lines.append("        )")

    lines += [
        "",
        "",
        "def parse_args():",
        f"    \"\"\"Parse command-line arguments for {func_name}()\"\"\"",
        "    parser = argparse.ArgumentParser(",
        f"        description='{func_name}() - auto-generated wrapper'",
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

        help_text = helps.get(name, "").replace('"', '\\"')
        short = name[0] if name[0] not in "h" else name[1] if len(name) > 1 else "x"

        line = f"    parser.add_argument('--{name}', '-{short}'"
        if typ and action != "store_true": line += f", type={typ}"
        if action: line += f", action='{action}'"
        if help_text: line += f", help=\"{help_text}\""

        if i >= default_start and func_node.args.defaults:
            default = ast.unparse(func_node.args.defaults[i - default_start])
            line += f", default={default}"
        else:
            line += ", required=True"
        line += ")"
        lines.append(line)

    lines += [
        "",
        "    return parser.parse_args()",
        "",
        "",
        "if __name__ == '__main__':",
        "    args = parse_args()",
        f"    runner = {class_name}(**vars(args))",
        "    runner.run()",
        "    print('Execution completed.')",
    ]

    return "\n".join(lines)

# ------------------- HTML UI (unchanged, beautiful as always) -------------------
HTML = """<!DOCTYPE html>
<html><head><title>Argparse + Class Wrapper Generator</title>
<meta charset="utf-8">
<style>
    body{font-family:system-ui;background:#f8fafc;margin:0;padding:20px;}
    .container{max-width:1100px;margin:auto;background:white;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,0.12);overflow:hidden;}
    header{background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:white;padding:40px;text-align:center;}
    h1{margin:0;font-size:36px;}
    .content{padding:40px;}
    .upload-box{border:3px dashed #8b5cf6;padding:40px;border-radius:16px;background:#f6f4ff;text-align:center;}
    input,button{padding:16px;margin:12px 0;font-size:17px;border-radius:12px;width:100%;border:1px solid #ddd;}
    button{background:#3b82f6;color:white;border:none;cursor:pointer;font-weight:bold;transition:0.3s;}
    button:hover{background:#2563eb;}
    .btn-success{background:#10b981;}
    .btn-success:hover{background:#16a34a;}
    .btn-download{background:#ef4444;}
    .btn-download:hover{background:#dc2626;}
    .functions{background:#f1f5f9;padding:25px;border-radius:14px;max-height:400px;overflow-y:auto;margin:25px 0;}
    .func-item{padding:18px;background:white;border-radius:12px;margin:12px 0;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.08);transition:0.3s;}
    .func-item:hover{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,0.15);}
    pre{background:#1e293b;color:#c4b5fd;padding:28px;border-radius:14px;overflow-x:auto;font-size:15px;line-height:1.6;}
    .status{padding:16px;border-radius:12px;margin:16px 0;font-weight:600;}
    .success{background:#dcfce7;color:#166534;}
    .error{background:#fee2e2;color:#991b1b;}
</style></head>
<body>
<div class="container">
<header><h1>Smart Wrapper Generator</h1><p>Class first • parse_args() after • Ready to run</p></header>
<div class="content">

{% if message %}<div class="status success">{{ message }}</div>{% endif %}
{% if error %}<div class="status error">{{ error }}</div>{% endif %}

<form method="post" enctype="multipart/form-data">
    <div class="upload-box">
        <h3>Upload Your Python File (saved permanently)</h3>
        <input type="file" name="file" accept=".py" required>
        <button type="submit" name="action" value="upload">Upload & Save</button>
    </div>
</form>

{% if functions %}
<h3>Select Function:</h3>
<div class="functions">
{% for f in functions %}
<div class="func-item" onclick="document.getElementById('method').value='{{ f.name }}'">
    <strong>{{ f.name }}()</strong><br>
    <small>{{ f.args|join(', ') or 'no parameters' }}</small>
</div>
{% endfor %}
</div>

<form method="post">
    <input type="text" id="method" name="method" placeholder="Enter function name" value="{{ selected|default('') }}" required>
    <br><br>
    <button type="submit" name="action" value="generate">Generate Full Wrapper</button>
    <button type="submit" class="btn-success" name="action" value="help">Show --help</button>
</form>
{% endif %}

{% if result %}
<div style="margin:30px 0;">
    <form method="post" style="display:inline;">
        <input type="hidden" name="method" value="{{ selected }}">
        <button type="submit" name="action" value="download" class="btn-download">
            Download wrapper_{{ selected }}.py
        </button>
    </form>
</div>
<h3>{% if is_help %}Terminal --help Output{% else %}Generated Wrapper Script{% endif %}</h3>
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
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in node.args.args if a.arg not in ('self', 'cls')]
                    functions.append({"name": node.name, "args": args})

    if request.method == "POST":
        action = request.form.get("action")

        if action == "upload":
            file = request.files["file"]
            if not file or not file.filename.endswith(".py"):
                return render_template_string(HTML, error="Please upload a valid .py file", functions=functions)
            file.save(PERSISTENT_FILE)
            return render_template_string(HTML, message="File uploaded and saved!", functions=functions, file_exists=True)

        method_name = request.form.get("method")
        if not method_name or not file_exists:
            return render_template_string(HTML, error="Missing function name or file", functions=functions)

        with open(PERSISTENT_FILE, "r", encoding="utf-8") as f:
            source = f.read()
            source_lines = source.splitlines()

        tree = ast.parse(source)
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                func_node = node
                break

        if not func_node:
            return render_template_string(HTML, error=f"Function '{method_name}' not found", functions=functions, selected=method_name)

        code = build_full_script(func_node, source_lines, method_name)

        if action == "download":
            buffer = BytesIO(code.encode('utf-8'))
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"wrapper_{method_name}.py",
                mimetype="text/x-python"
            )

        if action == "help":
            result = subprocess.run([sys.executable, "-c", code, "--help"], capture_output=True, text=True, timeout=10)
            output = result.stdout or result.stderr
            return render_template_string(HTML, result=output, is_help=True, functions=functions, selected=method_name, file_exists=True)

        return render_template_string(HTML, result=code, functions=functions, selected=method_name, file_exists=True)

    return render_template_string(HTML, functions=functions, file_exists=file_exists)

# ------------------- Run -------------------
if __name__ == "__main__":
    print("Final Version: Class first → parse_args() after")
    print("Open: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)