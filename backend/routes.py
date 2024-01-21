from flask import Flask, jsonify, request,render_template
from collections import deque
from dotenv import load_dotenv
import os
#from requests import HTTPError
#from flask_cors import CORS, cross_origin
#from flask_session import Session

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
#TODO make this into well-formed efficiently designed data structure
appointment_queues = \
    dict(zip(range(0,10),([] for _ in range(0,10))))
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


if __name__ == '__main__':
    app.run(debug=True, load_dotenv=True)
