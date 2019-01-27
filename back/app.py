import copy

import pickle

import spacy
from flask import Flask, flash, request, redirect, render_template, jsonify, session
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

import requests
from bs4 import BeautifulSoup

import os

from ..back.receipt_detection import detect_ingredients
from ..crawl.extractor import get_data, return_question

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/'
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

recipes, reverse_mapping = get_data('../crawl/recipes.json')
nlp = spacy.load('../model/')


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_photo(photo_id):
    page = requests.get("https://www.allrecipes.com/recipe/{}/".format(photo_id))
    soup = BeautifulSoup(page.content, 'html.parser')
    tag = soup.find(id="BI_openPhotoModal1")
    return tag.attrs.get('src')


@app.before_request
def before():
    if session.get('state', None) is None:
        session['state'] = {'recipes': copy.deepcopy(recipes), 'reverse_mapping': copy.deepcopy(reverse_mapping),
                            'available': [], 'not_available': []}
        session.modified = True


# static page for initial page
@app.route('/')
def home():
    return render_template('index.html')


# page containing questions and final results
@app.route('/questions')
def questions():
    return render_template('questions.html')


@app.route('/detail')
def detail():
    rec_id = request.args.get('id')
    return render_template('detail.html', photo_src=get_photo(rec_id))


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
        detected = detect_ingredients("static/uploaded-file.jpg")

        filtered = []
        for i in range(len(detected)):
            doc = nlp(detected[i])

            if len(doc.ents) >= 1:
                filtered.append(doc.ents[0].text)

        session.get('state')['available'].extend(filtered)
        session.modified = True

        print(filtered)
        flash(filtered)
        return redirect('/questions')
    return 'unknown error'


# post here to get a question or a results page if no questions are left.
# pass the answer (yes/no/dont know) to the prev quesiton here. if no answer, its the first question
@app.route('/question', methods=['GET'])
@cross_origin()
def question():
    question_response = request.args.get('response', 'N/A')

    if question_response == 'yes':
        session['state']['available'].append(session['previous_question'])
    elif question_response == 'no':
        session['state']['not_available'].append(session['previous_question'])

    state = session.get('state')
    question = return_question(state['reverse_mapping'], state['recipes'],
                               state['available'], state['not_available'])
    question['recipes'] = list(map(lambda recipe: {'value': recipe.id, 'name': recipe.name}, question['recipes']))

    print(question)

    session['previous_question'] = question['question']
    session.modified = True

    return jsonify(question)


@app.route('/recipe', methods=['GET'])
@cross_origin()
def recipe():
    return render_template('recipe.html')


@app.route('/reset', methods=['GET'])
@cross_origin()
def reset():
    session.pop('state')
    return ''
