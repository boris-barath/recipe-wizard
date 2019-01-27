import copy

import spacy
import random
from flask import Flask, flash, request, redirect, render_template, jsonify, session
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

import requests
import requests_cache
from bs4 import BeautifulSoup

import os

from ..back.receipt_detection import detect_ingredients
from ..crawl.extractor import get_data, return_question

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

max_returned_recipes = 5

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/'
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

recipes, reverse_mapping = get_data('../crawl/recipes.json')
nlp = spacy.load('../model/')

requests_cache.install_cache('req_cache')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_photo(photo_id):
    page = requests.get("https://www.allrecipes.com/recipe/{}/".format(photo_id))
    soup = BeautifulSoup(page.content, 'html.parser')
    tag = soup.find(id="BI_openPhotoModal1")

    if not tag:
        tag = soup.find("img", {"class": "rec-photo"})

    return tag.attrs.get('src')


@app.before_request
def before():
    if session.get('state', None) is None:
        session['state'] = {'recipes': copy.deepcopy(recipes), 'reverse_mapping': copy.deepcopy(reverse_mapping),
                            'available': [], 'not_available': [], 'fixed': [],
                            'available_recipes': []}
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
    rec_id = int(request.args.get('id'))
    rec = list(filter(lambda r: r.id == rec_id, recipes))[0]
    other = {'name': rec.name, 'ingredients': rec.ingredients, 'directions': rec.directions, 'calories': rec.calories,
             'url': get_photo(rec_id), 'id': rec_id}
    return jsonify(other)


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
        session.get('state')['fixed'] = filtered
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

    # keep a list of all available recipes
    available_recipes = state['available_recipes']
    question = return_question(state['reverse_mapping'], state['recipes'],
                               state['available'], state['not_available'])

    available_recipes.extend(question['recipes'])

    # if len(available_recipes) == 0:
    #     question['recipes'] = []
    # else:
    #     max_views = max([recipe.views for recipe in available_recipes])

    #     sum_views = sum([max_views - recipe.views + 1 for recipe in available_recipes])

    #     # get a random samble of all available recipes, faboring ones that have least number
    #     # of views
    #     question['recipes'] = np.random.choice(available_recipes,
    #             min(len(available_recipes), max_returned_recipes),
    #             p = list(map(lambda recipe: (max_views - recipe.views + 1) / sum_views, available_recipes)),
    #             replace = False)

    # # increase view count on all suggested recipes
    # for recipe in question['recipes']:
    #     recipe.views += 1

    available_recipes.sort(key=lambda recipe: recipe.difficulty)
    question['recipes'] = available_recipes[:max_returned_recipes]

    question['recipes'] = list(map(lambda recipe: {'value': recipe.id, 'name': recipe.name}, question['recipes']))

    print(question)
    print(session.get('state')['available'])

    session['previous_question'] = question['question']
    session.modified = True

    return jsonify(question)


@app.route('/shuffle', methods=['GET'])
@cross_origin()
def shuffle_recipes():
    state = session.get('state')
    # keep a list of all available recipes
    available_recipes = state['available_recipes']
    available_recipes = random.sample(available_recipes,
                                      k=min(len(available_recipes), max_returned_recipes))
    available_recipes = list(map(lambda recipe: {'value': recipe.id, 'name': recipe.name},
                                 available_recipes))

    return jsonify({'recipes': available_recipes})


@app.route('/recipe/<id>', methods=['GET'])
@cross_origin()
def recipe(id):
    return render_template('recipe.html')


@app.route('/remove', methods=['GET'])
def remove():
    elem = request.args.get('elem')
    session['state']['recipes'] = copy.deepcopy(recipes)
    session['state']['reverse_mapping'] = copy.deepcopy(reverse_mapping)
    session['state']['not_available'].append(elem)
    session['state']['available'] = list(filter(lambda x: x != elem, session['state']['available']))
    return ''


@app.route('/reset', methods=['GET'])
@cross_origin()
def reset():
    if len(session.get('state')['available']) == len(session.get('state')['fixed']) and len(
            session.get('state')['not_available']) == 0:
        print('return')
        return ''

    state = session.pop('state', {'fixed': []})
    before()
    session.get('state')['fixed'] = state['fixed']
    session.get('state')['available'] = state['fixed'][:]
    session.modified = True
    return ''
