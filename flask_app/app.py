from flask import Flask, render_template, request, redirect, url_for, jsonify
from forms import GenericModelForm
import requests
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

current_directory = os.path.dirname(os.path.abspath(__file__))
models_json_path = os.path.join(current_directory, '..', 'models', 'models.json')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        model_id = request.form.get('model_id')
        return redirect(url_for('specific_model_form', model_id=model_id))

    with open(models_json_path) as f:
        models_info = json.load(f)
    return render_template('index.html', models=models_info["models"])

@app.route('/model/<model_id>', methods=['GET', 'POST'])
def specific_model_form(model_id):
    model_config_path = os.path.join(current_directory, '..', 'models', f'model_{model_id}', 'config.json')
    with open(model_config_path) as f:
        config = json.load(f)

    FormClass = GenericModelForm.create_form(config['form_fields'])
    form = FormClass()

    if form.validate_on_submit():
        data = form.data
        response = requests.post(f'http://localhost:8000/process/{model_id}', json=data)
        result_data = response.json()
        result = {key: result_data.get(key) for key in config["output_locations"].keys()}
        return render_template('result.html', result=result)
    return render_template('dynamic_form.html', form=form, model_id=model_id)

@app.route('/lookup_data/<model_id>/<field_name>', methods=['POST'])
def lookup_data(model_id, field_name):
    depends_on = request.json.get('depends_on', {})
    response = requests.post(f'http://localhost:8000/lookup_data/{model_id}/{field_name}', json=depends_on)
    data = response.json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
