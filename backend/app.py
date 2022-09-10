from flask import Flask, request, jsonify
from api.papers import get_paper, get_cord_paper
from api.retrieval import search as _search
from api.similar import similar_by_cord, similar_by_doi
from database.database import db_session
from flask_cors import CORS, cross_origin
from time
from os import path
from os import walk
from collections import defaultdict
from scripts.evaluate import Evaluator, evaluate
from model import Predictor
import json

app = Flask(__name__)
CORS(app)
pred = Predictor()
evaluator = Evaluator()

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

@app.route("/cord_papers", methods=['GET','POST'])
def cord_papers():
    if request.method == 'GET':
        return jsonify({'response': 'ok'})
    if request.method == 'POST':
        data = request.get_json()
        response = get_cord_paper(data['doi'])
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
            with open('api/local_data/fixed_papers.json') as f:
                old_fixed_papers = json.load(f)
            fixed_papers = old_fixed_papers + fixed_papers
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

@app.route("/effectValues", methods=['GET', 'POST'])
def effect_values():
    if request.method == 'GET':
        if path.isfile('api/local_data/effect_values.json'):
            with open('api/local_data/effect_values.json') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])
    if request.method == 'POST':
        effect = request.get_json()['effect']
        effect_list = []
        if path.isfile('api/local_data/effect_values.json'):
            with open('api/local_data/effect_values.json') as f:
                effect_list = json.load(f)
            effect_list.append(effect)
            with open('api/local_data/effect_values.json', 'w') as f:
                json.dump(effect_list, f)
        return jsonify(effect_list)
@app.route("/search", methods=['POST'])
def search():
    session = db_session() # New session instance
    query = request.get_json()['query']
    print(query)
    results = _search(query)
    return jsonify(results)

@app.route("/similar", methods=['POST'])
def similar():
    session = db_session # New session instance
    by = request.get_json()['by']
    by = by.lower()
    id = request.get_json()['id']
    if by == 'cord':
        results = similar_by_cord(id)
    if by == 'doi':
        results = similar_by_doi(id)
    return jsonify(results)


@app.route("/test_dois", methods=['GET'])
def get_test_dois():
    if request.method == 'GET':
        if path.isfile('api/local_data/test_set_dois.json'):
            with open('api/local_data/test_set_dois.json') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])


############# Prediction Model Part ################################


@app.route('/predict_and_saliency', methods=['POST'])
def PredictAndSaliency():
    data = request.get_json()
    output_attributes = data['output_attributes']
    outputs = pred.predict_and_saliency(
        data['input'], output_attributes
    )

    # outputs = [dict(
    #     value=output.strip(),
    #     fixed=False,
    #     confidence=np.round(np.float64(confidences[i]), 2)
    #     ) for i, output in enumerate(output_list)]

    response = {
        'outputs': outputs,
    }
    return jsonify(response)

@app.route('/generate_table', methods=['POST'])
def generateTable():
    data = request.get_json()
    inputs = data['inputs']
    attributes = data['output_attributes']
    outputs = pred.generateTable(inputs, attributes)
    return jsonify(outputs)

@app.route('/save_and_train', methods=['POST'])
def SaveAndTrain():
    data = request.get_json()
    input_text = data['input_text']
    outputs = data['outputs']
    if len(outputs) == 0:
        training_list = ['mutation_name_list: ' + '<EOS>']
    else:
        output_list = []
        field_list = []
        mutation_name_list = []
        effect_dict = defaultdict(list)
        for instance in outputs:
            # print(instance)
            mutation_name_list.append(instance['mutation_name']['value'])
            effect_dict[instance['mutation_name']['value']].append(instance['effect']['value'])
            output_instance = ''
            for attribute in instance.keys():
                if instance[attribute]['attribute'] != 'mutation_type':
                    output_instance += str(instance[attribute]['attribute']) + ':' ' ' + instance[attribute]['value'] + ' | '
            output_list.append(output_instance[:-6] + '<EOS>')


        effect_list = []
        for mutation_name in effect_dict.keys():
            effect_string = 'mutation_name: ' + mutation_name + ' | ' + 'effect_list: '
            for effect in effect_dict[mutation_name]:
                effect_string += effect + ','
            effect_list.append(effect_string[:-1] + '<EOS>')

        mutation_name_list = ','.join(list(set(mutation_name_list)))
        mutation_name_list = ['mutation_name_list: ' + mutation_name_list + '<EOS>']
        # print(mutation_name_list)
        # print(output_list)
        # print(effect_list)
        training_list = mutation_name_list + effect_list + output_list 

    pred.onlineLearning(input_text, training_list)
    return 'online_training_finished'

@app.route('/get_status_evaluator', methods=['GET'])
def get_generate_status_evaluator():
    time.sleep(2)
    return jsonify(evaluator.status)

@app.route('/get_status_train', methods=['GET'])
def get_status_train():
    time.sleep(2)
    return jsonify(pred.status_train)

@app.route('/get_status_prediction', methods=['GET'])
def get_status_prediction():
    time.sleep(0.5)
    return jsonify(pred.status_prediction)

@app.route('/evaluate', methods=['POST'])
def evaluate_model():
    data = request.get_json()
    checkpoint_name = data['checkpoint_name']
    # evaluator = Evaluator()
    evaluator.status = 0
    scores_dicts = evaluator.evaluate(
        checkpoint_name_input=checkpoint_name,
    )
    # del evaluator
    # evaluate2(prova=checkpoint_name)
    return jsonify(scores_dicts)

@app.route('/checkpoint_list', methods=['GET'])
def checkpoint_list():
    checkpoints_path = 'api/Checkpoints/'
    test_resuls_path = 'api/test_results/'
    filenames_checkpoint_folder = next(walk(checkpoints_path), (None, None, []))[2]
    filenames_test_results_folder = next(walk(test_resuls_path), (None, None, []))[2]
    filenames_ckpt = [filename for filename in filenames_checkpoint_folder if 'ckpt' in filename[-4:]]
    new_checkpoints = [
        filename for filename in filenames_ckpt if filename[:-5] + '.tsv' not in filenames_test_results_folder
    ]
    history_checkpoints = [
        filename for filename in filenames_ckpt if filename[:-5] + '.tsv' in filenames_test_results_folder
    ]
    return jsonify({ 'new_checkpoints': new_checkpoints, 'history_checkpoints': history_checkpoints})
