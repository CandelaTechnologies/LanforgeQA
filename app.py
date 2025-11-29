# app.py - Generates Class Wrapper + parse_args() + Download
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

# ------------------- Build Full Parser + Class -------------------
def build_full_script(func_node, source_lines, original_func_name):
    helps = extract_help_from_comments(source_lines, func_node)
    doc = ast.get_docstring(func_node) or ""
    if not helps:
        # fallback to docstring
        for line in doc.split('\n'):
            if ': ' in line and not line.strip().startswith(('Returns:', 'Raises:')):
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    param = parts[0].strip().split()[-1]
                    helps[param] = parts[1].strip()

    class_name = "".join(word.capitalize() for word in original_func_name.split('_'))
    params = [arg.arg for arg in func_node.args.args if arg.arg not in ('self', 'cls')]

    lines = [
        "#!/usr/bin/env python3",
        '"""Auto-generated wrapper for ' + original_func_name + '()"""',
        "import argparse",
        "",
        "def parse_args():",
        "    parser = argparse.ArgumentParser(description=\"" + func_node.name + " wrapper\")",
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
        short = name[0] if name[0] not in "h" else name[1] if len(name)>1 else "x"

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
        f"class {class_name}:",
        "    \"\"\"Wrapper class that holds parameters and can call the original function\"\"\"",
        "",
        "    def __init__(self, **kwargs):",
        "        for key, value in kwargs.items():",
        "            setattr(self, key, value)",
        "",
        f"    def {original_func_name}(self):",
        "        \"\"\"Call the original function with self. parameters\"\"\"",
        "        from current_script import " + original_func_name + "  # your original file",
        ""
    ]

    call_lines = ["        " + original_func_name + "("]
    for param in params:
        call_lines.append(f"            {param}=self.{param},")
    call_lines[-1] = call_lines[-1].rstrip(",") + ")"
    lines.extend(call_lines)
    lines.append("")

    lines += [
        "",
        "if __name__ == '__main__':",
        "    args = parse_args()",
        f"    runner = {class_name}(**vars(args))",
        f"    runner.{original_func_name}()",
        "    print('Done!')",
    ]

    return "\n".join(lines)

# ------------------- HTML (same great UI + Download) -------------------
HTML = """<!DOCTYPE html>
<html><head><title>Argparse + Class Wrapper Generator</title>
<style>
    body{font-family:system-ui;background:#f8fafc;margin:0;padding:20px;}
    .container{max-width:1100px;margin:auto;background:white;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,0.1);overflow:hidden;}
    header{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;padding:35px;text-align:center;}
    h1{margin:0;font-size:34px;}
    .content{padding:35px;}
    .upload-box{border:3px dashed #8b5cf6;padding:35px;border-radius:14px;background:#f6f4ff;text-align:center;}
    input,button{padding:14px;margin:10px 0;font-size:16px;border-radius:10px;width:100%;border:1px solid #ddd;}
    button{background:#6366f1;color:white;border:none;cursor:pointer;font-weight:bold;transition:0.3s;}
    button:hover{background:#4f46e5;}
    .btn-success{background:#10b981;}
    .btn-download{background:#ef4444;}
    .btn-download:hover{background:#dc2626;}
    .functions{background:#f1f5f9;padding:20px;border-radius:12px;max-height:350px;overflow-y:auto;margin:20px 0;}
    .func-item{padding:15px;background:white;border-radius:10px;margin:10px 0;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.05);transition:0.3s;}
    .func-item:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,0.1);}
    pre{background:#1e293b;color:#a5b4fc;padding:25px;border-radius:12px;overflow-x:auto;font-size:14px;}
    .status{padding:15px;border-radius:10px;margin:15px 0;}
    .success{background:#dcfce7;color:#166534;}
    .error{background:#fee2e2;color:#991b1b;}
</style></head>
<body>
<div class="container">
<header><h1>Argparse + Class Wrapper</h1><p>Generates parse_args() + smart class that calls your function</p></header>
<div class="content">

{% if message %}<div class="status success">{{ message }}</div>{% endif %}
{% if error %}<div class="status error">{{ error }}</div>{% endif %}

<form method="post" enctype="multipart/form-data">
    <div class="upload-box">
        <h3>Upload Your Python File</h3>
        <input type="file" name="file" accept=".py" required>
        <button type="submit" name="action" value="upload">Upload & Save Permanently</button>
    </div>
</form>

{% if functions %}
<h3>Select Function to Wrap:</h3>
<div class="functions">
{% for f in functions %}
<div class="func-item" onclick="document.getElementById('method').value='{{ f.name }}'">
    <strong>{{ f.name }}()</strong><br>
    <small>{{ f.args|join(', ') or 'no parameters' }}</small>
</div>
{% endfor %}
</div>

<form method="post">
    <input type="text" id="method" name="method" placeholder="Function name" value="{{ selected|default('') }}" required>
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
<h3>{% if is_help %}--help Output{% else %}Generated Wrapper Script{% endif %}</h3>
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
                return render_template_string(HTML, error="Please upload a .py file", functions=functions)
            file.save(PERSISTENT_FILE)
            return render_template_string(HTML, message="File saved permanently!", functions=functions, file_exists=True)

        method_name = request.form.get("method")
        if not method_name or not file_exists:
            return render_template_string(HTML, error="Missing function or file", functions=functions)

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
            return send_file(buffer, as_attachment=True, download_name=f"wrapper_{method_name}.py", mimetype="text/x-python")

        if action == "help":
            result = subprocess.run([sys.executable, "-c", code, "--help"], capture_output=True, text=True)
            return render_template_string(HTML, result=result.stdout or result.stderr, is_help=True, functions=functions, selected=method_name)

        return render_template_string(HTML, result=code, functions=functions, selected=method_name, file_exists=True)

    return render_template_string(HTML, functions=functions, file_exists=file_exists)

if __name__ == "__main__":
    print("Smart Argparse + Class Wrapper Generator Running!")
    print("http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)