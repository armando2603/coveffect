# import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import Predictor
# import json
# import datetime
import time
# from os import path
from os import walk
from collections import defaultdict
from scripts.evaluate import Evaluator, evaluate


app = Flask(__name__)
CORS(app)
pred = Predictor()
evaluator = Evaluator()


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

@app.route('/getGenerateStatus', methods=['GET'])
def getGenerateStatus():
    time.sleep(2)
    return jsonify(evaluator.status)

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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--colab",
        action="store_true",
        help="colab mode"
    )
    args = parser.parse_args()
    if args.colab:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app)
    app.run()
