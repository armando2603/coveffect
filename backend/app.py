from flask import Flask, request, jsonify
from api.papers import get_paper
from flask_cors import CORS, cross_origin
from time import time
import json

app = Flask(__name__)
CORS(app)

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
        return

@app.route("/search", methods=['GET'])
def search():
    if request.method == 'GET':
        results = {}
        return json.dump(results)