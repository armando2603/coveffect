from flask import Flask, request, jsonify
from api.papers import get_paper
from api.retrieval import search as _search
from api.similar import similar_by_cord, similar_by_doi
from database.database import db_session
from flask_cors import CORS, cross_origin
from time import time
from os import path
import json

app = Flask(__name__)
CORS(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/papers", methods=['GET', 'POST'])
def papers():
    if request.method == 'GET':
        return jsonify({'response': 'ok'})
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

@app.route("/saveFeedbacks", methods=['POST'])
def saveFeedbacks():
    feedbacks = request.get_json()['feedback_list']
    if path.isfile('api/local_data/feedbacks.json'):
        with open('api/local_data/feedbacks.json') as f:
            old_feedbacks = json.load(f)
        feedbacks = old_feedbacks + feedbacks
        with open('api/local_data/feedbacks.json', 'w') as f:
            json.dump(feedbacks, f) 
    else:
        with open('api/local_data/feedbacks.json', 'w') as f:
            json.dump(feedbacks, f) 
    return jsonify({'msg': 'error'})

@app.route("/fixedPapers", methods=['POST', 'GET'])
def fixedPapers():
    if request.method == 'POST':
        fixed_papers = request.get_json()['fixed_papers']
        if path.isfile('api/local_data/fixed_papers.json'):
            # with open('api/local_data/fixed_papers.json') as f:
            #     old_fixed_papers = json.load(f)
            # fixed_papers = old_fixed_papers + fixed_papers
            with open('api/local_data/fixed_papers.json', 'w') as f:
                json.dump(fixed_papers, f) 
        else:
            with open('api/local_data/fixed_papers.json', 'w') as f:
                json.dump(fixed_papers, f) 
        return jsonify({'msg': 'error'})
    if request.method == 'GET':
        if path.isfile('api/local_data/fixed_papers.json'):
            with open('api/local_data/fixed_papers.json') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])

@app.route("/mutationValues", methods=['GET'])
def mutation_values():
    if request.method == 'GET':
        if path.isfile('api/local_data/mutation_values.json'):
            with open('api/local_data/mutation_values.json') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])

@app.route("/search", methods=['POST'])
def search():
    query = request.get_json()['query']
    print(query)
    results = _search(query)
    return jsonify(results)

@app.route("/similar", methods=['POST'])
def similar():
    by = request.get_json()['by']
    by = by.lower()
    id = request.get_json()['id']
    if by == 'cord':
        results = similar_by_cord(id)
    if by == 'doi':
        results = similar_by_doi(id)
    return jsonify(results)
