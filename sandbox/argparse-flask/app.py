import os
import sys
import subprocess
import re
import json
from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'argparse-web-runner-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SAVED_FORMS_FOLDER'] = 'saved_forms'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SAVED_FORMS_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return filename.lower().endswith('.py')


def extract_arguments_from_script(script_path):
    try:
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        arguments = []
        matches = re.findall(r'\.add_argument\(\s*([^)]+)\)', content, re.DOTALL)

        for match in matches:
            arg_info = {
                'dest': None,
                'preferred_flag': None,
                'help': '',
                'default': None,
                'field_type': 'text',
                'is_flag': False
            }

            flags = re.findall(r'["\'](--?[\w-]+)["\']', match)
            if flags:
                flags.sort(key=len, reverse=True)
                arg_info['option_strings'] = flags
                arg_info['preferred_flag'] = flags[0]
                arg_info['dest'] = flags[0].lstrip('-').replace('-', '_')

            help_match = re.search(r'help\s*=\s*["\'](.*?)["\']', match, re.DOTALL)
            if help_match:
                arg_info['help'] = help_match.group(1).strip()

            if re.search(r'action\s*=\s*["\']?store_true["\']?', match):
                arg_info['field_type'] = 'checkbox'
                arg_info['is_flag'] = True

            if 'type=int' in match:
                arg_info['field_type'] = 'number'

            if arg_info['dest']:
                arguments.append(arg_info)

        seen = set()
        unique = []
        for arg in arguments:
            if arg['dest'] not in seen:
                seen.add(arg['dest'])
                unique.append(arg)
        return unique
    except:
        return []


def get_saved_forms():
    forms = []
    folder = app.config['SAVED_FORMS_FOLDER']
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.json'):
                forms.append(f)
    return sorted(forms)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.args.get('new_script'):
        session.clear()

    script_path = session.get('script_path')
    filename = os.path.basename(script_path) if script_path else None
    actions = []
    generated_command = None
    output = None
    saved_form = session.get('form_data', {'selected_params': [], 'values': {}})
    saved_forms_list = get_saved_forms()

    if request.method == 'POST':
        if 'script' in request.files:
            file = request.files['script']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                script_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(script_path)
                session['script_path'] = script_path
                session['form_data'] = {'selected_params': [], 'values': {}}
                actions = extract_arguments_from_script(script_path)

        elif 'action_type' in request.form and session.get('script_path'):
            script_path = session.get('script_path')
            actions = extract_arguments_from_script(script_path)

            # Save current form state in session
            form_values = {
                'selected_params': request.form.getlist('selected_params'),
                'values': {}
            }
            for key in request.form:
                if key not in ['script_path', 'action_type']:
                    form_values['values'][key] = request.form.get(key)
            session['form_data'] = form_values

            # Build command
            selected_params = request.form.getlist('selected_params')  # this is where the Selected Parameters clears
            cmd = [sys.executable, script_path]

            for dest in selected_params:
                value = request.form.get(dest) or ""
                action = next((a for a in actions if a['dest'] == dest), None)
                flag = action['preferred_flag'] if action and action.get('preferred_flag') else f"--{dest.replace('_', '-')}"

                if action and action.get('is_flag'):
                    cmd.append(flag)
                elif value.strip():
                    cmd.extend([flag, value.strip()])

            full_command = ' '.join(cmd)

            if request.form.get('action_type') == 'generate':
                generated_command = full_command
            elif request.form.get('action_type') == 'run':
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                    output = {
                        'command': full_command,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    }
                except Exception as e:
                    output = {'command': full_command, 'stdout': '', 'stderr': str(e), 'returncode': -1}

    saved_form = session.get('form_data', {'selected_params': [], 'values': {}})
    saved_forms_list = get_saved_forms()

    return render_template('index.html',
                         script_path=script_path,
                         filename=filename,
                         actions=actions,
                         generated_command=generated_command,
                         output=output,
                         saved_form=saved_form,
                         saved_forms_list=saved_forms_list)


if __name__ == '__main__':
    print("Flask app running at http://127.0.0.1:5000")
    app.run(debug=True)