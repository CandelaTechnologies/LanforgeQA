# app.py
import ast
import sys
import os
import tempfile
import subprocess
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# ------------------- Parsing Helpers -------------------
def parse_docstring(docstring):
    if not docstring:
        return {}
    helps = {}
    in_args = False
    for line in docstring.split('\n'):
        line = line.strip()
        if line in ("Args:", "Arguments:"):
            in_args = True
            continue
        if in_args and ':' in line and not line.startswith(("Returns:", "Raises:", "Example:")):
            param_part, desc = line.split(':', 1)
            param = param_part.strip().split()[0]
            helps[param] = desc.strip()
        elif in_args and line and not line[0].isspace():
            in_args = False
    return helps

def get_type_action(ann):
    if not ann:
        return "str", None
    a = ann.lower()
    if a == "str":           return "str", None
    if a == "int":           return "int", None
    if a == "float":         return "float", None
    if a == "bool":          return None, "store_true"
    if "list" in a:          return "str", "append"
    return "str", None

class FuncFinder(ast.NodeVisitor):
    def __init__(self, name):
        self.name = name
        self.node = None
    def visit_FunctionDef(self, node):
        if node.name == self.name and self.node is None:
            self.node = node
        self.generic_visit(node)

def build_parser_code(func_node):
    doc = ast.get_docstring(func_node) or ""
    helps = parse_docstring(doc)

    lines = [
        "import argparse",
        "import sys",
        "",
        "parser = argparse.ArgumentParser(description='Auto-generated parser for {}')".format(func_node.name),
        ""
    ]

    default_start = len(func_node.args.args) - len(func_node.args.defaults)

    for i, arg in enumerate(func_node.args.args):
        name = arg.arg
        if name in ("self", "cls"):
            continue

        ann = ast.unparse(arg.annotation) if arg.annotation else None
        typ, action = get_type_action(ann)
        help_text = helps.get(name, "").replace("'", "\\'")

        arg_line = f"parser.add_argument('--{name}', '-{name[0]}'"

        if typ and action != "store_true":
            arg_line += f", type={typ}"
        if action:
            arg_line += f", action='{action}'"

        arg_line += f", help='{help_text}'" if help_text else ", help=''"

        if i >= default_start and func_node.args.defaults:
            default_val = ast.unparse(func_node.args.defaults[i - default_start])
            arg_line += f", default={default_val}"
        else:
            arg_line += ", required=True"

        arg_line += ")"
        lines.append(arg_line)

    lines += [
        "",
        "args = parser.parse_args()",
        "print(args)"
    ]
    return "\n".join(lines)

# ------------------- HTML GUI Template -------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Argparse Generator</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #f7f9fc; }
        h1 { color: #2c3e50; text-align: center; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        input, button, textarea { margin: 10px 0; width: 100%; padding: 12px; font-size: 16px; border-radius: 8px; border: 1px solid #ddd; }
        input[type="file"] { padding: 8px; }
        button { background: #3498db; color: white; cursor: pointer; font-weight: bold; }
        button:hover { background: #2980b9; }
        button#showHelp { background: #27ae60; }
        button#showHelp:hover { background: #219a52; }
        textarea { height: 400px; font-family: 'Courier New', monospace; background: #2c3e50; color: #f1c40f; }
        .buttons { display: flex; gap: 10px; }
        .result { margin-top: 20px; }
        pre { background: #2c3e50; color: #f1c40f; padding: 15px; border-radius: 8px; overflow-x: auto; }
        .footer { text-align: center; margin-top: 50px; color: #7f8c8d; font-size: 14px; }
    </style>
</head>
<body>
    <h1>Argparse Generator from Function</h1>
    <div class="card">
        <form id="uploadForm" method="post" enctype="multipart/form-data">
            <label><strong>1. Upload your Python file (.py)</strong></label>
            <input type="file" name="file" accept=".py" required>

            <label><strong>2. Function / Method name</strong></label>
            <input type="text" name="method" placeholder="e.g. train_model" required>

            <div class="buttons">
                <button type="submit" name="action" value="generate">Generate Parser Code</button>
                <button type="submit" id="showHelp" name="action" value="help">Show --help Output</button>
            </div>
        </form>

        {% if result %}
        <div class="result">
            <h3>
                {% if is_help %}--help Output{% else %}Generated argparse Code{% endif %}
            </h3>
            <pre>{{ result }}</pre>
        </div>
        {% endif %}

        {% if error %}
        <div class="result" style="color: #e74c3c;">
            <h3>Error</h3>
            <pre>{{ error }}</pre>
        </div>
        {% endif %}
    </div>

    <div class="footer">
        Auto-generates argparse from type hints & docstrings • Supports str, int, float, bool, list
    </div>
</body>
</html>
"""

# ------------------- Routes -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_TEMPLATE)

    if "file" not in request.files:
        return render_template_string(HTML_TEMPLATE, error="No file uploaded")

    file = request.files["file"]
    method_name = request.form.get("method", "").strip()
    action = request.form.get("action")

    if not file.filename.endswith(".py"):
        return render_template_string(HTML_TEMPLATE, error="Please upload a .py file")

    if not method_name:
        return render_template_string(HTML_TEMPLATE, error="Function/method name is required")

    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    try:
        file.save(path)
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        finder = FuncFinder(method_name)
        finder.visit(tree)

        if not finder.node:
            return render_template_string(HTML_TEMPLATE, error=f"Function '{method_name}' not found")

        code = build_parser_code(finder.node)

        if action == "help":
            result = subprocess.run(
                [sys.executable, "-c", code, "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout or result.stderr or "No output"
            return render_template_string(HTML_TEMPLATE, result=output, is_help=True)

        return render_template_string(HTML_TEMPLATE, result=code)

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=str(e))
    finally:
        try:
            os.unlink(path)
        except:
            pass

# ------------------- Run -------------------
if __name__ == "__main__":
    print("Argparse Generator GUI is running!")
    print("Open your browser → http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)