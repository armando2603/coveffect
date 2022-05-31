import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import Predictor
import json
import datetime
import time
from os import path
from collections import defaultdict


app = Flask(__name__)
CORS(app)
pred = Predictor()


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
                    output_instance += str(instance[attribute]['attribute']) + ':' ' ' + instance[attribute]['value'] + '<SEPO>'
            output_list.append(output_instance[:-6] + '<EOS>')


        effect_list = []
        for mutation_name in effect_dict.keys():
            effect_string = 'mutation_name: ' + mutation_name + '<SEPO>' + 'effect_list: '
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
    return jsonify(pred.status)


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
