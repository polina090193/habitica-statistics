from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import habitica_statistics
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
file = open("secret_key.txt", "r")
app.secret_key = file.read()

@app.route('/get-statistics', methods=['POST'])
def get_statistics():
  if 'habitica-tasks-history' not in request.files:
    return jsonify({'error': 'File not found'}), 400

  start_date = request.form.get('start-date')
  end_date = request.form.get('end-date')

  if (not start_date or start_date == ''):
    start_date = datetime(1, 1, 1).strftime('%d.%m.%Y')

  if (not end_date or end_date == ''):
    end_date = datetime.now().strftime('%d.%m.%Y')

  uploaded_file = request.files['habitica-tasks-history']

  # Check if uploaded file exists and is CSV
  if uploaded_file.filename == '' or not uploaded_file.filename.endswith('.csv'):
    return jsonify({'error': 'The file must be a CSV file'}), 400

  str_file_value = uploaded_file.read().decode('utf-8')
  file_to_process = str_file_value.splitlines()
  
  reader = list(csv.DictReader(file_to_process))

  ids_seen = set()

  for row in reader:
    task_id = row['Task ID']
    if task_id not in ids_seen:
      ids_seen.add(task_id)

  response = {
    'statistics': habitica_statistics.calculate_statistics(
      reader,
      datetime.strptime(start_date, '%d.%m.%Y'),
      datetime.strptime(end_date, '%d.%m.%Y'),
      ids_seen
    )
  }

  return response, 200, {'Access-Control-Allow-Origin': 'http://localhost:8080'}
