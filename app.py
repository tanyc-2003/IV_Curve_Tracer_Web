from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

import webbrowser
import gunicorn
import os
import json
from datetime import datetime
import csv
import io

import firebase_admin
from firebase_admin import credentials, storage, firestore

import openai
from dotenv import load_dotenv



# Open the browser automatically (local)
# url = "http://127.0.0.1:5000"
# webbrowser.open(url)

#Server configurations
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = "Uploads"
CORS(app)

#crendential
load_dotenv()
cendential_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize Firebase Admin SDK
cred = credentials.Certificate(cendential_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': "iv-curve-tracer-web.appspot.com"
})

db = firestore.client()
bucket = storage.bucket()


# Variables
current_selection = ''


# App routes 
@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/dataPacketAvailable', methods=["GET", "POST"])
def dataPacketAvailable():
    
    dataPacket = request.get_json()
    print(dataPacket)

    global bucket
    timeStamp = dateTime()
    temp_csv_filename = 'temp_csv_file.csv'
    csv_filename = timeStamp + '.csv'

    # write to csv file -> convert from dictionary
    with open(temp_csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for key, value in dataPacket.items():
            writer.writerow([key, value])

    print("csv created")

    # upload to firebase storage
    blob = bucket.blob(csv_filename)
    blob.upload_from_filename(temp_csv_filename)

    print("csv uploaded to firebase storage")

    return 'Succeed'


@app.route('/getDataPacket/<csv_filename>', methods=["GET", "POST"])
def getDataPacket(csv_filename):
    global bucket
    global current_selection
    current_selection = csv_filename

    # get csv from firebase storage
    blob = bucket.blob(csv_filename)
    csv_content = blob.download_as_string()

    # read csv file - convert to dictionary
    dataPacket = {}
    csv_file = io.StringIO(csv_content.decode('utf-8'))
    reader = csv.reader(csv_file)
    for row in reader:
        key = float(row[0])
        value = float(row[1])
        dataPacket[key] = value

    return jsonify(dataPacket)


@app.route('/downloadCSV', methods=["GET", "POST"])
def downloadCSV():
    global bucket
    global current_selection
    csv_filename = current_selection
    local_filename = 'downloaded_' + csv_filename

    # get csv from firebase storage
    blob = bucket.blob(csv_filename)
    blob.download_to_filename(local_filename)

    # Serve the file to the client
    return send_file(local_filename, as_attachment=True)


@app.route('/list_files', methods=['GET'])
def list_files():
    global bucket
    blobs = bucket.list_blobs()
    
    filenames = [blob.name for blob in blobs]
    # print(filenames)
    
    return jsonify(filenames)


# Generate data and time 
def dateTime():
    # Get current date and time
    current_datetime = datetime.utcnow()
    # Format the date and time
    formatted_datetime = current_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    return formatted_datetime




if __name__ == "__main__":
    # appFlask.run(ssl_context='adhoc')
    app.run(ssl_context='adhoc')
    # port = os.environ.get("PORT", 5000)# Get port number of env at runtime, else use default port 5000
    # app.run(debug=True, host='0.0.0.0', port=port)  # 0.0.0.0 port forwarding resolves the host IP address at runtime
