import csv

from flask import Flask, jsonify, request,render_template
from collections import deque
from dotenv import load_dotenv
import os
#from requests import HTTPError
#from flask_cors import CORS, cross_origin
#from flask_session import Session

from csv_parsing import *

WDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(WDIR + os.sep + '.flaskenv')
print(__name__)
app = Flask(__name__)
#from forms import authorized, login_required

# with app.app_context():
#     from config import AppSessionConfig
# app.config.from_object(AppSessionConfig)
# Session(app)
#
# cors = CORS(

appointment_queues = main()
print(appointment_queues)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/api/get_queues', methods=['GET'])
def get_queues():
    return jsonify(appointment_queues)

@app.route('/api/update_queue/<bay>', methods=['POST'])
def update_queue(bay):
    if int(bay) in appointment_queues:
        data = request.get_json()
        appointment_queues[bay] = data['queue']
        return jsonify(success=True, message=f'Queue for bay#{bay} updated successfully.')
    else:
        return jsonify(success=False, message=f'Invalid bay: bay#{bay}')

@app.route('/api/schedule_appointment', methods=['POST'])
def schedule_appointment():
    data = request.get_json()
    print(f"TODO: do add schedule appointment (request data: {data})")
    return jsonify(success=True, message='Appointment scheduled successfully.')

@app.route('/api/get_appointments', methods=['GET'])
def get_appointments():
    csv_file_path = 'datafile.csv'

    appointments_list = []
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            row_string = ', '.join(row)
            appointments_list.append(row_string)

    return jsonify(appointments_list)


if __name__ == '__main__':
    app.run(debug=True, load_dotenv=True)
