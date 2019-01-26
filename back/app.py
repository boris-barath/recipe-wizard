import uuid

from flask import Flask, flash, request, redirect, url_for, Response, session
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

import os
import random
import string

UPLOAD_FOLDER = '../upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)


def generate_random_string():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# static page for initial page
@app.route('/')
def home():
    content = get_file('static/index.html')
    return Response(content, mimetype="text/html")


# page containing questions and final results
@app.route('/questions')
def questions():
    content = get_file('static/questions.html')
    session['session_id'] = uuid.uuid4()
    return Response(content, mimetype="text/html")


# post request here to upload image
@app.route('/image', methods=['POST'])
def upload_file():
    # if not session.get('username'):
    #     return 'user does not exist'

    # check if the post request has the file part
    if 'file-upload' not in request.files:
        return 'No file part'

    file = request.files['file-upload']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename('uploaded-file.jpg')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/questions')
    return 'unknown error'


# post here to get a question or a results page if no questions are left.
# pass the answer (yes/no/dont know) to the prev quesiton here. if no answer, its the first question
@app.route('/question', methods=['GET'])
@cross_origin()
def question():
    return 'beris'
