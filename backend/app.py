from flask import Flask, request, jsonify
from api.papers import get_paper
from api.retrieval import search as _search
from api.similar import similar_by_cord
from api.similar import similar_by_cord_euclidean
from database.database import db_session
from flask_cors import CORS, cross_origin
from time import time
import json

app = Flask(__name__)
CORS(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/papers", methods=['GET', 'POST'])
def papers():
    if request.method == 'GET':
        return jsonify({'reposonse': 'ok'})
    if request.method == 'POST':
        data = request.get_json()
        response = get_paper(data['doi'])
        return jsonify(response)

@app.route("/paperlist", methods=['GET', 'POST'])
def paperlist():
    if request.method == 'GET':
        with open('api/local_data/paper_list.json', 'r') as file:
            paper_list = json.load(file)
        return jsonify({'paper_list': paper_list})
    if request.method == 'POST':
        paper_list = request.get_json()['paper_list']
        with open('api/local_data/paper_list.json', 'w') as file:
            json.dump(paper_list, file)
        return jsonify({'msg': 'The list has been saved'})

@app.route("/search", methods=['GET'])
def search():
    if request.method == 'GET':
        query = request.args.get('query')
        results = _search(query)
        return jsonify(results)

@app.route("/similar", methods=['GET'])
def similar():
    if request.method == 'GET':
        by = request.args.get('by')
        id = request.args.get('id')
        results = similar_by_cord(id)
        return jsonify(results)

@app.route("/similar_eu", methods=['GET'])
def similar_euclidean():
    if request.method == 'GET':
        by = request.args.get('by')
        id = request.args.get('id')
        results = similar_by_cord_euclidean(id)
        return jsonify(results)